"""
Testes de roteamento do módulo de empresas.

O frontend deve consumir empresas pelo contrato versionado /api/v1/empresas.
"""

from app.routers.empresas import router


def test_empresas_usa_prefixo_versionado():
    caminhos = [route.path for route in router.routes]  # type: ignore[attr-defined]

    assert "/api/v1/empresas" in caminhos
    assert "/api/v1/empresas/{empresa_id}" in caminhos
    assert not any(path.startswith("/api/empresas") for path in caminhos)
