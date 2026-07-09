"""
Endpoints de consulta do resultado da conciliação.

GET /api/v1/conciliacoes/{id}/itens        — itens gerados pelo motor
GET /api/v1/conciliacoes/{id}/divergencias  — divergências para revisão
"""
from typing import Annotated, Optional
import uuid
from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import get_usuario_atual
from app.core.database import get_db
from app.core.permissoes import verificar_acesso_por_empresa_id
from app.models.divergencia_conciliacao import DivergenciaConciliacao
from app.models.fechamento_financeiro import FechamentoFinanceiro
from app.models.item_conciliacao import ItemConciliacao
from app.models.usuario import Usuario
from app.schemas.resposta import RespostaLista, paginar

router = APIRouter(prefix="/api/v1/conciliacoes", tags=["resultado_conciliacao"])


class ItemConciliacaoListagem(BaseModel):
    id: uuid.UUID
    tipo_item: str
    status: str
    tipo_movimento: str
    data_prevista: date | None
    data_realizada: date | None
    descricao_prevista: str | None
    descricao_realizada: str | None
    valor_previsto: Decimal | None
    valor_realizado: Decimal | None
    diferenca_valor: Decimal | None
    diferenca_dias: int | None
    confianca: Decimal | None
    criado_em: datetime

    model_config = {"from_attributes": True}


class DivergenciaListagem(BaseModel):
    id: uuid.UUID
    item_conciliacao_id: uuid.UUID
    tipo_divergencia: str
    severidade: str
    descricao: str
    valor_previsto: Decimal | None
    valor_realizado: Decimal | None
    diferenca_valor: Decimal | None
    data_prevista: date | None
    data_realizada: date | None
    diferenca_dias: int | None
    status: str
    observacao: str | None
    resolvido_em: datetime | None
    atualizado_por_usuario_id: uuid.UUID | None
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}


def _verificar_acesso(
    conciliacao_id: str,
    usuario: Usuario,
    db: Session,
) -> FechamentoFinanceiro:
    fechamento = db.query(FechamentoFinanceiro).filter(
        FechamentoFinanceiro.id == conciliacao_id
    ).first()
    if not fechamento:
        raise HTTPException(status_code=404, detail="Conciliação não encontrada")
    verificar_acesso_por_empresa_id(fechamento.empresa_id, usuario, db)
    return fechamento


@router.get(
    "/{conciliacao_id}/itens",
    response_model=RespostaLista[ItemConciliacaoListagem],
)
def listar_itens_conciliacao(
    conciliacao_id: str,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
    status: Optional[str] = Query(None, description="Filtrar por status: conciliado, divergente, pendente"),
    tipo_movimento: Optional[str] = Query(None),
    pagina: int = Query(1, ge=1),
    limite: int = Query(50, ge=1, le=200),
):
    _verificar_acesso(conciliacao_id, usuario, db)

    q = db.query(ItemConciliacao).filter(
        ItemConciliacao.fechamento_id == conciliacao_id
    )
    if status:
        q = q.filter(ItemConciliacao.status == status)
    if tipo_movimento:
        q = q.filter(ItemConciliacao.tipo_movimento == tipo_movimento)

    total = q.count()
    itens = q.order_by(ItemConciliacao.criado_em.asc()).offset((pagina - 1) * limite).limit(limite).all()

    dados = [ItemConciliacaoListagem.model_validate(item) for item in itens]
    return RespostaLista(dados=dados, paginacao=paginar(total, pagina, limite))


@router.get(
    "/{conciliacao_id}/divergencias",
    response_model=RespostaLista[DivergenciaListagem],
)
def listar_divergencias_conciliacao(
    conciliacao_id: str,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
    status: Optional[str] = Query(None, description="Filtrar por status: aberta, resolvida, ignorada, em_analise"),
    tipo_divergencia: Optional[str] = Query(None),
    severidade: Optional[str] = Query(None),
    pagina: int = Query(1, ge=1),
    limite: int = Query(50, ge=1, le=200),
):
    _verificar_acesso(conciliacao_id, usuario, db)

    q = db.query(DivergenciaConciliacao).filter(
        DivergenciaConciliacao.fechamento_id == conciliacao_id
    )
    if status:
        q = q.filter(DivergenciaConciliacao.status == status)
    if tipo_divergencia:
        q = q.filter(DivergenciaConciliacao.tipo_divergencia == tipo_divergencia)
    if severidade:
        q = q.filter(DivergenciaConciliacao.severidade == severidade)

    total = q.count()
    divs = q.order_by(DivergenciaConciliacao.severidade.desc(), DivergenciaConciliacao.criado_em.asc()).offset((pagina - 1) * limite).limit(limite).all()

    dados = [DivergenciaListagem.model_validate(div) for div in divs]
    return RespostaLista(dados=dados, paginacao=paginar(total, pagina, limite))
