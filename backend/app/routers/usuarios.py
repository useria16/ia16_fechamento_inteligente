from typing import Annotated
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_usuario_atual, exigir_perfil
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import ResetarSenhaRequest, UsuarioCreate, UsuarioPatch, UsuarioResponse
from app.services.supabase_auth_service import (
    SupabaseAuthError,
    atualizar_senha_usuario_auth,
    criar_usuario_auth,
    remover_usuario_auth,
)

router = APIRouter(prefix="/api/v1/usuarios", tags=["usuarios"])


def _mesmo_cliente(usuario: Usuario, alvo: Usuario) -> bool:
    """Verifica se dois usuários pertencem ao mesmo cliente (com fallback legado por empresa)."""
    if usuario.cliente_id and alvo.cliente_id:
        return str(usuario.cliente_id) == str(alvo.cliente_id)
    # fallback legado
    if usuario.empresa_id and alvo.empresa_id:
        return str(usuario.empresa_id) == str(alvo.empresa_id)
    return False


@router.get("", response_model=list[UsuarioResponse])
def listar_usuarios(
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    if usuario.perfil == "admin_ia16":
        return db.query(Usuario).filter(Usuario.cliente_id.isnot(None)).all()
    if usuario.cliente_id:
        return db.query(Usuario).filter(Usuario.cliente_id == usuario.cliente_id).all()
    # fallback legado
    if usuario.empresa_id:
        return db.query(Usuario).filter(
            Usuario.empresa_id == usuario.empresa_id,
            Usuario.empresa_id.isnot(None),
        ).all()
    return []


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    dados: UsuarioCreate,
    usuario: Annotated[Usuario, Depends(exigir_perfil("admin_ia16", "cliente_admin"))],
    db: Annotated[Session, Depends(get_db)],
):
    if dados.perfil == "admin_ia16" and usuario.perfil != "admin_ia16":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas admin iA16 pode criar outro admin iA16",
        )

    if usuario.perfil == "cliente_admin":
        cliente_destino = dados.cliente_id or dados.empresa_id  # aceita legado
        cliente_atual = usuario.cliente_id or usuario.empresa_id
        if str(cliente_destino) != str(cliente_atual):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Não é permitido criar usuário para outro cliente",
            )
        if dados.perfil != "cliente_operador":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cliente admin só pode criar usuários operadores",
            )

    existente = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")

    try:
        usuario_auth_id = criar_usuario_auth(dados.email, dados.senha_temporaria)
    except SupabaseAuthError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    novo = Usuario(
        cliente_id=dados.cliente_id,
        empresa_id=dados.empresa_id,  # legado
        usuario_auth_id=usuario_auth_id,
        nome=dados.nome,
        email=dados.email,
        perfil=dados.perfil,
        troca_senha_obrigatoria=True,
    )
    try:
        db.add(novo)
        db.commit()
        db.refresh(novo)
    except Exception:
        db.rollback()
        remover_usuario_auth(usuario_auth_id)
        raise
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

    if usuario.perfil != "admin_ia16" and not _mesmo_cliente(usuario, alvo):
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

    if usuario.perfil == "cliente_admin" and not _mesmo_cliente(usuario, alvo):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso não autorizado")

    if dados.nome is not None:
        alvo.nome = dados.nome
    if dados.ativo is not None:
        alvo.ativo = dados.ativo
    if dados.perfil is not None:
        if usuario.perfil != "admin_ia16" and dados.perfil != "cliente_operador":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cliente admin só pode manter perfil operador",
            )
        alvo.perfil = dados.perfil

    alvo.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alvo)
    return alvo


@router.post("/{usuario_id}/resetar-senha", response_model=UsuarioResponse)
def resetar_senha_usuario(
    usuario_id: str,
    dados: ResetarSenhaRequest,
    usuario: Annotated[Usuario, Depends(exigir_perfil("admin_ia16", "cliente_admin"))],
    db: Annotated[Session, Depends(get_db)],
):
    alvo = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not alvo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    if usuario.perfil == "cliente_admin":
        if not _mesmo_cliente(usuario, alvo):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso não autorizado")
        if alvo.perfil != "cliente_operador":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cliente admin só pode resetar senha de operadores",
            )

    try:
        atualizar_senha_usuario_auth(alvo.usuario_auth_id, dados.senha_temporaria)
    except SupabaseAuthError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível resetar a senha no provedor de autenticação.",
        ) from exc

    alvo.troca_senha_obrigatoria = True
    alvo.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alvo)
    return alvo
