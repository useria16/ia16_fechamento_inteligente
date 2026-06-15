"""
Testes unitários do motor de conciliação (Sprint 6B v2).

Cobre explicitamente os 8 tipos de classificação:
  - match perfeito
  - divergência de data
  - divergência de valor
  - previsto não realizado
  - realizado não previsto
  - duplicidade no extrato
  - duplicidade no fluxo
  - pendente análise manual
"""
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock
import uuid

from app.services.motor_conciliacao_service import executar_motor


# ── Fixtures ──────────────────────────────────────────────────────────────────

@dataclass
class R:
    data_realizada: date
    descricao_realizada: str
    valor_realizado: Decimal
    tipo_movimento: str
    razao_social: str | None = None
    documento: str | None = None
    descricao_operacao: str = ""
    arquivo_id: str = "ext-001"
    linha_origem: int = 1
    metadados: dict = field(default_factory=dict)


@dataclass
class P:
    data_prevista: date
    descricao_prevista: str
    valor_previsto: Decimal
    tipo_movimento: str
    categoria: str = "geral"
    arquivo_id: str = "flx-001"
    linha_origem: int = 1
    coluna_origem: str = "D"
    metadados: dict = field(default_factory=dict)


EMPRESA_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
FECHAMENTO_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
ARQ_R = uuid.UUID("00000000-0000-0000-0000-000000000010")
ARQ_P = uuid.UUID("00000000-0000-0000-0000-000000000020")
DT = date(2024, 6, 10)


def _db():
    db = MagicMock()
    adicionados = []

    def add_side(obj):
        adicionados.append(obj)
        if hasattr(obj, "id") and obj.id is None:
            obj.id = uuid.uuid4()

    db.add = MagicMock(side_effect=add_side)
    db.flush = MagicMock()
    db.query.return_value.filter.return_value.delete = MagicMock(return_value=0)
    db._adicionados = adicionados
    return db


def _run(realizados, previstos):
    db = _db()
    r = [(ARQ_R, x) for x in realizados]
    p = [(ARQ_P, x) for x in previstos]
    res = executar_motor(FECHAMENTO_ID, EMPRESA_ID, r, p, db)
    itens = [o for o in db._adicionados if hasattr(o, "tipo_item")]
    tipos = [i.tipo_item for i in itens]
    return res, itens, tipos


# ── Match perfeito ─────────────────────────────────────────────────────────────

class TestMatchPerfeito:
    def test_mesma_data_mesmo_valor_concilia(self):
        res, itens, tipos = _run(
            [R(DT, "PGTO X", Decimal("1000"), "saida", razao_social="Empresa SA")],
            [P(DT, "Pagamento X", Decimal("1000"), "saida")],
        )
        assert res.quantidade_conciliados == 1
        assert "conciliado" in tipos

    def test_contadores_valor(self):
        res, _, _ = _run(
            [R(DT, "A", Decimal("500"), "saida")],
            [P(DT, "A", Decimal("500"), "saida")],
        )
        assert res.valor_total_conciliado == Decimal("500")
        assert res.valor_total_divergente == Decimal("0")

    def test_tipo_movimento_diferente_nao_concilia(self):
        res, _, tipos = _run(
            [R(DT, "A", Decimal("500"), "saida")],
            [P(DT, "A", Decimal("500"), "entrada")],
        )
        assert res.quantidade_conciliados == 0
        assert "conciliado" not in tipos


# ── Divergência de data ────────────────────────────────────────────────────────

class TestDivergenciaData:
    def test_1_dia_gera_divergencia_data(self):
        _, itens, tipos = _run(
            [R(DT, "BOLETO X", Decimal("320"), "saida")],
            [P(DT - timedelta(days=1), "Internet X", Decimal("320"), "saida")],
        )
        assert "divergencia_data" in tipos

    def test_3_dias_gera_divergencia_data(self):
        _, itens, tipos = _run(
            [R(DT, "PGTO X", Decimal("780"), "saida")],
            [P(DT - timedelta(days=3), "Aluguel X", Decimal("780"), "saida")],
        )
        assert "divergencia_data" in tipos

    def test_divergencia_data_nao_e_conciliado(self):
        res, _, _ = _run(
            [R(DT, "A", Decimal("500"), "saida")],
            [P(DT + timedelta(days=2), "A", Decimal("500"), "saida")],
        )
        assert res.quantidade_conciliados == 0
        assert res.quantidade_divergentes == 1

    def test_4_dias_nao_casa(self):
        res, _, tipos = _run(
            [R(DT, "A", Decimal("500"), "saida")],
            [P(DT + timedelta(days=4), "A", Decimal("500"), "saida")],
        )
        assert "divergencia_data" not in tipos

    def test_prioridade_match_perfeito_sobre_divergencia_data(self):
        """Quando há previsto com mesma data e outro com data próxima, casa o perfeito."""
        _, itens, tipos = _run(
            [R(DT, "A", Decimal("500"), "saida")],
            [
                P(DT + timedelta(days=2), "A", Decimal("500"), "saida"),
                P(DT, "A", Decimal("500"), "saida"),
            ],
        )
        assert tipos.count("conciliado") == 1
        assert tipos.count("divergencia_data") == 0


