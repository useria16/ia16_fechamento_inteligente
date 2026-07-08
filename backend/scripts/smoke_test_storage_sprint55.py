"""
Smoke test real do Storage — Sprint 5.5.

Envia os dois arquivos sintéticos de teste para a API real,
usando o Storage do Supabase remoto (schema ia16_fechamento_dev).

Estratégia: injeta usuário real no FastAPI via dependency_overrides,
eliminando necessidade de JWT sem mockar o Storage, banco ou a lógica de negócio.

Uso:
  cd backend
  DB_SCHEMA=ia16_fechamento_dev python -m scripts.smoke_test_storage_sprint55

Critérios de aprovação:
  [1]  Arquivo 1 enviado para Storage sem erro
  [2]  Arquivo 2 enviado para Storage sem erro
  [3]  modo_retencao = temporario nos dois registros
  [4]  arquivo_persistido = true nos dois
  [5]  expira_em preenchido nos dois
  [6]  expira_em ≈ criado_em + 168h (tolerância 5 min)
  [7]  hash_arquivo preenchido (64 chars SHA-256)
  [8]  caminho_storage segue padrão empresa/conciliacao/originais/nome
  [9]  excluido_em = null nos dois
  [10] Arquivos verificados no bucket via API do Storage
"""
import sys
import os
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from starlette.testclient import TestClient

import app.models.base  # noqa: F401 — registra todos os models
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.usuario import Usuario
from app.main import app
from app.core.auth import get_usuario_atual

MASSA_TESTE = Path(__file__).parent.parent.parent / "docs" / "massa-teste"
BUCKET      = "arquivos-originais"
EMPRESA_ID  = "8fcde7f9-f37f-4680-8fdf-3288cf2949be"  # Daxx Omnimedia
CONCILIACAO = "48626b8e-cfb5-48d1-9774-a2c5607e9d55"

OK   = "\033[32m✔\033[0m"
FAIL = "\033[31m✘\033[0m"
INFO = "\033[34mℹ\033[0m"

erros: list[str] = []
ids_criados: list[str] = []


def check(descricao: str, condicao: bool, detalhe: str = "") -> bool:
    if condicao:
        print(f"  {OK}  {descricao}")
    else:
        print(f"  {FAIL}  {descricao}" + (f"\n       {detalhe}" if detalhe else ""))
        erros.append(descricao)
    return condicao


def verificar_arquivo_no_bucket(caminho: str) -> bool:
    url = f"{settings.SUPABASE_URL}/storage/v1/object/info/{BUCKET}/{caminho}"
    headers = {"Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"}
    try:
        resp = httpx.head(url, headers=headers, timeout=10)
        return resp.status_code == 200
    except Exception:
        return False


def remover_arquivo_do_bucket(caminho: str) -> None:
    url = f"{settings.SUPABASE_URL}/storage/v1/object/{BUCKET}/{caminho}"
    headers = {"Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"}
    httpx.delete(url, headers=headers, timeout=10)


