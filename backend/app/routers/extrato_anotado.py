"""
Endpoints do fluxo extrato_anotado.

GET  /api/v1/conciliacoes/{id}/extrato-anotado  — listar lançamentos anotáveis
PATCH /api/v1/extrato-anotado/{lancamento_id}   — anotar/revisar um lançamento
"""
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_usuario_atual
from app.core.database import get_db
from app.core.permissoes import verificar_acesso_por_empresa_id
from app.models.fechamento_financeiro import FechamentoFinanceiro
from app.models.lancamento_extrato_anotado import LancamentoExtratoAnotado
from app.models.log_processamento import LogProcessamento
from app.models.usuario import Usuario
from app.schemas.extrato_anotado import AtualizarLancamentoAnotado, LancamentoExtratoAnotadoResponse
from app.schemas.resposta import RespostaErro, RespostaLista, RespostaSucesso, paginar

router = APIRouter(tags=["extrato_anotado"])


def _verificar_acesso(conciliacao_id: str, usuario: Usuario, db: Session) -> FechamentoFinanceiro:
    fechamento = db.query(FechamentoFinanceiro).filter(FechamentoFinanceiro.id == conciliacao_id).first()
    if not fechamento:
        raise HTTPException(status_code=404, detail={
            "sucesso": False, "erro": {"codigo": "FECHAMENTO_NAO_ENCONTRADO", "mensagem": "Conciliação não encontrada."}
        })
    verificar_acesso_por_empresa_id(fechamento.empresa_id, usuario, db)
    if fechamento.tipo_conciliacao != "extrato_anotado":
        raise HTTPException(status_code=400, detail={
            "sucesso": False, "erro": {
                "codigo": "TIPO_CONCILIACAO_INVALIDO",
                "mensagem": "Este endpoint é exclusivo para conciliações do tipo extrato_anotado.",
            }
        })
    return fechamento


@router.get(
    "/api/v1/conciliacoes/{conciliacao_id}/extrato-anotado",
    response_model=RespostaLista[LancamentoExtratoAnotadoResponse],
)
def listar_lancamentos_anotados(
    conciliacao_id: str,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
    status_revisao: str | None = Query(None),
    pagina: int = Query(1, ge=1),
    limite: int = Query(50, ge=1, le=200),
):
    _verificar_acesso(conciliacao_id, usuario, db)

    q = db.query(LancamentoExtratoAnotado).filter(
        LancamentoExtratoAnotado.fechamento_id == conciliacao_id
    )
    if status_revisao:
        q = q.filter(LancamentoExtratoAnotado.status_revisao == status_revisao)

    total = q.count()
    lancamentos = (
        q.order_by(LancamentoExtratoAnotado.data_lancamento, LancamentoExtratoAnotado.linha_origem)
        .offset((pagina - 1) * limite)
        .limit(limite)
        .all()
    )

    return RespostaLista(
        dados=[LancamentoExtratoAnotadoResponse.model_validate(l) for l in lancamentos],
        paginacao=paginar(total, pagina, limite),
    )


@router.patch(
    "/api/v1/extrato-anotado/{lancamento_id}",
    response_model=RespostaSucesso[LancamentoExtratoAnotadoResponse],
    responses={400: {"model": RespostaErro}, 403: {"model": RespostaErro}, 404: {"model": RespostaErro}},
)
def anotar_lancamento(
    lancamento_id: str,
    dados: AtualizarLancamentoAnotado,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    lancamento = db.query(LancamentoExtratoAnotado).filter(
        LancamentoExtratoAnotado.id == lancamento_id
    ).first()

    if not lancamento:
        raise HTTPException(status_code=404, detail={
            "sucesso": False, "erro": {"codigo": "LANCAMENTO_NAO_ENCONTRADO", "mensagem": "Lançamento não encontrado."}
        })

    verificar_acesso_por_empresa_id(lancamento.empresa_id, usuario, db)

    status_anterior = lancamento.status_revisao
    agora = datetime.now(timezone.utc)

    if dados.categoria is not None:
        lancamento.categoria = dados.categoria
    if dados.descricao_negocio is not None:
        lancamento.descricao_negocio = dados.descricao_negocio
    if dados.nf_doc is not None:
        lancamento.nf_doc = dados.nf_doc
    if dados.valor_nf_doc is not None:
        lancamento.valor_nf_doc = dados.valor_nf_doc
    if dados.observacao is not None:
        lancamento.observacao = dados.observacao
    if dados.status_revisao is not None:
        lancamento.status_revisao = dados.status_revisao

    lancamento.atualizado_por_usuario_id = usuario.id
    lancamento.atualizado_em = agora

    partes = []
    if dados.status_revisao and dados.status_revisao != status_anterior:
        partes.append(f"status: '{status_anterior}' → '{dados.status_revisao}'")
    if dados.categoria is not None:
        partes.append("categoria atualizada")
    if dados.descricao_negocio is not None:
        partes.append("descrição de negócio atualizada")

    if partes:
        db.add(LogProcessamento(
            empresa_id=lancamento.empresa_id,
            fechamento_id=lancamento.fechamento_id,
            nivel="info",
            evento="lancamento_anotado",
            mensagem=f"Lançamento anotado por '{usuario.email}': {', '.join(partes)}.",
            detalhes={
                "lancamento_id": str(lancamento.id),
                "usuario_id": str(usuario.id),
                "status_anterior": status_anterior,
            },
        ))

    db.commit()
    db.refresh(lancamento)

    return RespostaSucesso(
        dados=LancamentoExtratoAnotadoResponse.model_validate(lancamento),
        mensagem="Lançamento atualizado com sucesso.",
    )
