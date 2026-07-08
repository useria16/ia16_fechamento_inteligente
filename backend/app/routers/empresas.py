from typing import Annotated
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_usuario_atual, exigir_perfil
from app.core.database import get_db
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.schemas.empresa import EmpresaCreate, EmpresaPatch, EmpresaResponse

router = APIRouter(prefix="/api/v1/empresas", tags=["empresas"])


@router.get("", response_model=list[EmpresaResponse])
def listar_empresas(
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    if usuario.perfil == "admin_ia16":
        return db.query(Empresa).all()
    return db.query(Empresa).filter(Empresa.id == usuario.empresa_id).all()


@router.post("", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
def criar_empresa(
    dados: EmpresaCreate,
    usuario: Annotated[Usuario, Depends(exigir_perfil("admin_ia16"))],
    db: Annotated[Session, Depends(get_db)],
):
    existente = db.query(Empresa).filter(Empresa.cnpj == dados.cnpj).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="CNPJ já cadastrado")

    empresa = Empresa(nome=dados.nome, cnpj=dados.cnpj)
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return empresa


@router.get("/{empresa_id}", response_model=EmpresaResponse)
def obter_empresa(
    empresa_id: str,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

    if usuario.perfil != "admin_ia16" and str(usuario.empresa_id) != str(empresa_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso não autorizado")

    return empresa


@router.patch("/{empresa_id}", response_model=EmpresaResponse)
def atualizar_empresa(
    empresa_id: str,
    dados: EmpresaPatch,
    usuario: Annotated[Usuario, Depends(exigir_perfil("admin_ia16"))],
    db: Annotated[Session, Depends(get_db)],
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

    if dados.nome is not None:
        empresa.nome = dados.nome
    if dados.status is not None:
        empresa.status = dados.status

    empresa.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(empresa)
    return empresa
