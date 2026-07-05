"""
Service de exportação da planilha mensal de conciliação.

Gera um arquivo .xlsx em memória com uma única aba no layout da planilha
conciliada mensal: cabeçalho de empresa nas primeiras linhas, seguido da
tabela de lançamentos acumulados do mês (uma linha por lançamento).

Suporta qualquer tipo de conciliação (multicliente/multiconciliação).
"""
import io
import re
import calendar
from datetime import date, datetime

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from sqlalchemy.orm import Session

from app.models.arquivo_enviado import ArquivoEnviado
from app.models.empresa import Empresa
from app.models.fechamento_financeiro import FechamentoFinanceiro
from app.models.item_conciliacao import ItemConciliacao
from app.models.lancamento_extrato_anotado import LancamentoExtratoAnotado

# Status que indicam processamento concluído e elegíveis para exportação
_STATUS_EXPORTAVEL = {"processado", "com_divergencias", "aprovado", "reaberto"}

# Abreviações dos meses em PT-BR (3 letras)
_ABREV_MES = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

# Colunas fixas da aba mensal (em ordem)
_COLUNAS_MENSAL = [
    "DATA",
    "DESCRIÇÃO LANÇAMENTO BANCO",
    "DESCRIÇÃO FORNECEDOR/CLIENTE",
    "NF / DOC",
    "VALOR NF/DOC",
    "ENTRADA EXTRATO",
    "SAIDA EXTRATO",
    "SALDO",
]

# Linha onde o cabeçalho da tabela é inserido
_LINHA_CABECALHO_TABELA = 8

# Estilo do cabeçalho da tabela
_FILL_CABECALHO = PatternFill("solid", fgColor="1F4E79")
_FONT_CABECALHO = Font(bold=True, color="FFFFFF")
_ALIGN_CENTRO = Alignment(horizontal="center", vertical="center", wrap_text=True)


# ── helpers ───────────────────────────────────────────────────────────────────

