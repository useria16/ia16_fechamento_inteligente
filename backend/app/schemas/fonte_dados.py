import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel

TipoFonteDados = Literal["excel_manual", "banco", "adquirente", "erp", "google_drive", "outro"]


class FonteDadosCreate(BaseModel):
    nome: str
    tipo: TipoFonteDados
    empresa_id: uuid.UUID | None = None
    configuracao: dict[str, Any] | None = None


class FonteDadosResponse(BaseModel):
    id: uuid.UUID
    empresa_id: uuid.UUID
    nome: str
    tipo: TipoFonteDados
    ativo: bool
    configuracao: dict[str, Any] | None
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}


class FonteDadosPatch(BaseModel):
    nome: str | None = None
    ativo: bool | None = None
    configuracao: dict[str, Any] | None = None
