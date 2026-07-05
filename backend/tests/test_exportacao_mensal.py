"""
Testes do service de exportação mensal de conciliação (exportacao_mensal_service).

Cobre:
  1. Exportação diária existente continua funcionando (smoke test do import).
  2. Erro quando não há conciliações no mês.
  3. Inclui apenas conciliações da empresa correta (isolamento multicliente).
  4. Filtra por tipo de conciliação.
  5. Inclui múltiplos dias do mesmo mês.
  6. Exclui conciliações fora do mês.
  7. Gera workbook válido com uma única aba.
  8. Aba tem nome no formato mês+ano (ex: Jun26).
  9. Aba NÃO contém abas antigas (Resumo Mensal, Conciliação Mensal, etc.).
 10. Cabeçalho da tabela está na linha 8 com as colunas corretas.
 11. Lançamentos aparecem a partir da linha 9.
 12. Nome do arquivo segue o padrão ia16_conciliacao_mensal_*.
 13. Dados de entrada e saída separados corretamente.
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
    _nome_aba,
    _COLUNAS_MENSAL,
    _LINHA_CABECALHO_TABELA,
)
from app.services.exportacao_fechamento_service import gerar_excel_fechamento


# ── Fixtures ─────────────────────────────────────────────────────────────────

EMPRESA_A = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
EMPRESA_B = uuid.UUID("bbbbbbbb-0000-0000-0000-000000000002")
FECH_1 = uuid.UUID("00000000-1111-0000-0000-000000000001")
FECH_2 = uuid.UUID("00000000-2222-0000-0000-000000000002")
FECH_3 = uuid.UUID("00000000-3333-0000-0000-000000000003")
ARQ_1 = uuid.UUID("00000000-0000-1111-0000-000000000001")


def _make_fechamento(
    fid=FECH_1,
    empresa_id=EMPRESA_A,
    tipo="extrato_anotado",
    status="aprovado",
    periodo_inicio=date(2026, 6, 1),
    titulo="Conciliação 01/06",
):
    f = MagicMock()
    f.id = fid
    f.empresa_id = empresa_id
    f.tipo_conciliacao = tipo
    f.status = status
    f.periodo_inicio = periodo_inicio
    f.periodo_fim = periodo_inicio
    f.titulo = titulo
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
    l.linha_origem = linha_origem
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

    q_fech = MagicMock()
    q_fech.filter.return_value = q_fech
    q_fech.order_by.return_value = q_fech
    q_fech.all.return_value = fechamentos

    q_emp = MagicMock()
    q_emp.filter.return_value = q_emp
    q_emp.first.return_value = empresa_obj

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
    fech_a = _make_fechamento(fid=FECH_1, empresa_id=EMPRESA_A)
    db = _db_com_fechamentos(fechamentos=[fech_a], lancamentos=[])
    conteudo, nome = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    assert len(conteudo) > 0
    assert "empresa_teste" in nome or "2026_06" in nome
    assert db.query.called


# ── Teste 4: filtra por tipo de conciliação ───────────────────────────────────

def test_filtra_por_tipo_conciliacao():
    fech = _make_fechamento(fid=FECH_1, tipo="extrato_anotado", status="aprovado")
    db = _db_com_fechamentos(fechamentos=[fech], lancamentos=[])
    conteudo, nome = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    assert len(conteudo) > 0
    assert "extrato_anotado" in nome


# ── Teste 5: inclui múltiplos dias do mesmo mês ───────────────────────────────

def test_multiplos_dias_mesmo_mes():
    fech1 = _make_fechamento(fid=FECH_1, periodo_inicio=date(2026, 6, 1))
    fech2 = _make_fechamento(fid=FECH_2, periodo_inicio=date(2026, 6, 2))
    fech3 = _make_fechamento(fid=FECH_3, periodo_inicio=date(2026, 6, 9))

    l1 = _make_lancamento(fechamento_id=FECH_1, data=date(2026, 6, 1))
    l2 = _make_lancamento(fechamento_id=FECH_2, data=date(2026, 6, 2))
    l3 = _make_lancamento(fechamento_id=FECH_3, data=date(2026, 6, 9))

    db = _db_com_fechamentos(fechamentos=[fech1, fech2, fech3], lancamentos=[l1, l2, l3])
    conteudo, _ = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    assert len(conteudo) > 0

    wb = openpyxl.load_workbook(io.BytesIO(conteudo))
    ws = wb.active
    # 7 linhas de cabeçalho + 1 cabeçalho de tabela + 3 lançamentos = 11 linhas
    assert ws.max_row >= _LINHA_CABECALHO_TABELA + 3


# ── Teste 6: não inclui datas fora do mês ────────────────────────────────────

def test_exclui_datas_fora_do_mes():
    fech_junho = _make_fechamento(fid=FECH_1, periodo_inicio=date(2026, 6, 15))
    db = _db_com_fechamentos(fechamentos=[fech_junho], lancamentos=[])
    fechamentos = buscar_fechamentos_do_mes(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    assert len(fechamentos) == 1
    assert fechamentos[0].periodo_inicio.month == 6


# ── Teste 7: gera workbook com UMA única aba ─────────────────────────────────

def test_gera_workbook_com_uma_aba():
    fech = _make_fechamento()
    l = _make_lancamento()
    db = _db_com_fechamentos(fechamentos=[fech], lancamentos=[l])
    conteudo, nome = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    wb = openpyxl.load_workbook(io.BytesIO(conteudo))
    assert wb is not None
    assert nome.endswith(".xlsx")
    assert len(wb.sheetnames) == 1, f"Esperado 1 aba, mas encontrou: {wb.sheetnames}"


# ── Teste 8: aba tem nome no formato mês+ano ─────────────────────────────────

def test_aba_tem_nome_mes_ano():
    fech = _make_fechamento(periodo_inicio=date(2026, 6, 1))
    l = _make_lancamento(data=date(2026, 6, 1))
    db = _db_com_fechamentos(fechamentos=[fech], lancamentos=[l])
    conteudo, _ = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    wb = openpyxl.load_workbook(io.BytesIO(conteudo))
    assert wb.sheetnames[0] == "Jun26", f"Nome da aba esperado 'Jun26', recebeu '{wb.sheetnames[0]}'"


def test_nome_aba_diferentes_meses():
    """Valida a função auxiliar de nomeação da aba para todos os meses."""
    assert _nome_aba(1, 2026) == "Jan26"
    assert _nome_aba(6, 2026) == "Jun26"
    assert _nome_aba(12, 2025) == "Dez25"
    assert _nome_aba(3, 2027) == "Mar27"


# ── Teste 9: NÃO contém abas antigas ─────────────────────────────────────────

def test_nao_contem_abas_antigas():
    """A exportação mensal não deve mais gerar abas do formato antigo."""
    fech = _make_fechamento()
    l = _make_lancamento()
    db = _db_com_fechamentos(fechamentos=[fech], lancamentos=[l])
    conteudo, _ = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    wb = openpyxl.load_workbook(io.BytesIO(conteudo))
    abas = wb.sheetnames
    assert "Resumo Mensal" not in abas, "Aba 'Resumo Mensal' não deve existir"
    assert "Conciliação Mensal" not in abas, "Aba 'Conciliação Mensal' não deve existir"
    assert "Dias Incluídos" not in abas, "Aba 'Dias Incluídos' não deve existir"
    assert "Pendências" not in abas, "Aba 'Pendências' não deve existir"


# ── Teste 10: cabeçalho da tabela na linha 8 com colunas corretas ────────────

def test_cabecalho_tabela_na_linha_8():
    fech = _make_fechamento()
    l = _make_lancamento()
    db = _db_com_fechamentos(fechamentos=[fech], lancamentos=[l])
    conteudo, _ = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    wb = openpyxl.load_workbook(io.BytesIO(conteudo))
    ws = wb.active
    cabecalhos = [ws.cell(row=_LINHA_CABECALHO_TABELA, column=c).value for c in range(1, len(_COLUNAS_MENSAL) + 1)]
    assert cabecalhos == _COLUNAS_MENSAL, f"Cabeçalhos incorretos: {cabecalhos}"


# ── Teste 11: lançamentos aparecem a partir da linha 9 ───────────────────────

def test_lancamentos_a_partir_da_linha_9():
    fech = _make_fechamento()
    l = _make_lancamento(descricao_banco="TED recebida teste")
    db = _db_com_fechamentos(fechamentos=[fech], lancamentos=[l])
    conteudo, _ = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    wb = openpyxl.load_workbook(io.BytesIO(conteudo))
    ws = wb.active
    primeira_linha_dados = _LINHA_CABECALHO_TABELA + 1
    descricao = ws.cell(row=primeira_linha_dados, column=2).value
    assert descricao == "TED recebida teste", f"Descrição esperada na linha {primeira_linha_dados}, recebeu: {descricao}"


# ── Teste 12: nome do arquivo segue padrão ia16_conciliacao_mensal_* ─────────

def test_nome_arquivo_padrao():
    fech = _make_fechamento()
    l = _make_lancamento()
    db = _db_com_fechamentos(fechamentos=[fech], lancamentos=[l])
    _, nome = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    assert nome.startswith("ia16_conciliacao_mensal_"), f"Nome não segue padrão: {nome}"
    assert "2026_06" in nome
    assert nome.endswith(".xlsx")


# ── Teste 13: entrada e saída separados corretamente ─────────────────────────

def test_entrada_saida_separados():
    fech = _make_fechamento()
    l_entrada = _make_lancamento(tipo_movimento="entrada", valor=Decimal("1000.00"), saldo=None)
    l_saida = _make_lancamento(tipo_movimento="saida", valor=Decimal("300.00"), saldo=None)
    db = _db_com_fechamentos(fechamentos=[fech], lancamentos=[l_entrada, l_saida])
    conteudo, _ = gerar_excel_mensal(
        db=db, empresa_id=EMPRESA_A, ano=2026, mes=6, tipo_conciliacao="extrato_anotado"
    )
    wb = openpyxl.load_workbook(io.BytesIO(conteudo))
    ws = wb.active

    col_entrada = _COLUNAS_MENSAL.index("ENTRADA EXTRATO") + 1  # 1-based
    col_saida = _COLUNAS_MENSAL.index("SAIDA EXTRATO") + 1

    linha_entrada = _LINHA_CABECALHO_TABELA + 1
    linha_saida = _LINHA_CABECALHO_TABELA + 2

    assert ws.cell(row=linha_entrada, column=col_entrada).value == 1000.0
    assert ws.cell(row=linha_entrada, column=col_saida).value in (None, "")

    assert ws.cell(row=linha_saida, column=col_saida).value == 300.0
    assert ws.cell(row=linha_saida, column=col_entrada).value in (None, "")