# ── Divergência de valor ───────────────────────────────────────────────────────

class TestDivergenciaValor:
    def test_valor_diferente_mesma_data_gera_divergencia_valor(self):
        _, _, tipos = _run(
            [R(DT, "PGTO RH", Decimal("3400"), "saida")],
            [P(DT, "RH Pgto", Decimal("3600"), "saida")],
        )
        assert "divergencia_valor" in tipos

    def test_diferenca_acima_30_pct_nao_casa(self):
        """R$950 vs R$400 = 57% de diferença — não deve casar como divergencia_valor."""
        # razao_social="AUTONOMO" → realizado_nao_previsto (status=divergente)
        res, _, tipos = _run(
            [R(DT, "PIX A", Decimal("950"), "saida", razao_social="AUTONOMO")],
            [P(DT, "Pgto B", Decimal("400"), "saida")],
        )
        assert "divergencia_valor" not in tipos
        assert res.quantidade_divergentes == 2  # realizado_nao_previsto + previsto_nao_realizado

    def test_nao_reclassifica_como_match_perfeito(self):
        res, _, _ = _run(
            [R(DT, "A", Decimal("3400"), "saida")],
            [P(DT, "A", Decimal("3600"), "saida")],
        )
        assert res.quantidade_conciliados == 0
        assert res.quantidade_divergentes == 1


# ── Previsto não realizado ─────────────────────────────────────────────────────

class TestPrevistNaoRealizado:
    def test_previsto_sem_correspondencia(self):
        _, _, tipos = _run(
            [],
            [P(DT, "Freelancer X", Decimal("400"), "saida")],
        )
        assert "previsto_nao_realizado" in tipos

    def test_status_divergente(self):
        res, _, _ = _run(
            [],
            [P(DT, "Freelancer X", Decimal("400"), "saida")],
        )
        assert res.quantidade_divergentes == 1
        assert res.quantidade_pendentes == 0


# ── Realizado não previsto ────────────────────────────────────────────────────

class TestRealizadoNaoPrevisto:
    def test_realizado_com_razao_social(self):
        """Tem razao_social preenchida → realizado_nao_previsto, não pendente."""
        _, _, tipos = _run(
            [R(DT, "PIX AUTONOMO", Decimal("950"), "saida", razao_social="AUTONOMO")],
            [],
        )
        assert "realizado_nao_previsto" in tipos

    def test_status_divergente(self):
        res, _, _ = _run(
            [R(DT, "PIX X", Decimal("500"), "saida", razao_social="Empresa SA")],
            [],
        )
        assert res.quantidade_divergentes == 1
        assert res.quantidade_pendentes == 0


# ── Duplicidade no extrato ────────────────────────────────────────────────────

class TestDuplicidadeExtrato:
    def test_dois_identicos_gera_uma_duplicidade(self):
        _, _, tipos = _run(
            [
                R(DT, "PIX X", Decimal("200"), "saida"),
                R(DT, "PIX X", Decimal("200"), "saida"),  # duplicado
            ],
            [],
        )
        assert tipos.count("duplicidade_extrato") == 1

    def test_original_continua_para_matching(self):
        """O original não é removido — participa da conciliação normalmente."""
        res, _, tipos = _run(
            [
                R(DT, "PIX X", Decimal("200"), "saida"),
                R(DT, "PIX X", Decimal("200"), "saida"),
            ],
            [P(DT, "Limpeza", Decimal("200"), "saida")],
        )
        assert "conciliado" in tipos
        assert "duplicidade_extrato" in tipos
        assert res.quantidade_conciliados == 1

    def test_tres_identicos_geram_duas_duplicidades(self):
        _, _, tipos = _run(
            [
                R(DT, "A", Decimal("100"), "saida"),
                R(DT, "A", Decimal("100"), "saida"),
                R(DT, "A", Decimal("100"), "saida"),
            ],
            [],
        )
        assert tipos.count("duplicidade_extrato") == 2


# ── Duplicidade no fluxo ──────────────────────────────────────────────────────

