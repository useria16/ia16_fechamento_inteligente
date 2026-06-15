"""
Endpoint de revisão de divergências — Sprint 7A.

PATCH /api/v1/divergencias/{id}
  Permite ao operador revisar uma divergência gerada pelo motor:
  atualizar status e registrar observação.
"""
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_usuario_atual
from app.core.database import get_db
from app.models.divergencia_conciliacao import DivergenciaConciliacao
from app.models.log_processamento import LogProcessamento
from app.models.usuario import Usuario
from app.schemas.divergencia import DivergenciaAtualizacao, DivergenciaDetalhe
from app.schemas.resposta import RespostaErro, RespostaSucesso

router = APIRouter(prefix="/api/v1/divergencias", tags=["divergencias"])

_STATUS_VALIDOS = {"aberta", "em_analise", "resolvida", "ignorada"}


def _log_revisao(
    db: Session,
    divergencia: DivergenciaConciliacao,
    usuario: Usuario,
    status_anterior: str,
    novo_status: str | None,
    tem_observacao: bool,
) -> None:
    partes = []
    if novo_status and novo_status != status_anterior:
        partes.append(f"status: '{status_anterior}' → '{novo_status}'")
    if tem_observacao:
        partes.append("observação atualizada")
    if not partes:
        return
    db.add(LogProcessamento(
        empresa_id=divergencia.empresa_id,
        fechamento_id=divergencia.fechamento_id,
        nivel="info",
        evento="divergencia_revisada",
        mensagem=f"Divergência revisada pelo usuário '{usuario.email}': {', '.join(partes)}.",
        detalhes={
            "divergencia_id": str(divergencia.id),
            "tipo_divergencia": divergencia.tipo_divergencia,
            "usuario_id": str(usuario.id),
            "status_anterior": status_anterior,
            "novo_status": novo_status,
        },
    ))


@router.patch(
    "/{divergencia_id}",
    response_model=RespostaSucesso[DivergenciaDetalhe],
    responses={
        400: {"model": RespostaErro},
        403: {"model": RespostaErro},
        404: {"model": RespostaErro},
        422: {"model": RespostaErro},
    },
)
def revisar_divergencia(
    divergencia_id: str,
    dados: DivergenciaAtualizacao,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    # ── 1. Verificar existência ───────────────────────────────────────────
    divergencia = db.query(DivergenciaConciliacao).filter(
        DivergenciaConciliacao.id == divergencia_id
    ).first()

    if not divergencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "sucesso": False,
                "erro": {
                    "codigo": "DIVERGENCIA_NAO_ENCONTRADA",
                    "mensagem": "Divergência não encontrada.",
                    "detalhes": {"divergencia_id": divergencia_id},
                },
            },
        )

    # ── 2. Verificar acesso por empresa ───────────────────────────────────
    if usuario.perfil != "admin_ia16" and str(divergencia.empresa_id) != str(usuario.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "sucesso": False,
                "erro": {
                    "codigo": "SEM_PERMISSAO_DIVERGENCIA",
                    "mensagem": "Você não tem permissão para alterar esta divergência.",
                },
            },
        )

    # ── 3. Validar status ─────────────────────────────────────────────────
    if dados.status is not None and dados.status not in _STATUS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "sucesso": False,
                "erro": {
                    "codigo": "STATUS_DIVERGENCIA_INVALIDO",
                    "mensagem": f"Status inválido: '{dados.status}'. Valores aceitos: {sorted(_STATUS_VALIDOS)}.",
                },
            },
        )

    # ── 4. Aplicar alterações ─────────────────────────────────────────────
    agora = datetime.now(timezone.utc)
    status_anterior = divergencia.status

    if dados.status is not None:
        divergencia.status = dados.status
        if dados.status == "resolvida":
            divergencia.resolvido_em = agora
        elif divergencia.resolvido_em is not None:
            divergencia.resolvido_em = None

    if dados.observacao is not None:
        divergencia.observacao = dados.observacao

    divergencia.atualizado_por_usuario_id = usuario.id
    divergencia.atualizado_em = agora

    # ── 5. Log de revisão ─────────────────────────────────────────────────
    _log_revisao(
        db=db,
        divergencia=divergencia,
        usuario=usuario,
        status_anterior=status_anterior,
        novo_status=dados.status,
        tem_observacao=dados.observacao is not None,
    )

    db.commit()
    db.refresh(divergencia)

    return RespostaSucesso(
        dados=DivergenciaDetalhe.model_validate(divergencia),
        mensagem="Divergência atualizada com sucesso",
    )
