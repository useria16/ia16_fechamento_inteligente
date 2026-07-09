import uuid

from app.services import supabase_auth_service


class _RespostaOk:
    status_code = 200

    def json(self):
        return {}


class _ClienteHttpFake:
    chamadas: list[dict] = []

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def put(self, url, headers, json):
        self.chamadas.append({"url": url, "headers": headers, "json": json})
        return _RespostaOk()


def test_atualizar_senha_usuario_auth_confirma_email(monkeypatch):
    """
    Usuários controlados pela iA16 não dependem de confirmação por e-mail.
    Ao resetar senha, o Auth também deve marcar o e-mail como confirmado.
    """
    _ClienteHttpFake.chamadas = []
    monkeypatch.setattr(supabase_auth_service.httpx, "Client", _ClienteHttpFake)

    supabase_auth_service.atualizar_senha_usuario_auth(
        uuid.UUID("11111111-1111-1111-1111-111111111111"),
        "SenhaForte123",
    )

    assert _ClienteHttpFake.chamadas[0]["json"] == {
        "password": "SenhaForte123",
        "email_confirm": True,
    }