class TestDuplicidadeFluxo:
    def test_dois_identicos_gera_uma_duplicidade(self):
        _, _, tipos = _run(
            [],
            [
                P(DT, "Software X", Decimal("650"), "saida"),
                P(DT, "Software X", Decimal("650"), "saida"),
            ],
        )
        assert tipos.count("duplicidade_fluxo") == 1

    def test_original_continua_para_matching(self):
        res, _, tipos = _run(
            [R(DT, "BOLETO X", Decimal("650"), "saida")],
            [
                P(DT, "Software X", Decimal("650"), "saida"),
                P(DT, "Software X", Decimal("650"), "saida"),
            ],
        )
        assert "conciliado" in tipos
        assert "duplicidade_fluxo" in tipos
        assert res.quantidade_conciliados == 1


# ── Pendente análise manual ───────────────────────────────────────────────────

class TestPendenteAnaliseManual:
    def test_sem_razao_social_e_sem_documento(self):
        """razao_social=None e documento=None → pendente_analise_manual."""
        res, _, tipos = _run(
            [R(DT, "TED SEM IDENT", Decimal("3700"), "entrada",
               razao_social=None, documento=None)],
            [],
        )
        assert "pendente_analise_manual" in tipos
        assert res.quantidade_pendentes == 1
        assert res.quantidade_divergentes == 0

    def test_razao_social_s_identificacao(self):
        """'TRANSF S/IDENTIFICACAO' no campo razao_social → pendente."""
        res, _, tipos = _run(
            [R(DT, "TED RECEBIDA", Decimal("3700"), "entrada",
               razao_social="TRANSF S/IDENTIFICACAO", documento=None)],
            [],
        )
        assert "pendente_analise_manual" in tipos
        assert res.quantidade_pendentes == 1

    def test_com_razao_social_genuina_nao_e_pendente(self):
        """Com razao_social real → realizado_nao_previsto, não pendente."""
        res, _, tipos = _run(
            [R(DT, "PIX X", Decimal("500"), "saida",
               razao_social="Empresa SA", documento=None)],
            [],
        )
        assert "pendente_analise_manual" not in tipos
        assert res.quantidade_pendentes == 0

    def test_com_documento_nao_e_pendente(self):
        res, _, tipos = _run(
            [R(DT, "BOLETO X", Decimal("500"), "saida",
               razao_social=None, documento="12345")],
            [],
        )
        assert "pendente_analise_manual" not in tipos

    def test_documento_placeholder_zeros_e_pendente(self):
        """CPF/CNPJ '00.000.000/0000-00' é placeholder — conta como sem documento."""
        res, _, tipos = _run(
            [R(DT, "TED RECEBIDA", Decimal("3700"), "entrada",
               razao_social="CENARIO_10 TRANSF S/IDENTIFICACAO",
               documento="00.000.000/0000-00")],
            [],
        )
        assert "pendente_analise_manual" in tipos


# ── Contadores e semântica ─────────────────────────────────────────────────────

class TestContadores:
    def test_semantica_completa(self):
        """
        quantidade_conciliados  = conciliado
        quantidade_divergentes  = divergencia_data + divergencia_valor +
                                  realizado_nao_previsto + previsto_nao_realizado +
                                  duplicidade_extrato + duplicidade_fluxo
        quantidade_pendentes    = pendente_analise_manual
        """
        res, _, tipos = _run(
            [
                R(DT, "A", Decimal("100"), "saida"),                     # → conciliado
                R(DT, "B", Decimal("200"), "saida"),                     # → divergencia_data
                R(DT, "C", Decimal("300"), "saida", razao_social="X"),   # → realizado_nao_previsto
                R(DT, "D", Decimal("50"), "saida",
                  razao_social=None, documento=None),                    # → pendente_analise_manual
            ],
            [
                P(DT, "A", Decimal("100"), "saida"),
                P(DT + timedelta(days=2), "B", Decimal("200"), "saida"),
            ],
        )
        assert res.quantidade_conciliados == 1
        assert res.quantidade_divergentes == 2  # divergencia_data + realizado_nao_previsto
        assert res.quantidade_pendentes == 1

    def test_reprocessamento_limpa_anteriores(self):
        """Motor chama DELETE em divergencias e itens antes de re-gravar."""
        db = _db()
        executar_motor(
            FECHAMENTO_ID, EMPRESA_ID,
            [(ARQ_R, R(DT, "X", Decimal("100"), "saida"))],
            [],
            db,
        )
        assert db.query.return_value.filter.return_value.delete.call_count == 2

    def test_previsto_nao_usa_dois_realizados(self):
        """O mesmo previsto não pode ser usado por dois realizados."""
        res, _, tipos = _run(
            [
                R(DT, "A", Decimal("500"), "saida"),
                R(DT, "A", Decimal("500"), "saida"),
            ],
            [P(DT, "A", Decimal("500"), "saida")],
        )
        assert res.quantidade_conciliados == 1
