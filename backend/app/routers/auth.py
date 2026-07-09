from typing import Annotated
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import get_usuario_atual
from app.core.database import get_db
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.schemas.empresa import EmpresaSimples
from app.schemas.resposta import RespostaSucesso
from app.schemas.usuario import TrocarSenhaRequest
from app.services.supabase_auth_service import SupabaseAuthError, atualizar_senha_usuario_auth

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class UsuarioAtual(BaseModel):
    id: uuid.UUID
    nome: str
    email: str
    perfil: str
    cliente_id: uuid.UUID | None
    empresa_id: uuid.UUID | None  # legado
    troca_senha_obrigatoria: bool
    empresas: list[EmpresaSimples]


def _empresas_do_usuario(usuario: Usuario, db: Session) -> list[EmpresaSimples]:
    if usuario.perfil == "admin_ia16":
        rows = db.query(Empresa).order_by(Empresa.nome).all()
    elif usuario.cliente_id:
        rows = (
            db.query(Empresa)
            .filter(Empresa.cliente_id == usuario.cliente_id)
            .order_by(Empresa.nome)
            .all()
        )
    elif usuario.empresa_id:
        empresa = db.query(Empresa).filter(Empresa.id == usuario.empresa_id).first()
        rows = [empresa] if empresa else []
    else:
        rows = []
    return [EmpresaSimples.model_validate(e) for e in rows]


def _montar_usuario_atual(usuario: Usuario, db: Session) -> UsuarioAtual:
    return UsuarioAtual(
        id=usuario.id,
        nome=usuario.nome,
        email=usuario.email,
        perfil=usuario.perfil,
        cliente_id=usuario.cliente_id,
        empresa_id=usuario.empresa_id,
        troca_senha_obrigatoria=usuario.troca_senha_obrigatoria,
        empresas=_empresas_do_usuario(usuario, db),
    )


@router.get("/eu", response_model=RespostaSucesso[UsuarioAtual])
def obter_usuario_atual(
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    return RespostaSucesso(dados=_montar_usuario_atual(usuario, db))


@router.post("/trocar-senha", response_model=RespostaSucesso[UsuarioAtual])
def trocar_senha(
    dados: TrocarSenhaRequest,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        atualizar_senha_usuario_auth(usuario.usuario_auth_id, dados.nova_senha)
    except SupabaseAuthError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    usuario.troca_senha_obrigatoria = False
    usuario.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(usuario)

    return RespostaSucesso(dados=_montar_usuario_atual(usuario, db))
