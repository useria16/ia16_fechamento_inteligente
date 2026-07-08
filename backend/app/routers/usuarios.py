from typing import Annotated
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_usuario_atual, exigir_perfil
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioPatch, UsuarioResponse

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UsuarioResponse])
def listar_usuarios(
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    if usuario.perfil == "admin_ia16":
        return db.query(Usuario).all()
    return db.query(Usuario).filter(Usuario.empresa_id == usuario.empresa_id).all()


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    dados: UsuarioCreate,
    usuario: Annotated[Usuario, Depends(exigir_perfil("admin_ia16", "cliente_admin"))],
    db: Annotated[Session, Depends(get_db)],
):
    if usuario.perfil == "cliente_admin" and str(dados.empresa_id) != str(usuario.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é permitido criar usuário para outra empresa",
        )

    existente = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")

    novo = Usuario(
        empresa_id=dados.empresa_id,
        usuario_auth_id=dados.usuario_auth_id,
        nome=dados.nome,
        email=dados.email,
        perfil=dados.perfil,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obter_usuario(
    usuario_id: str,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    alvo = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not alvo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    if usuario.perfil != "admin_ia16" and str(alvo.empresa_id) != str(usuario.empresa_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso não autorizado")

    return alvo


@router.patch("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    usuario_id: str,
    dados: UsuarioPatch,
    usuario: Annotated[Usuario, Depends(exigir_perfil("admin_ia16", "cliente_admin"))],
    db: Annotated[Session, Depends(get_db)],
):
    alvo = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not alvo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    if usuario.perfil == "cliente_admin" and str(alvo.empresa_id) != str(usuario.empresa_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso não autorizado")

    if dados.nome is not None:
        alvo.nome = dados.nome
    if dados.ativo is not None:
        alvo.ativo = dados.ativo
    if dados.perfil is not None:
        alvo.perfil = dados.perfil

    alvo.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alvo)
    return alvo