def _sanitizar_nome(valor: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", valor.strip().lower())


def _sanitizar_nome_arquivo(valor: str) -> str:
    """Sanitiza o nome para uso em nome de arquivo, preservando maiúsculas."""
    return re.sub(r'[/\\:*?"<>|. ]', "_", valor.strip())


def _fmt_data(valor) -> str:
    if valor is None:
        return ""
    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y")
    return str(valor)


def _fmt_decimal(valor) -> float | str:
    if valor is None:
        return ""
    return float(valor)


def _nome_aba(mes: int, ano: int) -> str:
    """Retorna o nome da aba no formato 'Jun26'."""
    abrev = _ABREV_MES.get(mes, str(mes))
    return f"{abrev}{str(ano)[-2:]}"


def _ajustar_largura(ws) -> None:
    for col in ws.columns:
        max_len = max((len(str(c.value)) if c.value is not None else 0) for c in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width = min(max_len + 4, 60)


# ── busca de metadados do arquivo de extrato ─────────────────────────────────

def _buscar_metadados_extrato(db: Session, ids_fechamentos: list) -> dict:
    """
    Busca os metadados do arquivo de extrato bancário vinculado aos fechamentos.

    Percorre os fechamentos em ordem e retorna os metadados do primeiro arquivo
    de extrato_bancario que tiver metadados preenchidos.

    Retorna dict vazio se nenhum arquivo tiver metadados disponíveis.
    """
    for fech_id in ids_fechamentos:
        arquivo = (
            db.query(ArquivoEnviado)
            .filter(
                ArquivoEnviado.fechamento_id == fech_id,
                ArquivoEnviado.tipo_arquivo == "extrato_bancario",
            )
            .first()
        )
        if arquivo and arquivo.metadados:
            return arquivo.metadados
    return {}


# ── busca de fechamentos ───────────────────────────────────────────────────────

def buscar_fechamentos_do_mes(
    db: Session,
    empresa_id,
    ano: int,
    mes: int,
    tipo_conciliacao: str,
    status_incluidos: set[str] | None = None,
) -> list[FechamentoFinanceiro]:
    """
    Retorna fechamentos da empresa, ano, mês e tipo de conciliação informados.
    O mês é determinado pelo campo periodo_inicio do fechamento.
    """
    if status_incluidos is None:
        status_incluidos = _STATUS_EXPORTAVEL

    primeiro_dia = date(ano, mes, 1)
    ultimo_dia = date(ano, mes, calendar.monthrange(ano, mes)[1])

    fechamentos = (
        db.query(FechamentoFinanceiro)
        .filter(
            FechamentoFinanceiro.empresa_id == empresa_id,
            FechamentoFinanceiro.tipo_conciliacao == tipo_conciliacao,
            FechamentoFinanceiro.status.in_(status_incluidos),
            FechamentoFinanceiro.periodo_inicio >= primeiro_dia,
            FechamentoFinanceiro.periodo_inicio <= ultimo_dia,
        )
        .order_by(FechamentoFinanceiro.periodo_inicio)
        .all()
    )
    return fechamentos


# ── construção da aba mensal ──────────────────────────────────────────────────

def _montar_cabecalho_empresa(
    ws,
    empresa_nome: str,
    mes: int,
    ano: int,
    metadados: dict | None = None,
) -> None:
    """
    Preenche as linhas de cabeçalho da empresa acima da tabela de lançamentos.

    Usa metadados do arquivo de extrato quando disponíveis (atualizacao, nome,
    agencia, conta). Fallback para data/hora atual e nome da empresa.

    Estrutura:
      Linha 1: Atualização:  <metadados["atualizacao"] ou data/hora atual>
      Linha 2: Nome:         <metadados["nome"] ou nome da empresa>
      Linha 3: Agência:      <metadados["agencia"] ou vazio>
      Linha 4: Conta:        <metadados["conta"] ou vazio>
      Linha 5: (vazia)
      Linha 6: Periodo:  <Mês>/<Ano>
      Linha 7: (vazia)
    """
    meta = metadados or {}
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    periodo = f"{MESES_PT.get(mes, str(mes))}/{ano}"

    atualizacao = meta.get("atualizacao") or agora
    nome_banco = meta.get("nome") or empresa_nome
    agencia = meta.get("agencia") or ""
    conta = meta.get("conta") or ""

    font_label = Font(bold=True)

    ws.cell(row=1, column=1, value="Atualização:").font = font_label
    ws.cell(row=1, column=2, value=atualizacao)

    ws.cell(row=2, column=1, value="Nome:").font = font_label
    ws.cell(row=2, column=2, value=nome_banco)

    ws.cell(row=3, column=1, value="Agência:").font = font_label
    ws.cell(row=3, column=2, value=agencia)

    ws.cell(row=4, column=1, value="Conta:").font = font_label
    ws.cell(row=4, column=2, value=conta)

    # Linha 5 vazia

    ws.cell(row=6, column=1, value=f"Periodo:  {periodo}").font = font_label

    # Linha 7 vazia


def _montar_cabecalho_tabela(ws) -> None:
    """Insere e estiliza o cabeçalho da tabela na linha _LINHA_CABECALHO_TABELA."""
    for col_idx, titulo in enumerate(_COLUNAS_MENSAL, start=1):
        cell = ws.cell(row=_LINHA_CABECALHO_TABELA, column=col_idx, value=titulo)
        cell.fill = _FILL_CABECALHO
        cell.font = _FONT_CABECALHO
        cell.alignment = _ALIGN_CENTRO


def _linhas_extrato_anotado(lancamentos: list) -> list[list]:
    """
    Converte lançamentos de extrato_anotado nas linhas da tabela mensal.
    Cada linha: [DATA, DESCRIÇÃO BANCO, DESCRIÇÃO FORNECEDOR, NF/DOC,
                 VALOR NF/DOC, ENTRADA, SAIDA, SALDO]
    """
    linhas = []
    for l in lancamentos:
        entrada = _fmt_decimal(l.valor) if l.tipo_movimento == "entrada" else ""
        saida = _fmt_decimal(l.valor) if l.tipo_movimento == "saida" else ""
        saldo = _fmt_decimal(l.saldo) if l.saldo is not None else ""
        linhas.append([
            l.data_lancamento if hasattr(l.data_lancamento, "strftime") else _fmt_data(l.data_lancamento),
            l.descricao_banco or "",
            l.descricao_negocio or "",
            l.nf_doc or "",
            _fmt_decimal(l.valor_nf_doc) if l.valor_nf_doc is not None else "",
            entrada,
            saida,
            saldo,
        ])
    return linhas


def _linhas_bilateral(itens: list) -> list[list]:
    """
    Converte ItemConciliacao nas colunas da planilha mensal.
    Campos que não existem no modelo bilateral ficam em branco.
    """
    linhas = []
    for item in itens:
        data = item.data_realizada or item.data_prevista
        entrada = _fmt_decimal(item.valor_realizado) if getattr(item, "tipo_movimento", None) == "entrada" else ""
        saida = _fmt_decimal(item.valor_realizado) if getattr(item, "tipo_movimento", None) == "saida" else ""
        linhas.append([
            data if hasattr(data, "strftime") else _fmt_data(data),
            item.descricao_realizada or item.descricao_prevista or "",
            item.descricao_prevista or "",
            "",   # NF / DOC — não disponível no modelo bilateral
            "",   # VALOR NF/DOC
            entrada,
            saida,
            "",   # SALDO — não disponível no modelo bilateral
        ])
    return linhas


def _preencher_dados(ws, linhas: list[list]) -> None:
    """Escreve as linhas de dados a partir de _LINHA_CABECALHO_TABELA + 1."""
    inicio = _LINHA_CABECALHO_TABELA + 1
    for row_offset, linha in enumerate(linhas):
        for col_idx, valor in enumerate(linha, start=1):
            ws.cell(row=inicio + row_offset, column=col_idx, value=valor)


# ── função principal ───────────────────────────────────────────────────────────

def gerar_excel_mensal(
    db: Session,
    empresa_id,
    ano: int,
    mes: int,
    tipo_conciliacao: str,
    status_incluidos: set[str] | None = None,
) -> tuple[bytes, str]:
    """
    Gera a planilha mensal de conciliação para uma empresa, tipo e mês.

    Retorna (bytes_do_arquivo, nome_do_arquivo).
    Levanta ValueError se não houver fechamentos no período.

    O arquivo tem uma única aba com o layout da planilha conciliada mensal:
    cabeçalho de empresa nas linhas 1–7, cabeçalho da tabela na linha 8
    e lançamentos acumulados do mês a partir da linha 9.
    """
    fechamentos = buscar_fechamentos_do_mes(
        db, empresa_id, ano, mes, tipo_conciliacao, status_incluidos
    )

    if not fechamentos:
        raise ValueError(
            f"Nenhuma conciliação encontrada para {MESES_PT.get(mes, str(mes))}/{ano} "
            f"com tipo '{tipo_conciliacao}'."
        )

    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    empresa_nome = empresa.nome if empresa else str(empresa_id)

    ids_fechamentos = [f.id for f in fechamentos]

    # Busca metadados do arquivo de extrato para preencher cabeçalho
    metadados = _buscar_metadados_extrato(db, ids_fechamentos)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = _nome_aba(mes, ano)

    _montar_cabecalho_empresa(ws, empresa_nome, mes, ano, metadados)
    _montar_cabecalho_tabela(ws)

    if tipo_conciliacao == "extrato_anotado":
        lancamentos = (
            db.query(LancamentoExtratoAnotado)
            .filter(LancamentoExtratoAnotado.fechamento_id.in_(ids_fechamentos))
            .order_by(
                LancamentoExtratoAnotado.data_lancamento,
                LancamentoExtratoAnotado.fechamento_id,
                LancamentoExtratoAnotado.linha_origem,
            )
            .all()
        )
        linhas = _linhas_extrato_anotado(lancamentos)
    else:
        itens = (
            db.query(ItemConciliacao)
            .filter(ItemConciliacao.fechamento_id.in_(ids_fechamentos))
            .order_by(ItemConciliacao.data_prevista, ItemConciliacao.fechamento_id)
            .all()
        )
        linhas = _linhas_bilateral(itens)

    _preencher_dados(ws, linhas)
    _ajustar_largura(ws)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    conteudo = buffer.read()

    # Nome amigável: Conciliacao_<Empresa>_<Mes>_<Ano>.xlsx
    nome_mes = MESES_PT.get(mes, str(mes))
    empresa_slug = _sanitizar_nome_arquivo(empresa_nome)
    nome_arquivo = f"Conciliacao_{empresa_slug}_{nome_mes}_{ano}.xlsx"

    return conteudo, nome_arquivo
