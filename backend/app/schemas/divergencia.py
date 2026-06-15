import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, model_validator


StatusDivergencia = Literal["aberta", "em_analise", "resolvida", "ignorada"]

STATUS_VALIDOS: set[str] = {"aberta", "em_analise", "resolvida", "ignorada"}


class DivergenciaAtualizacao(BaseModel):
    status: StatusDivergencia | None = None
    observacao: str | None = None

    @model_validator(mode="after")
    def ao_menos_um_campo(self) -> "DivergenciaAtualizacao":
        if self.status is None and self.observacao is None:
            raise ValueError("Pelo menos um campo deve ser informado: status ou observacao.")
        return self


class DivergenciaDetalhe(BaseModel):
    id: uuid.UUID
    fechamento_id: uuid.UUID
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
