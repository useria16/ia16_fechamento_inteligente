import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator


class EmpresaCreate(BaseModel):
    cliente_id: uuid.UUID
    nome: str
    cnpj: str

    @field_validator("cnpj")
    @classmethod
    def cnpj_apenas_numeros(cls, v: str) -> str:
        numeros = "".join(filter(str.isdigit, v))
        if len(numeros) != 14:
            raise ValueError("CNPJ deve conter 14 dígitos")
        return numeros


class EmpresaResponse(BaseModel):
    id: uuid.UUID
    cliente_id: uuid.UUID | None
    nome: str
    cnpj: str
    status: Literal["ativa", "inativa"]
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}


class EmpresaSimples(BaseModel):
    id: uuid.UUID
    nome: str
    cnpj: str

    model_config = {"from_attributes": True}


class EmpresaPatch(BaseModel):
    nome: str | None = None
    status: Literal["ativa", "inativa"] | None = None
