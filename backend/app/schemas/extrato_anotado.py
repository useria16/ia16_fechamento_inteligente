import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, model_validator

StatusRevisao = Literal["pendente", "em_revisao", "revisado", "ignorado"]


class LancamentoExtratoAnotadoResponse(BaseModel):
    id: uuid.UUID
    fechamento_id: uuid.UUID
    arquivo_id: uuid.UUID
    data_lancamento: date
    descricao_banco: str
    razao_social: str | None
    documento: str | None
    valor: Decimal
    tipo_movimento: str
    saldo: Decimal | None
    linha_origem: int | None
    categoria: str | None
    descricao_negocio: str | None
    nf_doc: str | None
    valor_nf_doc: Decimal | None
    observacao: str | None
    categoria_sugerida: str | None
    confianca_sugestao: Decimal | None
    status_revisao: StatusRevisao
    atualizado_por_usuario_id: uuid.UUID | None
    criado_em: datetime
    atualizado_em: datetime

    # Conferência com fluxo de caixa
    previsto_no_fluxo: bool | None = None
    tipo_conferencia_fluxo: str | None = None
    confianca_conferencia: Decimal | None = None
    observacao_sistema: str | None = None
    data_prevista: date | None = None
    valor_previsto: Decimal | None = None
    descricao_prevista: str | None = None

    model_config = {"from_attributes": True}


class AtualizarLancamentoAnotado(BaseModel):
    categoria: str | None = None
    descricao_negocio: str | None = None
    nf_doc: str | None = None
    valor_nf_doc: Decimal | None = None
    observacao: str | None = None
    status_revisao: StatusRevisao | None = None

    @model_validator(mode="after")
    def ao_menos_um_campo(self) -> "AtualizarLancamentoAnotado":
        campos = [self.categoria, self.descricao_negocio, self.nf_doc, self.valor_nf_doc, self.observacao, self.status_revisao]
        if all(c is None for c in campos):
            raise ValueError("Pelo menos um campo deve ser informado.")
        return self
