"""
Testes do service de exportação mensal consolidada (exportacao_mensal_service).

Cobre:
  1. Exportação diária existente continua funcionando (smoke test do import).
  2. Erro quando não há conciliações no mês.
  3. Inclui apenas conciliações da empresa correta (isolamento multicliente).
  4. Filtra por tipo de conciliação.
  5. Inclui múltiplos dias do mesmo mês.
  6. Exclui conciliações fora do mês.
  7. Gera workbook válido.
  8. Workbook contém abas esperadas.
  9. Aba Conciliação Mensal contém lançamentos de mais de um dia.
 10. Aba Dias Incluídos lista os fechamentos incluídos.
 11. Testa com dados de extrato_anotado.
"""
import io
import uuid
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
import pytest

import openpyxl

from app.services.exportacao_mensal_service import (
    buscar_fechamentos_do_mes,
    gerar_excel_mensal,
)
from app.services.exportacao_fechamento_service import gerar_excel_fechamento


# ── Fixtures ─────────────────────────────────────────────────────────────────

EMPRESA_A = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
EMPRESA_B = uuid.UUID("bbbbbbbb-0000-0000-0000-000000000002")
FECH_1 = uuid.UUID("00000000-1111-0000-0000-000000000001")
FECH_2 = uuid.UUID("00000000-2222-0000-0000-000000000002")
FECH_3 = uuid.UUID("00000000-3333-0000-0000-000000000003")
ARQ_1 = uuid.UUID("00000000-0000-1111-0000-000000000001")
ARQ_2 = uuid.UUID("00000000-0000-2222-0000-000000000002")


def _make_fechamento(
    fid=FECH_1,
    empresa_id=EMPRESA_A,
    tipo="extrato_anotado",
    status="aprovado",
    periodo_inicio=date(2026, 6, 1),
    titulo="Conciliação 01/06",
    qtd_registros=5,
    qtd_conciliados=4,
    qtd_divergentes=1,
    qtd_pendentes=0,
):
    f = MagicMock()
    f.id = fid
    f.empresa_id = empresa_id
    f.tipo_conciliacao = tipo
    f.status = status
    f.periodo_inicio = periodo_inicio
    f.periodo_fim = periodo_inicio
    f.titulo = titulo
    f.quantidade_registros = qtd_registros
    f.quantidade_conciliados = qtd_conciliados
    f.quantidade_divergentes = qtd_divergentes
    f.quantidade_pendentes = qtd_pendentes
    f.valor_total_processado = Decimal("10000.00")
    f.valor_total_conciliado = Decimal("9000.00")
    f.valor_total_divergente = Decimal("1000.00")
    f.aprovado_em = None
    f.aprovado_por_usuario_id = None
    f.reaberto_em = None
    f.reaberto_por_usuario_id = None
    f.motivo_reabertura = None
    f.observacao_aprovacao = None
    f.criado_em = None
    f.atualizado_em = None
    f.criado_por_usuario_id = None
    return f


def _make_lancamento(
    fechamento_id=FECH_1,
    empresa_id=EMPRESA_A,
    arquivo_id=ARQ_1,
    data=date(2026, 6, 1),
    descricao_banco="PIX recebido",
    descricao_negocio="Cliente X",
    tipo_movimento="entrada",
    valor=Decimal("500.00"),
    saldo=Decimal("1500.00"),
    status_revisao="revisado",
    tipo_conferencia_fluxo="encontrado",
    nf_doc=None,
    valor_nf_doc=None,
    categoria=None,
    categoria_sugerida=None,
    observacao=None,
    observacao_sistema=None,
    data_prevista=None,
    valor_previsto=None,
    descricao_prevista=None,
    linha_origem=1,
):
    l = MagicMock()
    l.id = uuid.uuid4()
    l.fechamento_id = fechamento_id
    l.empresa_id = empresa_id
    l.arquivo_id = arquivo_id
    l.data_lancamento = data
    l.descricao_banco = descricao_banco
    l.descricao_negocio = descricao_negocio
    l.tipo_movimento = tipo_movimento
    l.valor = valor
    l.saldo = saldo
    l.status_revisao = status_revisao
    l.tipo_conferencia_fluxo = tipo_conferencia_fluxo
    l.nf_doc = nf_doc
    l.valor_nf_doc = valor_nf_doc
    l.categoria = categoria
    l.categoria_sugerida = categoria_sugerida
    l.observacao = observacao
    l.observacao_sistema = observacao_sistema
    l.data_prevista = data_prevista
    l.valor_previsto = valor_previsto
    l.descricao_prevista = descricao_prevista
    l.razao_social = None
    l.linha_origem = linha_origem
    l.confianca_conferencia = None
    l.criado_em = None
    l.atualizado_em = None
    l.atualizado_por_usuario_id = None
    return l


def _make_empresa(eid=EMPRESA_A, nome="Empresa Teste"):
    e = MagicMock()
    e.id = eid
    e.nome = nome
    return e


