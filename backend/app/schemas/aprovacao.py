import uuid
from datetime import datetime

from pydantic import BaseModel


class AprovarFechamentoRequest(BaseModel):
    observacao_aprovacao: str | None = None


class ReabrirFechamentoRequest(BaseModel):
    motivo: str | None = None


class RespostaAprovacao(BaseModel):
    id: uuid.UUID
    status: str
    aprovado_em: datetime
    aprovado_por_usuario_id: uuid.UUID
    observacao_aprovacao: str | None

    model_config = {"from_attributes": True}


class RespostaReabertura(BaseModel):
    id: uuid.UUID
    status: str
    reaberto_em: datetime
    reaberto_por_usuario_id: uuid.UUID

    model_config = {"from_attributes": True}
