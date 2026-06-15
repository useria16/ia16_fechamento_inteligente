import json
import uuid
import urllib.request
from typing import Annotated

import jwt
from jwt import PyJWK, PyJWKSet
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.usuario import Usuario

bearer_scheme = HTTPBearer()

_jwks_cache: PyJWKSet | None = None


def _buscar_jwks() -> PyJWKSet:
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache

    url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    req = urllib.request.Request(url, headers={
        "apikey": settings.SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
    })
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read())

    _jwks_cache = PyJWKSet.from_dict(data)
    return _jwks_cache


def _decode_token(token: str) -> dict:
    try:
        jwks = _buscar_jwks()
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        chave: PyJWK | None = None
        for k in jwks.keys:
            if k.key_id == kid:
                chave = k
                break
        if chave is None:
            chave = jwks.keys[0]

        payload = jwt.decode(
            token,
            chave.key,
            algorithms=["RS256", "ES256"],
            audience="authenticated",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token inválido: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao validar token: {e}")


def get_usuario_atual(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    payload = _decode_token(credentials.credentials)
    auth_id = uuid.UUID(payload["sub"])

    usuario = db.query(Usuario).filter(
        Usuario.usuario_auth_id == auth_id,
        Usuario.ativo == True,  # noqa: E712
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
        )
    return usuario


def exigir_perfil(*perfis: str):
    def verificar(usuario: Annotated[Usuario, Depends(get_usuario_atual)]) -> Usuario:
        if usuario.perfil not in perfis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso não autorizado para este perfil",
            )
        return usuario
    return verificar