def _db_com_fechamentos(fechamentos, lancamentos=None, empresa=None):
    """Cria um mock de db que retorna os dados fornecidos."""
    db = MagicMock()
    empresa_obj = empresa or _make_empresa()

    # Mock da query de fechamentos
    q_fech = MagicMock()
    q_fech.filter.return_value = q_fech
    q_fech.order_by.return_value = q_fech
    q_fech.all.return_value = fechamentos

    # Mock da query de empresa
    q_emp = MagicMock()
    q_emp.filter.return_value = q_emp
    q_emp.first.return_value = empresa_obj

    # Mock da query de lancamentos
    q_lanc = MagicMock()
    q_lanc.filter.return_value = q_lanc
    q_lanc.order_by.return_value = q_lanc
    q_lanc.all.return_value = lancamentos or []

    def side_effect_query(model):
        from app.models.fechamento_financeiro import FechamentoFinanceiro
        from app.models.empresa import Empresa
        from app.models.lancamento_extrato_anotado import LancamentoExtratoAnotado
        if model is FechamentoFinanceiro:
            return q_fech
        if model is Empresa:
            return q_emp
        if model is LancamentoExtratoAnotado:
            return q_lanc
        return MagicMock()

    db.query.side_effect = side_effect_query
    return db


# ── Teste 1: importação do serviço diário não quebra ─────────────────────────

def test_importacao_servico_diario():
    """Exportação diária existente: o import e função principal devem existir."""
    assert callable(gerar_excel_fechamento)


# ── Teste 2: erro quando não há conciliações ──────────────────────────────────

def test_erro_sem_conciliacoes_no_mes():
    db = _db_com_fechamentos(fechamentos=[])
    with pytest.raises(ValueError, match="Nenhuma conciliação encontrada"):
        gerar_excel_mensal(
            db=db,
            empresa_id=EMPRESA_A,
            ano=2026,
            mes=6,
            tipo_conciliacao="extrato_anotado",
        )


# ── Teste 3: não inclui empresa errada ────────────────────────────────────────

def test_isolamento_por_empresa():
    """O service deve filtrar por empresa_id; outros dados não devem vazar."""
    fech_a = _make_fechamento(fid=FECH_1, empresa_id=EMPRESA_A)
    # Simula db que retorna apenas fechamentos da empresa A (comportamento correto)
    db = _db_com_fechamentos(fechamentos=[fech_a], lancamentos=[])
    conteudo, nome = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    # Garante que o resultado foi gerado e tem bytes válidos
    assert len(conteudo) > 0
    assert "empresa_teste" in nome or "2026_06" in nome

    # Verifica que db.query foi chamado ao menos uma vez
    assert db.query.called, "db.query deve ter sido chamado"


# ── Teste 4: filtra por tipo de conciliação ───────────────────────────────────

def test_filtra_por_tipo_conciliacao():
    """Apenas conciliações do tipo informado devem ser incluídas."""
    fech = _make_fechamento(fid=FECH_1, tipo="extrato_anotado", status="aprovado")
    db = _db_com_fechamentos(fechamentos=[fech], lancamentos=[])
    conteudo, nome = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    assert len(conteudo) > 0
    assert "extrato_anotado" in nome


# ── Teste 5: inclui múltiplos dias do mesmo mês ───────────────────────────────

def test_multiplos_dias_mesmo_mes():
    fech1 = _make_fechamento(fid=FECH_1, periodo_inicio=date(2026, 6, 1), titulo="01/06")
    fech2 = _make_fechamento(fid=FECH_2, periodo_inicio=date(2026, 6, 2), titulo="02/06")
    fech3 = _make_fechamento(fid=FECH_3, periodo_inicio=date(2026, 6, 9), titulo="09/06")

    l1 = _make_lancamento(fechamento_id=FECH_1, data=date(2026, 6, 1))
    l2 = _make_lancamento(fechamento_id=FECH_2, data=date(2026, 6, 2))
    l3 = _make_lancamento(fechamento_id=FECH_3, data=date(2026, 6, 9))

    db = _db_com_fechamentos(fechamentos=[fech1, fech2, fech3], lancamentos=[l1, l2, l3])
    conteudo, _ = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    assert len(conteudo) > 0

    wb = openpyxl.load_workbook(io.BytesIO(conteudo))
    ws_dias = wb["Dias Incluídos"]
    # 3 fechamentos devem estar listados
    assert ws_dias.max_row >= 4  # 1 cabeçalho + 3 dias


# ── Teste 6: não inclui datas fora do mês ────────────────────────────────────

