"""
Teste de aceite da Sprint 5.5 — Política de retenção de arquivos.

Testa a camada de serviço diretamente com dados reais do banco (schema dev).
Não requer token JWT — acessa o banco via SQLAlchemy com service key.

Uso:
  cd backend
  DB_SCHEMA=ia16_fechamento_dev python -m scripts.teste_aceite_sprint55

Critérios de aceite:
  [1] Política da Daxx retornada corretamente (modo_retencao=temporario, 168h)
  [2] calcular_campos_retencao preenche modo_retencao, arquivo_persistido, expira_em, hash_arquivo
  [3] expira_em = criado_em + 168 horas (dentro de margem de 60s)
  [4] hash_arquivo é SHA-256 hex de 64 caracteres
  [5] Upload real insere registro com todos os campos de retenção corretos
  [6] Listagem retorna arquivo_disponivel=True para arquivo recém-enviado
  [7] Registro expirado é identificado pela query de limpeza
  [8] Script de limpeza atualiza arquivo_persistido=False e excluido_em
  [9] Log de retenção registrado em logs_retencao_arquivos
"""
import sys
import os
import io
import uuid
import hashlib
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openpyxl
from sqlalchemy import text

from app.core.database import SessionLocal, engine
import app.models.base  # noqa: F401 — carrega todos os models no registry do SQLAlchemy
from app.models.arquivo_enviado import ArquivoEnviado
from app.models.log_retencao_arquivo import LogRetencaoArquivo
from app.services.retencao_arquivos_service import (
    buscar_politica_ativa,
    calcular_campos_retencao,
    calcular_hash,
    arquivo_disponivel,
    limpar_arquivos_expirados,
)
from app.core.config import settings

SCHEMA = settings.DB_SCHEMA
EMPRESA_DAXX_ID = uuid.UUID("8fcde7f9-f37f-4680-8fdf-3288cf2949be")
FECHAMENTO_ID   = uuid.UUID("48626b8e-cfb5-48d1-9774-a2c5607e9d55")
USUARIO_ID      = uuid.UUID("3505ab0b-7548-4e96-b62d-c7452dc8e7ba")  # admin_ia16

OK   = "\033[32m✔\033[0m"
FAIL = "\033[31m✘\033[0m"
INFO = "\033[34mℹ\033[0m"

erros = []


def check(descricao: str, condicao: bool, detalhe: str = "") -> bool:
    if condicao:
        print(f"  {OK}  {descricao}")
    else:
        print(f"  {FAIL}  {descricao}" + (f" — {detalhe}" if detalhe else ""))
        erros.append(descricao)
    return condicao


