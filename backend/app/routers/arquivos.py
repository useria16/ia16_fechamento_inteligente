import uuid
import re
from datetime import datetime, timezone
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.auth import get_usuario_atual
from app.core.config import settings
from app.core.database import get_db
from app.models.arquivo_enviado import ArquivoEnviado
from app.models.fechamento_financeiro import FechamentoFinanceiro
from app.models.usuario import Usuario
from app.schemas.arquivo import ArquivoResponse
from app.schemas.resposta import RespostaLista, RespostaSucesso
from app.services.retencao_arquivos_service import (
    arquivo_disponivel,
    buscar_politica_ativa,
    calcular_campos_retencao,
)

router = APIRouter(tags=["arquivos"])

BUCKET = "arquivos-originais"
TAMANHO_MAXIMO = 10 * 1024 * 1024  # 10 MB
EXTENSOES_PERMITIDAS = {".xlsx", ".xls"}


def _nome_seguro(nome: str) -> str:
    base = nome.rsplit(".", 1)
    nome_limpo = re.sub(r"[^\w\-]", "_", base[0])
    ext = f".{base[1]}" if len(base) > 1 else ""
    return f"{nome_limpo}_{uuid.uuid4().hex[:8]}{ext}"


def _fazer_upload_storage(caminho: str, conteudo: bytes, content_type: str) -> None:
    url = f"{settings.SUPABASE_URL}/storage/v1/object/{BUCKET}/{caminho}"
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
        "Content-Type": content_type,
        "x-upsert": "false",
    }
    resp = httpx.post(url, content=conteudo, headers=headers, timeout=30)
    if resp.status_code not in (200, 201):
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao salvar arquivo no Storage: {resp.text}",
        )


def _remover_storage(caminho: str) -> None:
    url = f"{settings.SUPABASE_URL}/storage/v1/object/{BUCKET}/{caminho}"
    headers = {"Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"}
    httpx.delete(url, headers=headers, timeout=10)


def _verificar_acesso_conciliacao(
    conciliacao_id: str,
    usuario: Usuario,
    db: Session,
) -> FechamentoFinanceiro:
    fechamento = db.query(FechamentoFinanceiro).filter(
        FechamentoFinanceiro.id == conciliacao_id
    ).first()
    if not fechamento:
        raise HTTPException(status_code=404, detail="Conciliação não encontrada")
    if usuario.perfil != "admin_ia16" and str(fechamento.empresa_id) != str(usuario.empresa_id):
        raise HTTPException(status_code=403, detail="Sem permissão para acessar esta conciliação")
    return fechamento


def _montar_response(arquivo: ArquivoEnviado, politica_permite_download: bool, politica_permite_reprocessamento: bool) -> ArquivoResponse:
    disponivel = arquivo_disponivel(arquivo)
    return ArquivoResponse(
        id=arquivo.id,
        empresa_id=arquivo.empresa_id,
        conciliacao_id=arquivo.fechamento_id,
        nome_original=arquivo.nome_original,
        tipo_arquivo=arquivo.tipo_arquivo,
        status=arquivo.status,
        tamanho_bytes=arquivo.tamanho_bytes,
        modo_retencao=arquivo.modo_retencao,
        arquivo_persistido=arquivo.arquivo_persistido,
        expira_em=arquivo.expira_em,
        excluido_em=arquivo.excluido_em,
        hash_arquivo=arquivo.hash_arquivo,
        metadados=arquivo.metadados or {},
        arquivo_disponivel=disponivel,
        permitir_download_original=disponivel and politica_permite_download,
        permitir_reprocessamento_sem_reenvio=disponivel and politica_permite_reprocessamento,
        criado_em=arquivo.criado_em,
    )


# ── Listar arquivos da conciliação ──────────────────────────────────────────