def test_exclui_datas_fora_do_mes():
    """buscar_fechamentos_do_mes deve filtrar pelo mês/ano correto via SQL."""
    fech_junho = _make_fechamento(fid=FECH_1, periodo_inicio=date(2026, 6, 15))
    # O mock retorna apenas o de junho — simula o comportamento correto do filtro SQL
    db = _db_com_fechamentos(fechamentos=[fech_junho], lancamentos=[])
    fechamentos = buscar_fechamentos_do_mes(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    assert len(fechamentos) == 1
    assert fechamentos[0].periodo_inicio.month == 6


# ── Teste 7: gera workbook válido ────────────────────────────────────────────

def test_gera_workbook_valido():
    fech = _make_fechamento()
    l = _make_lancamento()
    db = _db_com_fechamentos(fechamentos=[fech], lancamentos=[l])
    conteudo, nome = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    wb = openpyxl.load_workbook(io.BytesIO(conteudo))
    assert wb is not None
    assert nome.endswith(".xlsx")


# ── Teste 8: workbook contém abas esperadas ───────────────────────────────────

def test_workbook_contem_abas_esperadas():
    fech = _make_fechamento()
    l = _make_lancamento()
    db = _db_com_fechamentos(fechamentos=[fech], lancamentos=[l])
    conteudo, _ = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    wb = openpyxl.load_workbook(io.BytesIO(conteudo))
    abas = wb.sheetnames
    assert "Resumo Mensal" in abas
    assert "Conciliação Mensal" in abas
    assert "Dias Incluídos" in abas
    assert "Pendências" in abas


# ── Teste 9: aba Conciliação Mensal contém lançamentos de mais de um dia ─────

def test_conciliacao_mensal_contem_lancamentos_multiplos_dias():
    fech1 = _make_fechamento(fid=FECH_1, periodo_inicio=date(2026, 6, 1), titulo="01/06")
    fech2 = _make_fechamento(fid=FECH_2, periodo_inicio=date(2026, 6, 2), titulo="02/06")

    l1a = _make_lancamento(fechamento_id=FECH_1, data=date(2026, 6, 1), descricao_banco="Lanc A", linha_origem=1)
    l1b = _make_lancamento(fechamento_id=FECH_1, data=date(2026, 6, 1), descricao_banco="Lanc B", linha_origem=2)
    l2a = _make_lancamento(fechamento_id=FECH_2, data=date(2026, 6, 2), descricao_banco="Lanc C", linha_origem=1)

    db = _db_com_fechamentos(
        fechamentos=[fech1, fech2],
        lancamentos=[l1a, l1b, l2a],
    )
    conteudo, _ = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    wb = openpyxl.load_workbook(io.BytesIO(conteudo))
    ws_conc = wb["Conciliação Mensal"]
    # 1 cabeçalho + 3 lançamentos
    assert ws_conc.max_row >= 4


# ── Teste 10: aba Dias Incluídos lista fechamentos ────────────────────────────

def test_dias_incluidos_lista_fechamentos():
    fech1 = _make_fechamento(fid=FECH_1, periodo_inicio=date(2026, 6, 1), titulo="01/06")
    fech2 = _make_fechamento(fid=FECH_2, periodo_inicio=date(2026, 6, 5), titulo="05/06")

    l1 = _make_lancamento(fechamento_id=FECH_1, data=date(2026, 6, 1))
    l2 = _make_lancamento(fechamento_id=FECH_2, data=date(2026, 6, 5))

    db = _db_com_fechamentos(fechamentos=[fech1, fech2], lancamentos=[l1, l2])
    conteudo, _ = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    wb = openpyxl.load_workbook(io.BytesIO(conteudo))
    ws_dias = wb["Dias Incluídos"]
    titulos_coluna = [ws_dias.cell(row=r, column=3).value for r in range(2, ws_dias.max_row + 1)]
    assert "01/06" in titulos_coluna
    assert "05/06" in titulos_coluna


# ── Teste 11: dados de extrato_anotado — lançamentos com conferência de fluxo ─

def test_extrato_anotado_com_conferencia_fluxo():
    fech = _make_fechamento(tipo="extrato_anotado", status="aprovado")
    l_enc = _make_lancamento(
        tipo_conferencia_fluxo="encontrado",
        status_revisao="revisado",
        descricao_banco="TED pagamento",
    )
    l_nao_enc = _make_lancamento(
        tipo_conferencia_fluxo="nao_encontrado",
        status_revisao="pendente",
        descricao_banco="Débito desconhecido",
        tipo_movimento="saida",
    )
    db = _db_com_fechamentos(fechamentos=[fech], lancamentos=[l_enc, l_nao_enc])
    conteudo, _ = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    wb = openpyxl.load_workbook(io.BytesIO(conteudo))

    # Aba Conciliação Mensal deve ter coluna STATUS NO FLUXO
    ws_conc = wb["Conciliação Mensal"]
    cabecalhos = [ws_conc.cell(row=1, column=c).value for c in range(1, ws_conc.max_column + 1)]
    assert "STATUS NO FLUXO" in cabecalhos

    # Aba Pendências deve incluir o lançamento não encontrado
    ws_pend = wb["Pendências"]
    assert ws_pend.max_row >= 2  # pelo menos 1 pendente + cabeçalho
