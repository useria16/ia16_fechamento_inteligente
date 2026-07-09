"""
Helper central de autorização por empresa.

Regra:
- admin_ia16: acessa qualquer empresa.
- usuário com cliente_id: acessa empresas cujo empresa.cliente_id == usuario.cliente_id.
- fallback legado: sem cliente_id, acessa somente usuario.empresa_id.
- outros: acesso negado (403).
"""
import uuid
from typing import Union

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.empresa import Empresa
from app.models.usuario import Usuario


def validar_acesso_empresa(
    db: Session,
    usuario: Usuario,
    empresa_id: Union[str, uuid.UUID],
) -> Empresa:
    """
    Verifica se o usuário tem acesso à empresa e retorna o objeto Empresa.

    Raises:
        HTTPException 404: empresa não encontrada.
        HTTPException 403: usuário não tem permissão para acessar esta empresa.
    """
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada",
        )

    if usuario.perfil == "admin_ia16":
        return empresa

    if usuario.cliente_id:
        if str(empresa.cliente_id) != str(usuario.cliente_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para acessar dados desta empresa",
            )
        return empresa

    # fallback legado: usuário vinculado diretamente a uma empresa
    if usuario.empresa_id:
        if str(empresa.id) != str(usuario.empresa_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para acessar dados desta empresa",
            )
        return empresa

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Usuário sem vínculo de empresa ou cliente",
    )


def empresa_ids_do_usuario(usuario: Usuario, db: Session) -> list[str]:
    """Retorna IDs de todas as empresas acessíveis pelo usuário."""
    if usuario.cliente_id:
        rows = db.query(Empresa.id).filter(Empresa.cliente_id == usuario.cliente_id).all()
        return [str(r.id) for r in rows]
    if usuario.empresa_id:
        return [str(usuario.empresa_id)]
    return []


def verificar_acesso_por_empresa_id(
    empresa_id_recurso: Union[str, uuid.UUID],
    usuario: Usuario,
    db: Session,
) -> None:
    """Levanta 403 se o usuário não-admin não tiver acesso ao empresa_id do recurso."""
    if usuario.perfil == "admin_ia16":
        return
    ids_permitidos = empresa_ids_do_usuario(usuario, db)
    if str(empresa_id_recurso) not in ids_permitidos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar dados desta empresa",
        )
