import uuid
from datetime import datetime

from pydantic import BaseModel


class ClienteCreate(BaseModel):
    nome: str


class ClientePatch(BaseModel):
    nome: str | None = None
    ativo: bool | None = None


class ClienteResponse(BaseModel):
    id: uuid.UUID
    nome: str
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}
