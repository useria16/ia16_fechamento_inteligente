from typing import Annotated
import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.auth import get_usuario_atual
from app.models.usuario import Usuario
from app.schemas.resposta import RespostaSucesso

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class UsuarioAtual(BaseModel):
    id: uuid.UUID
    nome: str
    email: str
    perfil: str
    empresa_id: uuid.UUID | None


@router.get("/eu", response_model=RespostaSucesso[UsuarioAtual])
def obter_usuario_atual(usuario: Annotated[Usuario, Depends(get_usuario_atual)]):
    return RespostaSucesso(dados=UsuarioAtual(
        id=usuario.id,
        nome=usuario.nome,
        email=usuario.email,
        perfil=usuario.perfil,
        empresa_id=usuario.empresa_id,
    ))
