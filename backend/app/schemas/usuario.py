import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr

PerfilUsuario = Literal["admin_ia16", "cliente_admin", "cliente_operador"]


class UsuarioCreate(BaseModel):
    empresa_id: uuid.UUID | None = None
    usuario_auth_id: uuid.UUID
    nome: str
    email: EmailStr
    perfil: PerfilUsuario


class UsuarioResponse(BaseModel):
    id: uuid.UUID
    empresa_id: uuid.UUID | None
    usuario_auth_id: uuid.UUID
    nome: str
    email: str
    perfil: PerfilUsuario
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}


class UsuarioPatch(BaseModel):
    nome: str | None = None
    ativo: bool | None = None
    perfil: PerfilUsuario | None = None
