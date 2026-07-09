"""
Testes do módulo de usuários.

Verificam roteamento, validações de schema e regras de negócio das rotas
sem depender de banco real nem de inspeção de código-fonte.
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from uuid import UUID
from unittest.mock import MagicMock

from app.routers.usuarios import router
from app.services.supabase_auth_service import SupabaseAuthError


def _montar_app(perfil: str, cliente_id: str | None = None):
    """
    Cria FastAPI isolado com router de usuários e dependências mockadas.

    Sobrepor get_usuario_atual propaga para exigir_perfil, pois este
    depende internamente de get_usuario_atual via Depends().
    """
    from app.core.auth import get_usuario_atual
    from app.core.database import get_db

    app = FastAPI()
    app.include_router(router)

    usuario_mock = MagicMock()
    usuario_mock.perfil = perfil
    usuario_mock.cliente_id = cliente_id
    usuario_mock.empresa_id = None

    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.all.return_value = []
    db_mock.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_usuario_atual] = lambda: usuario_mock
    app.dependency_overrides[get_db] = lambda: db_mock

    return TestClient(app, raise_server_exceptions=False), db_mock


# ── Roteamento ────────────────────────────────────────────────────────────────

def test_usuarios_usa_prefixo_versionado():
    """Todas as rotas de usuários devem usar o prefixo /api/v1/usuarios."""
    caminhos = [route.path for route in router.routes]  # type: ignore[attr-defined]

    assert "/api/v1/usuarios" in caminhos
    assert "/api/v1/usuarios/{usuario_id}" in caminhos
    assert "/api/v1/usuarios/{usuario_id}/resetar-senha" in caminhos
    assert not any(path.startswith("/api/usuarios") for path in caminhos)


def test_usuario_auth_id_nao_declara_fk_orm_para_auth_users():
    """
    auth.users pertence ao Supabase Auth e não está no metadata ORM da aplicação.
    Declarar essa FK no model causa NoReferencedTableError em commits de Usuario.
    """
    from app.models.usuario import Usuario

    coluna = Usuario.__table__.c.usuario_auth_id

    assert len(coluna.foreign_keys) == 0


# ── Listagem ──────────────────────────────────────────────────────────────────

def test_listagem_admin_ia16_retorna_200():
    """
    admin_ia16 lista usuários — resposta 200.
    Confirma que o filtro por cliente_id (não nulo) é aplicado via query ao DB.
    """
    client, db_mock = _montar_app("admin_ia16")
    response = client.get("/api/v1/usuarios")

    assert response.status_code == 200
    assert db_mock.query.return_value.filter.called, (
        "Esperado que a listagem admin_ia16 filtre usuários por cliente_id via query."
    )


def test_listagem_cliente_admin_filtra_por_proprio_cliente():
    """
    cliente_admin deve ver apenas usuários do próprio cliente (cliente_id).
    """
    cliente_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    client, db_mock = _montar_app("cliente_admin", cliente_id=cliente_id)
    response = client.get("/api/v1/usuarios")

    assert response.status_code == 200
    assert db_mock.query.return_value.filter.called


# ── Criação — validação de schema ─────────────────────────────────────────────

def test_criar_usuario_cliente_sem_cliente_id_retorna_422():
    """
    Pydantic deve rejeitar criação de cliente_operador sem cliente_id —
    a validação ocorre em UsuarioCreate antes do handler rodar (422).
    """
    client, _ = _montar_app("admin_ia16")
    response = client.post(
        "/api/v1/usuarios",
        json={
            "nome": "Operador Teste",
            "email": "operador@ia16.com.br",
            "perfil": "cliente_operador",
            # cliente_id ausente — schema deve rejeitar
            "senha_temporaria": "SenhaForte123",
        },
    )

    assert response.status_code == 422, (
        f"Esperado 422 (schema rejeita cliente_operador sem cliente_id), "
        f"mas recebeu {response.status_code}. Resposta: {response.json()}"
    )


def test_criar_admin_ia16_sem_cliente_id_e_aceito_pelo_schema():
    """
    Criação de admin_ia16 sem cliente_id é válida pelo schema —
    admin_ia16 não precisa de cliente_id.

    O teste verifica que a validação Pydantic passa (não retorna 422).
    O 502 ou 409 seguintes são erros externos (Supabase/DB), não de validação.
    """
    client, _ = _montar_app("admin_ia16")
    response = client.post(
        "/api/v1/usuarios",
        json={
            "nome": "Novo Admin",
            "email": "novoadmin@ia16.com.br",
            "perfil": "admin_ia16",
            # cliente_id ausente — permitido para admin_ia16
            "senha_temporaria": "SenhaForte123",
        },
    )

    # Schema não rejeitou (422 seria rejeição de validação)
    assert response.status_code != 422, (
        f"Schema não deve rejeitar admin_ia16 sem cliente_id. "
        f"Recebeu {response.status_code}: {response.json()}"
    )


# ── Criação — regras de negócio ───────────────────────────────────────────────

def test_cliente_admin_nao_pode_criar_admin_ia16():
    """
    cliente_admin tentando criar admin_ia16 deve receber 403 —
    regra verificada no handler antes de qualquer operação externa.
    """
    cliente_id = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    client, _ = _montar_app("cliente_admin", cliente_id=cliente_id)
    response = client.post(
        "/api/v1/usuarios",
        json={
            "nome": "Admin Não Permitido",
            "email": "nao@ia16.com.br",
            "perfil": "admin_ia16",
            "cliente_id": cliente_id,
            "senha_temporaria": "SenhaForte123",
        },
    )

    assert response.status_code == 403, (
        f"Esperado 403 (cliente_admin não pode criar admin_ia16), "
        f"mas recebeu {response.status_code}. Resposta: {response.json()}"
    )


def test_cliente_admin_nao_pode_criar_usuario_de_outro_cliente():
    """
    cliente_admin não pode criar usuário vinculado a outro cliente_id.
    """
    cliente_id_proprio = "cccccccc-cccc-cccc-cccc-cccccccccccc"
    cliente_id_outro = "dddddddd-dddd-dddd-dddd-dddddddddddd"

    client, _ = _montar_app("cliente_admin", cliente_id=cliente_id_proprio)
    response = client.post(
        "/api/v1/usuarios",
        json={
            "nome": "Usuário Outro Cliente",
            "email": "outro@empresa.com",
            "perfil": "cliente_operador",
            "cliente_id": cliente_id_outro,
            "senha_temporaria": "SenhaForte123",
        },
    )

    assert response.status_code == 403, (
        f"Esperado 403 (cliente_admin não pode criar usuário para outro cliente), "
        f"mas recebeu {response.status_code}. Resposta: {response.json()}"
    )


# ── Reset de senha ────────────────────────────────────────────────────────────

def test_resetar_senha_converte_falha_auth_em_502(monkeypatch):
    """
    Falha controlada no provedor de autenticação deve retornar 502,
    não 500 genérico para a tela.
    """
    import app.routers.usuarios as usuarios_router

    client, db_mock = _montar_app("admin_ia16")
    alvo = MagicMock()
    alvo.id = UUID("11111111-1111-1111-1111-111111111111")
    alvo.usuario_auth_id = UUID("22222222-2222-2222-2222-222222222222")
    alvo.cliente_id = UUID("33333333-3333-3333-3333-333333333333")
    alvo.empresa_id = None
    alvo.perfil = "cliente_operador"
    db_mock.query.return_value.filter.return_value.first.return_value = alvo

    def falhar_auth(*_args, **_kwargs):
        raise SupabaseAuthError("Falha controlada no Auth")

    monkeypatch.setattr(usuarios_router, "atualizar_senha_usuario_auth", falhar_auth)

    response = client.post(
        f"/api/v1/usuarios/{alvo.id}/resetar-senha",
        json={"senha_temporaria": "SenhaForte123"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Falha controlada no Auth"


def test_resetar_senha_converte_erro_inesperado_auth_em_502(monkeypatch):
    """
    Exceções inesperadas durante a troca de senha externa também devem
    virar resposta controlada para não quebrar o fluxo da aplicação.
    """
    import app.routers.usuarios as usuarios_router

    client, db_mock = _montar_app("admin_ia16")
    alvo = MagicMock()
    alvo.id = UUID("44444444-4444-4444-4444-444444444444")
    alvo.usuario_auth_id = UUID("55555555-5555-5555-5555-555555555555")
    alvo.cliente_id = UUID("66666666-6666-6666-6666-666666666666")
    alvo.empresa_id = None
    alvo.perfil = "cliente_operador"
    db_mock.query.return_value.filter.return_value.first.return_value = alvo

    def quebrar_auth(*_args, **_kwargs):
        raise RuntimeError("erro inesperado")

    monkeypatch.setattr(usuarios_router, "atualizar_senha_usuario_auth", quebrar_auth)

    response = client.post(
        f"/api/v1/usuarios/{alvo.id}/resetar-senha",
        json={"senha_temporaria": "SenhaForte123"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Não foi possível resetar a senha no provedor de autenticação."