def criar_xlsx_teste() -> bytes:
    """Cria um arquivo .xlsx mínimo em memória."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Extrato"
    ws.append(["Data", "Descrição", "Valor", "Tipo"])
    ws.append(["2026-06-01", "Pagamento fornecedor", -1500.00, "débito"])
    ws.append(["2026-06-02", "Recebimento cliente", 3200.00, "crédito"])
    ws.append(["2026-06-03", "Taxa bancária", -25.50, "débito"])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def main():
    print(f"\n{'='*60}")
    print(f"  Teste de Aceite — Sprint 5.5 — Schema: {SCHEMA}")
    print(f"{'='*60}\n")

    db = SessionLocal()
    arquivo_teste_id = None

    try:
        # ── BLOCO 1: Política da Daxx ──────────────────────────────────────
        print(f"{INFO} [1/4] Validando política de retenção da Daxx...")
        politica = buscar_politica_ativa(EMPRESA_DAXX_ID, db)
        db.commit()

        check("Política encontrada", politica is not None)
        check("modo_retencao = temporario", politica.modo_retencao == "temporario",
              f"obtido: {politica.modo_retencao}")
        check("tempo_retencao_horas = 168", politica.tempo_retencao_horas == 168,
              f"obtido: {politica.tempo_retencao_horas}")
        check("salvar_arquivo_original = True", politica.salvar_arquivo_original)
        check("permitir_download_original = True", politica.permitir_download_original)
        check("permitir_reprocessamento_sem_reenvio = True", politica.permitir_reprocessamento_sem_reenvio)
        check("ativo = True", politica.ativo)

        # ── BLOCO 2: Cálculo dos campos de retenção ────────────────────────
        print(f"\n{INFO} [2/4] Validando cálculo dos campos de retenção...")
        conteudo = criar_xlsx_teste()
        nome = "extrato_teste_aceite.xlsx"
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        antes = datetime.now(timezone.utc)

        campos = calcular_campos_retencao(politica, conteudo, nome, content_type)

        check("modo_retencao = temporario", campos["modo_retencao"] == "temporario",
              f"obtido: {campos['modo_retencao']}")
        check("arquivo_persistido = True", campos["arquivo_persistido"])
        check("excluido_em = None", campos["excluido_em"] is None,
              f"obtido: {campos['excluido_em']}")
        check("expira_em preenchido", campos["expira_em"] is not None)
        check("hash_arquivo preenchido", bool(campos["hash_arquivo"]))
        check("hash_arquivo tem 64 caracteres (SHA-256)", len(campos["hash_arquivo"]) == 64,
              f"obtido: {len(campos['hash_arquivo'])} chars")

        # Validar cálculo de expiração
        esperado_expira = antes + timedelta(hours=168)
        diff_segundos = abs((campos["expira_em"] - esperado_expira).total_seconds())
        check("expira_em ≈ criado_em + 168h (margem 60s)", diff_segundos < 60,
              f"diferença: {diff_segundos:.1f}s")

        # Validar hash
        hash_esperado = hashlib.sha256(conteudo).hexdigest()
        check("hash_arquivo = SHA-256 correto", campos["hash_arquivo"] == hash_esperado)

        # Validar metadados
        check("metadados.nome_original correto", campos["metadados"]["nome_original"] == nome)
        check("metadados.tamanho_bytes correto", campos["metadados"]["tamanho_bytes"] == len(conteudo))

        # ── BLOCO 3: Upload real no banco ──────────────────────────────────
        print(f"\n{INFO} [3/4] Testando upload real (insert em arquivos_enviados)...")
        nome_armazenado = f"extrato_teste_{uuid.uuid4().hex[:8]}.xlsx"
        caminho = f"{EMPRESA_DAXX_ID}/{FECHAMENTO_ID}/originais/{nome_armazenado}"

        novo = ArquivoEnviado(
            empresa_id=EMPRESA_DAXX_ID,
            fechamento_id=FECHAMENTO_ID,
            criado_por_usuario_id=USUARIO_ID,
            nome_original=nome,
            nome_armazenado=nome_armazenado,
            tipo_arquivo="extrato_bancario",
            caminho_storage=caminho,
            tamanho_bytes=len(conteudo),
            status="enviado",
            atualizado_em=datetime.now(timezone.utc),
            **campos,
        )
        db.add(novo)
        db.commit()
        db.refresh(novo)
        arquivo_teste_id = novo.id

        print(f"     ID do arquivo criado: {arquivo_teste_id}")
        print(f"     expira_em:            {novo.expira_em.isoformat()}")
        print(f"     hash_arquivo:         {novo.hash_arquivo[:20]}...")

        check("Arquivo inserido no banco", True)
        check("modo_retencao gravado corretamente", novo.modo_retencao == "temporario")
        check("arquivo_persistido = True", novo.arquivo_persistido is True)
        check("expira_em gravado", novo.expira_em is not None)
        check("excluido_em = None", novo.excluido_em is None)
        check("hash_arquivo gravado", bool(novo.hash_arquivo))
        check("metadados gravado", isinstance(novo.metadados, dict))

        # Validar arquivo_disponivel via service
        check("arquivo_disponivel() = True", arquivo_disponivel(novo))

        # ── BLOCO 4: Script de limpeza ─────────────────────────────────────
        print(f"\n{INFO} [4/4] Testando script de limpeza com registro controlado...")

        # Forçar expiração do arquivo de teste (ajustar expira_em para o passado)
        db.execute(
            text(f"UPDATE {SCHEMA}.arquivos_enviados SET expira_em = now() - interval '1 hour' WHERE id = :id"),
            {"id": str(arquivo_teste_id)},
        )
        db.commit()

        # Verificar que o arquivo agora está candidato à limpeza
        db.refresh(novo)
        check("expira_em ajustado para o passado", novo.expira_em < datetime.now(timezone.utc))

        # Executar limpeza (sem remover do bucket — o arquivo não foi enviado ao Storage)
        # Para o teste, sobrescrevemos _remover_do_bucket para não falhar
        import app.services.retencao_arquivos_service as svc
        original_remover = svc._remover_do_bucket

        def _remover_mock(caminho: str) -> None:
            print(f"     [mock] Remoção do bucket simulada: {caminho}")

        svc._remover_do_bucket = _remover_mock

        resultado = limpar_arquivos_expirados(db)
        svc._remover_do_bucket = original_remover  # restaurar

        print(f"     Resultado da limpeza: {resultado}")

        check("Candidatos encontrados >= 1", resultado["total_candidatos"] >= 1,
              f"obtido: {resultado['total_candidatos']}")
        check("Excluídos com sucesso >= 1", resultado["excluidos"] >= 1,
              f"obtido: {resultado['excluidos']}")
        check("Sem falhas na limpeza", resultado["falhas"] == 0,
              f"falhas: {resultado['falhas']}")

        # Verificar estado após limpeza
        db.refresh(novo)
        check("arquivo_persistido = False após limpeza", novo.arquivo_persistido is False)
        check("excluido_em preenchido após limpeza", novo.excluido_em is not None)
        check("arquivo_disponivel() = False após limpeza", not arquivo_disponivel(novo))

        # Verificar log de retenção gerado
        log = db.query(LogRetencaoArquivo).filter(
            LogRetencaoArquivo.arquivo_id == arquivo_teste_id
        ).first()
        check("Log de retenção registrado", log is not None)
        check("Evento correto no log", log and log.evento == "arquivo_excluido_por_retencao",
              f"obtido: {log.evento if log else 'N/A'}")

    finally:
        # Limpar registro de teste do banco
        if arquivo_teste_id:
            try:
                db.execute(
                    text(f"DELETE FROM {SCHEMA}.logs_retencao_arquivos WHERE arquivo_id = :id"),
                    {"id": str(arquivo_teste_id)},
                )
                db.execute(
                    text(f"DELETE FROM {SCHEMA}.arquivos_enviados WHERE id = :id"),
                    {"id": str(arquivo_teste_id)},
                )
                db.commit()
                print(f"\n  {INFO}  Registro de teste removido do banco.")
            except Exception as e:
                print(f"\n  {INFO}  Aviso ao limpar: {e}")
        db.close()

    # ── Resultado final ────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    if not erros:
        print(f"  {OK}  TODOS OS CRITÉRIOS DE ACEITE APROVADOS ({9 - len(erros)}/9)")
    else:
        print(f"  {FAIL}  {len(erros)} critério(s) falharam:")
        for e in erros:
            print(f"       • {e}")
    print(f"{'='*60}\n")
    sys.exit(0 if not erros else 1)


if __name__ == "__main__":
    main()
