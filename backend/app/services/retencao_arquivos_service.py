"""
Service de retenção de arquivos.

Responsabilidades:
  - Buscar a política ativa de uma empresa (ou criar padrão)
  - Calcular campos de retenção no upload
  - Limpar arquivos expirados do bucket
"""
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.arquivo_enviado import ArquivoEnviado
from app.models.log_retencao_arquivo import LogRetencaoArquivo
from app.models.politica_retencao_arquivo import PoliticaRetencaoArquivo

BUCKET = "arquivos-originais"


def buscar_politica_ativa(empresa_id: Any, db: Session) -> PoliticaRetencaoArquivo:
    """Retorna a política ativa da empresa. Se não existir, cria uma padrão."""
    politica = db.query(PoliticaRetencaoArquivo).filter(
        PoliticaRetencaoArquivo.empresa_id == empresa_id,
        PoliticaRetencaoArquivo.ativo == True,  # noqa: E712
    ).first()

    if politica is None:
        politica = PoliticaRetencaoArquivo(
            empresa_id=empresa_id,
            modo_retencao="temporario",
            salvar_arquivo_original=True,
            salvar_resultado_processado=True,
            salvar_linhas_processadas=False,
            salvar_metadados=True,
            tempo_retencao_horas=168,
            excluir_arquivo_original_apos_processamento=False,
            permitir_download_original=True,
            permitir_reprocessamento_sem_reenvio=True,
            ativo=True,
        )
        db.add(politica)
        db.flush()

    return politica


def calcular_hash(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def calcular_campos_retencao(
    politica: PoliticaRetencaoArquivo,
    conteudo: bytes,
    nome_original: str,
    content_type: str,
) -> dict:
    """Retorna dict com campos de retenção a gravar em arquivos_enviados."""
    agora = datetime.now(timezone.utc)
    modo = politica.modo_retencao

    hash_arquivo = calcular_hash(conteudo)

    metadados: dict[str, Any] = {
        "nome_original": nome_original,
        "content_type": content_type,
        "tamanho_bytes": len(conteudo),
    }

    if modo == "temporario":
        expira_em = agora + timedelta(hours=politica.tempo_retencao_horas or 168)
        return {
            "modo_retencao": "temporario",
            "arquivo_persistido": True,
            "expira_em": expira_em,
            "excluido_em": None,
            "hash_arquivo": hash_arquivo,
            "metadados": metadados,
        }

    if modo == "persistente":
        return {
            "modo_retencao": "persistente",
            "arquivo_persistido": True,
            "expira_em": None,
            "excluido_em": None,
            "hash_arquivo": hash_arquivo,
            "metadados": metadados,
        }

    # somente_memoria — não chegará aqui no upload (bloqueado antes), mas incluso por completude
    return {
        "modo_retencao": "somente_memoria",
        "arquivo_persistido": False,
        "expira_em": None,
        "excluido_em": agora,
        "hash_arquivo": hash_arquivo,
        "metadados": metadados,
    }


def arquivo_disponivel(arquivo: ArquivoEnviado) -> bool:
    """Retorna True se o arquivo ainda pode ser acessado."""
    if not arquivo.arquivo_persistido:
        return False
    if arquivo.excluido_em is not None:
        return False
    return True


def _remover_do_bucket(caminho: str) -> None:
    url = f"{settings.SUPABASE_URL}/storage/v1/object/{BUCKET}/{caminho}"
    headers = {"Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"}
    httpx.delete(url, headers=headers, timeout=15)


def limpar_arquivos_expirados(db: Session) -> dict:
    """
    Busca arquivos com expira_em < now(), persistidos e não excluídos.
    Remove do bucket e atualiza o registro.
    Retorna resumo da operação.
    """
    agora = datetime.now(timezone.utc)

    arquivos = db.query(ArquivoEnviado).filter(
        ArquivoEnviado.expira_em < agora,
        ArquivoEnviado.arquivo_persistido == True,  # noqa: E712
        ArquivoEnviado.excluido_em == None,  # noqa: E711
    ).all()

    excluidos = 0
    falhas = 0

    for arquivo in arquivos:
        try:
            _remover_do_bucket(arquivo.caminho_storage)

            arquivo.arquivo_persistido = False
            arquivo.excluido_em = agora

            log = LogRetencaoArquivo(
                empresa_id=arquivo.empresa_id,
                arquivo_id=arquivo.id,
                evento="arquivo_excluido_por_retencao",
                mensagem=f"Arquivo '{arquivo.nome_original}' excluído por expiração de retenção.",
                detalhes={
                    "nome_original": arquivo.nome_original,
                    "expira_em": arquivo.expira_em.isoformat() if arquivo.expira_em else None,
                    "excluido_em": agora.isoformat(),
                },
            )
            db.add(log)
            excluidos += 1

        except Exception as exc:
            falhas += 1
            log = LogRetencaoArquivo(
                empresa_id=arquivo.empresa_id,
                arquivo_id=arquivo.id,
                evento="falha_ao_excluir_arquivo",
                mensagem=f"Falha ao excluir arquivo '{arquivo.nome_original}': {exc}",
                detalhes={"nome_original": arquivo.nome_original, "erro": str(exc)},
            )
            db.add(log)

    db.commit()
    return {
        "total_candidatos": len(arquivos),
        "excluidos": excluidos,
        "falhas": falhas,
        "executado_em": agora.isoformat(),
    }
