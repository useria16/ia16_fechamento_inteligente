from typing import Annotated
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import exigir_perfil, get_usuario_atual
from app.core.database import get_db
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from app.schemas.cliente import ClienteCreate, ClientePatch, ClienteResponse

router = APIRouter(prefix="/api/v1/clientes", tags=["clientes"])


@router.get("", response_model=list[ClienteResponse])
def listar_clientes(
    usuario: Annotated[Usuario, Depends(exigir_perfil("admin_ia16"))],
    db: Annotated[Session, Depends(get_db)],
):
    return db.query(Cliente).order_by(Cliente.nome).all()


@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(
    dados: ClienteCreate,
    usuario: Annotated[Usuario, Depends(exigir_perfil("admin_ia16"))],
    db: Annotated[Session, Depends(get_db)],
):
    cliente = Cliente(nome=dados.nome)
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.get("/{cliente_id}", response_model=ClienteResponse)
def obter_cliente(
    cliente_id: str,
    usuario: Annotated[Usuario, Depends(exigir_perfil("admin_ia16"))],
    db: Annotated[Session, Depends(get_db)],
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return cliente


@router.patch("/{cliente_id}", response_model=ClienteResponse)
def atualizar_cliente(
    cliente_id: str,
    dados: ClientePatch,
    usuario: Annotated[Usuario, Depends(exigir_perfil("admin_ia16"))],
    db: Annotated[Session, Depends(get_db)],
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")

    if dados.nome is not None:
        cliente.nome = dados.nome
    if dados.ativo is not None:
        cliente.ativo = dados.ativo

    cliente.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cliente)
    return cliente
