import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, model_validator

PerfilUsuario = Literal["admin_ia16", "cliente_admin", "cliente_operador"]


class UsuarioCreate(BaseModel):
    cliente_id: uuid.UUID | None = None
    empresa_id: uuid.UUID | None = None  # legado — mantido por compatibilidade
    nome: str
    email: EmailStr
    perfil: PerfilUsuario
    senha_temporaria: str = Field(min_length=8)

    @model_validator(mode="after")
    def validar_cliente_para_usuario(self):
        if self.perfil != "admin_ia16" and self.cliente_id is None:
            raise ValueError("cliente_id é obrigatório para usuários de cliente")
        return self


class UsuarioResponse(BaseModel):
    id: uuid.UUID
    cliente_id: uuid.UUID | None
    empresa_id: uuid.UUID | None  # legado
    usuario_auth_id: uuid.UUID
    nome: str
    email: str
    perfil: PerfilUsuario
    ativo: bool
    troca_senha_obrigatoria: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}


class UsuarioPatch(BaseModel):
    nome: str | None = None
    ativo: bool | None = None
    perfil: PerfilUsuario | None = None


class TrocarSenhaRequest(BaseModel):
    nova_senha: str = Field(min_length=8)


class ResetarSenhaRequest(BaseModel):
    senha_temporaria: str = Field(min_length=8)
