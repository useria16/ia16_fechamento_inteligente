import uuid

import httpx

from app.core.config import settings


class SupabaseAuthError(Exception):
    pass


ERRO_CONEXAO_AUTH = "Não foi possível executar a operação no provedor de autenticação."


def _headers() -> dict[str, str]:
    return {
        "apikey": settings.SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
    }


def criar_usuario_auth(email: str, senha: str) -> uuid.UUID:
    url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/admin/users"
    payload = {
        "email": email,
        "password": senha,
        "email_confirm": True,
    }

    try:
        with httpx.Client(timeout=15) as client:
            resposta = client.post(url, headers=_headers(), json=payload)
    except httpx.HTTPError as exc:
        raise SupabaseAuthError(ERRO_CONEXAO_AUTH) from exc
    except Exception as exc:
        raise SupabaseAuthError(ERRO_CONEXAO_AUTH) from exc

    if resposta.status_code >= 400:
        raise SupabaseAuthError(_mensagem_erro(resposta))

    dados = resposta.json()
    auth_id = dados.get("id")
    if not auth_id:
        raise SupabaseAuthError("Supabase Auth não retornou o ID do usuário.")
    return uuid.UUID(auth_id)


def atualizar_senha_usuario_auth(usuario_auth_id: uuid.UUID, nova_senha: str) -> None:
    url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/admin/users/{usuario_auth_id}"
    payload = {
        "password": nova_senha,
        "email_confirm": True,
    }
    try:
        with httpx.Client(timeout=15) as client:
            resposta = client.put(url, headers=_headers(), json=payload)
    except httpx.HTTPError as exc:
        raise SupabaseAuthError(ERRO_CONEXAO_AUTH) from exc
    except Exception as exc:
        raise SupabaseAuthError(ERRO_CONEXAO_AUTH) from exc

    if resposta.status_code >= 400:
        raise SupabaseAuthError(_mensagem_erro(resposta))


def remover_usuario_auth(usuario_auth_id: uuid.UUID) -> None:
    url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/admin/users/{usuario_auth_id}"
    try:
        with httpx.Client(timeout=15) as client:
            client.delete(url, headers=_headers())
    except Exception:
        return


def _mensagem_erro(resposta: httpx.Response) -> str:
    try:
        dados = resposta.json()
    except ValueError:
        return "Erro ao executar operação no Supabase Auth."

    return (
        dados.get("msg")
        or dados.get("message")
        or dados.get("error_description")
        or "Erro ao executar operação no Supabase Auth."
    )