@router.get(
    "/api/v1/conciliacoes/{conciliacao_id}/arquivos",
    response_model=RespostaLista[ArquivoResponse],
)
def listar_arquivos(
    conciliacao_id: str,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    fechamento = _verificar_acesso_conciliacao(conciliacao_id, usuario, db)
    politica = buscar_politica_ativa(fechamento.empresa_id, db)

    arquivos = db.query(ArquivoEnviado).filter(
        ArquivoEnviado.fechamento_id == conciliacao_id
    ).order_by(ArquivoEnviado.criado_em.desc()).all()

    dados = [
        _montar_response(a, politica.permitir_download_original, politica.permitir_reprocessamento_sem_reenvio)
        for a in arquivos
    ]

    from app.schemas.resposta import paginar
    return RespostaLista(dados=dados, paginacao=paginar(len(dados), 1, len(dados) or 1))


# ── Enviar arquivo ───────────────────────────────────────────────────────────

@router.post(
    "/api/v1/conciliacoes/{conciliacao_id}/arquivos",
    response_model=RespostaSucesso[ArquivoResponse],
    status_code=status.HTTP_201_CREATED,
)
async def enviar_arquivo(
    conciliacao_id: str,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
    arquivo: UploadFile = File(...),
    tipo_arquivo: str = Form(...),
):
    fechamento = _verificar_acesso_conciliacao(conciliacao_id, usuario, db)

    # Buscar ou criar política da empresa
    politica = buscar_politica_ativa(fechamento.empresa_id, db)

    # Bloquear upload standalone para somente_memoria
    if politica.modo_retencao == "somente_memoria":
        raise HTTPException(
            status_code=400,
            detail={
                "sucesso": False,
                "erro": {
                    "codigo": "POLITICA_RETENCAO_REQUER_PROCESSAMENTO_IMEDIATO",
                    "mensagem": (
                        "A política de retenção desta empresa exige processamento em memória. "
                        "Envie os arquivos pelo fluxo de processamento imediato."
                    ),
                    "detalhes": {"empresa_id": str(fechamento.empresa_id)},
                },
            },
        )

    # Validar extensão
    nome = arquivo.filename or "arquivo"
    ext = "." + nome.rsplit(".", 1)[-1].lower() if "." in nome else ""
    if ext not in EXTENSOES_PERMITIDAS:
        raise HTTPException(status_code=422, detail=f"Extensão não permitida. Use: {', '.join(EXTENSOES_PERMITIDAS)}")

    # Ler e validar tamanho
    conteudo = await arquivo.read()
    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(status_code=422, detail="Arquivo excede o tamanho máximo de 10 MB")

    nome_armazenado = _nome_seguro(nome)
    caminho = f"{fechamento.empresa_id}/{conciliacao_id}/originais/{nome_armazenado}"
    content_type = arquivo.content_type or "application/octet-stream"

    # Upload para Supabase Storage
    _fazer_upload_storage(caminho, conteudo, content_type)

    # Calcular campos de retenção
    campos_retencao = calcular_campos_retencao(politica, conteudo, nome, content_type)

    # Salvar metadados
    novo = ArquivoEnviado(
        empresa_id=fechamento.empresa_id,
        fechamento_id=uuid.UUID(conciliacao_id),
        criado_por_usuario_id=usuario.id,
        nome_original=nome,
        nome_armazenado=nome_armazenado,
        tipo_arquivo=tipo_arquivo,
        caminho_storage=caminho,
        tamanho_bytes=len(conteudo),
        status="enviado",
        atualizado_em=datetime.now(timezone.utc),
        **campos_retencao,
    )
    db.add(novo)

    # Atualizar status da conciliação para arquivos_enviados se estava em rascunho
    if fechamento.status == "rascunho":
        fechamento.status = "arquivos_enviados"
        fechamento.atualizado_em = datetime.now(timezone.utc)

    db.commit()
    db.refresh(novo)

    resposta = _montar_response(novo, politica.permitir_download_original, politica.permitir_reprocessamento_sem_reenvio)
    return RespostaSucesso(dados=resposta, mensagem="Arquivo enviado com sucesso")


# ── Remover arquivo ──────────────────────────────────────────────────────────

@router.delete(
    "/api/v1/arquivos/{arquivo_id}",
    response_model=RespostaSucesso[None],
)
def remover_arquivo(
    arquivo_id: str,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    arquivo = db.query(ArquivoEnviado).filter(ArquivoEnviado.id == arquivo_id).first()
    if not arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    if usuario.perfil != "admin_ia16" and str(arquivo.empresa_id) != str(usuario.empresa_id):
        raise HTTPException(status_code=403, detail="Sem permissão")

    if arquivo.status == "lido":
        raise HTTPException(status_code=409, detail="Não é possível remover arquivo já processado")

    if arquivo.arquivo_persistido and arquivo.excluido_em is None:
        _remover_storage(arquivo.caminho_storage)

    # Verificar se era o último arquivo válido da conciliação
    restantes = db.query(ArquivoEnviado).filter(
        ArquivoEnviado.fechamento_id == arquivo.fechamento_id,
        ArquivoEnviado.id != arquivo.id,
        ArquivoEnviado.excluido_em == None,  # noqa: E711
    ).count()

    if restantes == 0:
        fechamento = db.query(FechamentoFinanceiro).filter(
            FechamentoFinanceiro.id == arquivo.fechamento_id
        ).first()
        if fechamento and fechamento.status == "arquivos_enviados":
            fechamento.status = "rascunho"
            fechamento.atualizado_em = datetime.now(timezone.utc)

    db.delete(arquivo)
    db.commit()

    return RespostaSucesso(dados=None, mensagem="Arquivo removido com sucesso")