def main():
    print(f"\n{'='*60}")
    print(f"  Smoke Test Storage — Sprint 5.5")
    print(f"  Schema:       {settings.DB_SCHEMA}")
    print(f"  Bucket:       {BUCKET}")
    print(f"  Conciliação:  {CONCILIACAO}")
    print(f"{'='*60}\n")

    # ── Carregar usuário cliente_admin da Daxx ─────────────────────────────
    db = SessionLocal()
    usuario = db.query(Usuario).filter(
        Usuario.email == "elieziomesquita@gmail.com"
    ).first()
    if not usuario:
        print(f"  {FAIL}  Usuário de teste não encontrado")
        db.close()
        sys.exit(1)
    print(f"  {INFO}  Usuário: {usuario.email} ({usuario.perfil})")

    # ── Injetar usuário — bypass JWT, Storage real ─────────────────────────
    app.dependency_overrides[get_usuario_atual] = lambda: usuario
    client = TestClient(app, raise_server_exceptions=True)

    arquivos_para_enviar = [
        ("TESTE_Extrato_Lancamentos_banco.xlsx", "extrato_bancario"),
        ("TESTE_Fluxo_Caixa_Daxx.xlsx",          "planilha_interna"),
    ]

    respostas = []

    # ── Enviar cada arquivo ────────────────────────────────────────────────
    for nome_arquivo, tipo in arquivos_para_enviar:
        caminho_local = MASSA_TESTE / nome_arquivo
        if not caminho_local.exists():
            print(f"  {FAIL}  Arquivo não encontrado: {caminho_local}")
            erros.append(f"Arquivo não encontrado: {nome_arquivo}")
            continue

        tamanho_kb = caminho_local.stat().st_size // 1024
        print(f"\n{INFO} Enviando: {nome_arquivo} ({tamanho_kb} KB) — tipo: {tipo}")

        with open(caminho_local, "rb") as f:
            conteudo = f.read()

        antes = datetime.now(timezone.utc)
        response = client.post(
            f"/api/v1/conciliacoes/{CONCILIACAO}/arquivos",
            files={"arquivo": (nome_arquivo, conteudo,
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"tipo_arquivo": tipo},
        )
        depois = datetime.now(timezone.utc)

        check(f"HTTP 201 para {nome_arquivo}", response.status_code == 201,
              f"status={response.status_code} body={response.text[:200]}")

        if response.status_code != 201:
            continue

        body = response.json()
        dados = body.get("dados", {})
        respostas.append((nome_arquivo, tipo, dados, antes, depois))

        arquivo_id = dados.get("id", "")
        ids_criados.append(arquivo_id)

        print(f"       ID: {arquivo_id}")
        print(f"       nome_armazenado: {dados.get('nome_armazenado', 'N/A')[:50]}")

    db.close()

    if not respostas:
        print(f"\n  {FAIL}  Nenhum arquivo enviado com sucesso. Abortando validações.")
        _finalizar()

    print(f"\n{'─'*60}")
    print(f"  Validando campos de retenção nos {len(respostas)} arquivo(s) enviado(s)")
    print(f"{'─'*60}")

    # ── Validar campos de retenção na resposta ─────────────────────────────
    for nome_arquivo, tipo, dados, antes, depois in respostas:
        print(f"\n  [{nome_arquivo}]")

        check("modo_retencao = temporario",
              dados.get("modo_retencao") == "temporario",
              f"obtido: {dados.get('modo_retencao')}")

        check("arquivo_persistido = true",
              dados.get("arquivo_persistido") is True,
              f"obtido: {dados.get('arquivo_persistido')}")

        check("excluido_em = null",
              dados.get("excluido_em") is None,
              f"obtido: {dados.get('excluido_em')}")

        check("arquivo_disponivel = true",
              dados.get("arquivo_disponivel") is True,
              f"obtido: {dados.get('arquivo_disponivel')}")

        check("permitir_download_original = true",
              dados.get("permitir_download_original") is True,
              f"obtido: {dados.get('permitir_download_original')}")

        # Validar expira_em
        expira_em_str = dados.get("expira_em")
        check("expira_em preenchido", bool(expira_em_str), "campo nulo ou ausente")

        if expira_em_str:
            expira_em = datetime.fromisoformat(expira_em_str.replace("Z", "+00:00"))
            esperado   = antes + timedelta(hours=168)
            diff_min   = abs((expira_em - esperado).total_seconds()) / 60
            check("expira_em ≈ criado_em + 168h (margem 5 min)", diff_min < 5,
                  f"diferença: {diff_min:.1f} min | expira_em: {expira_em_str}")
            print(f"       expira_em: {expira_em_str}")

        # Validar hash
        check("hash_arquivo preenchido (64 chars SHA-256)",
              len(dados.get("hash_arquivo") or "") == 64,
              f"obtido: {len(dados.get('hash_arquivo') or '')} chars")

        # Validar caminho_storage
        caminho = dados.get("caminho_storage", "")
        padrao_ok = (EMPRESA_ID in caminho and
                     CONCILIACAO in caminho and
                     "originais" in caminho)
        check("caminho_storage segue padrão empresa/conciliacao/originais",
              padrao_ok, f"caminho: {caminho}")

        # Verificar arquivo no bucket real
        if caminho:
            no_bucket = verificar_arquivo_no_bucket(caminho)
            check("Arquivo salvo no bucket Storage real (sem mock)",
                  no_bucket, f"caminho: {caminho}")
            if no_bucket:
                print(f"       bucket: {BUCKET}/{caminho[:60]}...")

    # ── Validar via banco (MCP não disponível no script, usar SQLAlchemy) ──
    print(f"\n{'─'*60}")
    print(f"  Validando registros no banco (ia16_fechamento_dev)")
    print(f"{'─'*60}")

    db2 = SessionLocal()
    from app.models.arquivo_enviado import ArquivoEnviado
    from sqlalchemy import text

    registros = db2.execute(
        text(f"""
            SELECT nome_original, modo_retencao, arquivo_persistido,
                   expira_em, excluido_em, hash_arquivo,
                   caminho_storage, criado_em
            FROM {settings.DB_SCHEMA}.arquivos_enviados
            WHERE fechamento_id = :fid
              AND criado_em > now() - interval '10 minutes'
            ORDER BY criado_em DESC
        """),
        {"fid": CONCILIACAO},
    ).fetchall()

    check(f"Dois registros criados nos últimos 10 min", len(registros) == 2,
          f"encontrados: {len(registros)}")

    for reg in registros:
        r = dict(reg._mapping)
        print(f"\n  Banco — {r['nome_original']}")
        check("  modo_retencao = temporario", r["modo_retencao"] == "temporario",
              f"obtido: {r['modo_retencao']}")
        check("  arquivo_persistido = true", r["arquivo_persistido"] is True)
        check("  expira_em preenchido", r["expira_em"] is not None)
        check("  excluido_em = null", r["excluido_em"] is None)
        check("  hash_arquivo 64 chars", len(r.get("hash_arquivo") or "") == 64)
        check("  caminho_storage preenchido", bool(r["caminho_storage"]))

        if r["expira_em"] and r["criado_em"]:
            criado  = r["criado_em"].replace(tzinfo=timezone.utc)
            expira  = r["expira_em"].replace(tzinfo=timezone.utc)
            diff_h  = (expira - criado).total_seconds() / 3600
            check(f"  expira_em - criado_em ≈ 168h (obtido: {diff_h:.1f}h)",
                  167.9 <= diff_h <= 168.1)

    db2.close()
    app.dependency_overrides.clear()
    _finalizar()


def _finalizar():
    print(f"\n{'='*60}")
    total = 10
    aprovados = total - len(erros)
    if not erros:
        print(f"  {OK}  SMOKE TEST APROVADO — {aprovados}/{total} critérios")
    else:
        print(f"  {FAIL}  {len(erros)} critério(s) falharam:")
        for e in erros:
            print(f"       • {e}")
    print(f"{'='*60}")
    print(f"\n  IDs criados no banco (para consulta manual):")
    for id_ in ids_criados:
        print(f"    {id_}")
    print()
    sys.exit(0 if not erros else 1)


if __name__ == "__main__":
    main()
