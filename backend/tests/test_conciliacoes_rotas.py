"""
Testes de roteamento do router de conciliações.

Verifica que rotas estáticas como /exportar-mensal são resolvidas antes
da rota dinâmica /{conciliacao_id}, conforme exigido pelo FastAPI/Starlette.

A falha destes testes indica que a ordem das rotas no router está errada
e /exportar-mensal seria erroneamente tratada como um conciliacao_id.
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.routers.conciliacoes import router


def _app_com_mocks():
    """
    Cria uma instância FastAPI isolada com o router de conciliações e
    dependências mockadas para que o TestClient possa exercitar as rotas
    sem banco de dados real.
    """
    from app.core.auth import get_usuario_atual
    from app.core.database import get_db

    app = FastAPI()
    app.include_router(router)

    usuario_mock = MagicMock()
    usuario_mock.perfil = "cliente_admin"
    usuario_mock.empresa_id = "00000000-0000-0000-0000-000000000001"
    usuario_mock.id = "00000000-0000-0000-0000-000000000099"
    usuario_mock.email = "teste@ia16.com.br"

    db_mock = MagicMock()

    app.dependency_overrides[get_usuario_atual] = lambda: usuario_mock
    app.dependency_overrides[get_db] = lambda: db_mock

    return app, db_mock


def test_exportar_mensal_nao_e_capturado_por_rota_dinamica():
    """
    Garante que GET /api/v1/conciliacoes/exportar-mensal chama
    exportar_consolidado_mensal e NÃO obter_conciliacao.

    Se a rota dinâmica capturar 'exportar-mensal' como conciliacao_id,
    o banco seria consultado com esse valor e o teste falharia com 404
    retornando a mensagem de 'Conciliação não encontrada' em vez do
    erro esperado de parâmetros ausentes (422) ou empresa não encontrada.
    """
    app, db_mock = _app_com_mocks()

    # Simula empresa não encontrada — garante que o request chegou ao endpoint correto
    db_mock.query.return_value.filter.return_value.first.return_value = None

    client = TestClient(app, raise_server_exceptions=False)

    # Sem parâmetros obrigatórios: FastAPI retorna 422 (validação de query params)
    # Se a rota dinâmica capturasse, retornaria 404 com 'Conciliação não encontrada'
    response = client.get("/api/v1/conciliacoes/exportar-mensal")

    # 422 = FastAPI validou os query params do endpoint correto (ano, mes, tipo_conciliacao ausentes)
    # 404 com mensagem específica = endpoint errado (obter_conciliacao) foi chamado
    assert response.status_code == 422, (
        f"Esperado 422 (query params ausentes no endpoint mensal), "
        f"mas recebeu {response.status_code}. "
        f"Isso indica que a rota dinâmica '{{conciliacao_id}}' capturou 'exportar-mensal'. "
        f"Corrija a ordem das rotas no router de conciliações."
    )

    corpo = response.json()
    # Confirma que é erro de validação de query param (FastAPI padrão)
    assert "detail" in corpo


def test_exportar_mensal_com_params_chega_ao_endpoint_correto():
    """
    Com os parâmetros obrigatórios presentes, a requisição deve ser roteada
    para exportar_consolidado_mensal. O endpoint tentará resolver a empresa
    e retornará 404 (empresa não encontrada) — nunca o erro de
    'Conciliação não encontrada' da rota dinâmica.
    """
    app, db_mock = _app_com_mocks()

    # Empresa não encontrada — simula DB sem dados
    db_mock.query.return_value.filter.return_value.first.return_value = None

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get(
        "/api/v1/conciliacoes/exportar-mensal",
        params={"ano": 2026, "mes": 6, "tipo_conciliacao": "extrato_anotado"},
    )

    # Deve chegar ao endpoint mensal e falhar com 404 (empresa não encontrada)
    # Se retornar 404 com 'Conciliação não encontrada', a rota dinâmica captou
    assert response.status_code == 404
    corpo = response.json()
    detail = corpo.get("detail", {})
    erro = detail.get("erro", {}) if isinstance(detail, dict) else {}
    assert erro.get("codigo") == "EMPRESA_NAO_ENCONTRADA", (
        f"Esperado código EMPRESA_NAO_ENCONTRADA, recebeu: {corpo}. "
        f"Se recebeu 'FECHAMENTO_NAO_ENCONTRADO', a rota dinâmica capturou 'exportar-mensal'."
    )


def test_exportar_periodo_nao_e_capturado_por_rota_dinamica():
    """
    Garante que GET /api/v1/conciliacoes/exportar-periodo chama
    exportar_consolidado_periodo e NÃO obter_conciliacao.
    """
    app, db_mock = _app_com_mocks()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/api/v1/conciliacoes/exportar-periodo")

    assert response.status_code == 422, (
        f"Esperado 422 (query params ausentes no endpoint por período), "
        f"mas recebeu {response.status_code}. "
        f"Isso indica que a rota dinâmica '{{conciliacao_id}}' capturou 'exportar-periodo'."
    )


def test_exportar_periodo_com_params_chega_ao_endpoint_correto():
    """
    Com os parâmetros obrigatórios presentes, a requisição deve ser roteada
    para exportar_consolidado_periodo. O endpoint tentará resolver a empresa
    e retornará 404 (empresa não encontrada), não erro da rota dinâmica.
    """
    app, db_mock = _app_com_mocks()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get(
        "/api/v1/conciliacoes/exportar-periodo",
        params={
            "data_inicio": "2026-06-15",
            "data_fim": "2026-07-15",
            "tipo_conciliacao": "extrato_anotado",
        },
    )

    assert response.status_code == 404
    corpo = response.json()
    detail = corpo.get("detail", {})
    erro = detail.get("erro", {}) if isinstance(detail, dict) else {}
    assert erro.get("codigo") == "EMPRESA_NAO_ENCONTRADA", (
        f"Esperado código EMPRESA_NAO_ENCONTRADA, recebeu: {corpo}. "
        f"Se recebeu 'FECHAMENTO_NAO_ENCONTRADO', a rota dinâmica capturou 'exportar-periodo'."
    )


def test_exportar_periodo_rejeita_data_inicial_maior_que_final():
    app, db_mock = _app_com_mocks()
    db_mock.query.return_value.filter.return_value.first.return_value = MagicMock()

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get(
        "/api/v1/conciliacoes/exportar-periodo",
        params={
            "data_inicio": "2026-07-15",
            "data_fim": "2026-06-15",
            "tipo_conciliacao": "extrato_anotado",
        },
    )

    assert response.status_code == 400
    corpo = response.json()
    detail = corpo.get("detail", {})
    erro = detail.get("erro", {}) if isinstance(detail, dict) else {}
    assert erro.get("codigo") == "PERIODO_INVALIDO"


def test_rota_dinamica_ainda_funciona_com_uuid_valido():
    """
    Garante que a rota /{conciliacao_id} continua sendo atingida por UUID.
    Um UUID nunca deve ser tratado como /exportar-mensal (rota estática).

    Verifica a ausência do código de erro EMPRESA_NAO_ENCONTRADA (exclusivo
    do endpoint mensal) para confirmar que o endpoint correto foi chamado.
    """
    app, db_mock = _app_com_mocks()

    # Configura mock para o join usado em obter_conciliacao
    db_mock.query.return_value.join.return_value.filter.return_value.first.return_value = None

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/api/v1/conciliacoes/00000000-0000-0000-0000-000000000001")

    # Não deve retornar 422 (que indicaria que virou /exportar-mensal e faltaram query params)
    assert response.status_code != 422, (
        "Recebeu 422 ao acessar /{conciliacao_id} com UUID — indica roteamento incorreto."
    )

    # Não deve conter o código de erro exclusivo do endpoint mensal
    corpo = response.json()
    detail = corpo.get("detail", {})
    if isinstance(detail, dict):
        erro_codigo = detail.get("erro", {}).get("codigo", "")
        assert erro_codigo != "EMPRESA_NAO_ENCONTRADA", (
            "Recebeu EMPRESA_NAO_ENCONTRADA — indica que a rota mensal foi chamada em vez de obter_conciliacao."
        )


def test_ordem_das_rotas_no_router():
    """
    Inspeção direta da ordem de registro das rotas no router.
    Verifica que /exportar-mensal está registrada antes de /{conciliacao_id}.

    Os paths incluem o prefixo completo do router (ex: /api/v1/conciliacoes/...).
    """
    caminhos = [route.path for route in router.routes]  # type: ignore[attr-defined]

    # Busca por sufixo para não depender do prefixo exato
    idx_mensal = next(
        (i for i, p in enumerate(caminhos) if p.endswith("/exportar-mensal")),
        None,
    )
    assert idx_mensal is not None, (
        f"Rota /exportar-mensal não encontrada no router. Rotas registradas: {caminhos}"
    )

    idx_periodo = next(
        (i for i, p in enumerate(caminhos) if p.endswith("/exportar-periodo")),
        None,
    )
    assert idx_periodo is not None, (
        f"Rota /exportar-periodo não encontrada no router. Rotas registradas: {caminhos}"
    )

    idx_dinamica = next(
        (i for i, p in enumerate(caminhos) if p.endswith("/{conciliacao_id}")),
        None,
    )
    assert idx_dinamica is not None, (
        f"Rota /{{conciliacao_id}} não encontrada no router. Rotas registradas: {caminhos}"
    )

    assert idx_mensal < idx_dinamica, (
        f"/exportar-mensal está no índice {idx_mensal}, "
        f"mas /{{conciliacao_id}} está no índice {idx_dinamica}. "
        f"A rota estática deve ser registrada ANTES da dinâmica."
    )

    assert idx_periodo < idx_dinamica, (
        f"/exportar-periodo está no índice {idx_periodo}, "
        f"mas /{{conciliacao_id}} está no índice {idx_dinamica}. "
        f"A rota estática deve ser registrada ANTES da dinâmica."
    )
