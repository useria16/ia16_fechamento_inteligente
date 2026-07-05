"""
Service de exportação do consolidado mensal de conciliações em Excel.

Gera um arquivo .xlsx em memória com 4 abas:
  1. Resumo Mensal        — totais agregados do mês
  2. Conciliação Mensal   — todos os lançamentos do período
  3. Dias Incluídos       — lista de fechamentos incluídos
  4. Pendências           — lançamentos com status pendente ou divergente

Suporta qualquer tipo de conciliação (multicliente/multiconciliação).
Para tipo extrato_anotado: consolida LancamentoExtratoAnotado.
Para outros tipos: consolida ItemConciliacao e DivergenciaConciliacao.
"""
import io
import re
import calendar
from datetime import date

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from sqlalchemy.orm import Session

from app.models.divergencia_conciliacao import DivergenciaConciliacao
from app.models.empresa import Empresa
from app.models.fechamento_financeiro import FechamentoFinanceiro
from app.models.item_conciliacao import ItemConciliacao
from app.models.lancamento_extrato_anotado import LancamentoExtratoAnotado

# Status que indicam processamento concluído e elegíveis para o consolidado
_STATUS_EXPORTAVEL = {"processado", "com_divergencias", "aprovado", "reaberto"}

# Status de lançamento extrato que indicam pendência
_STATUS_PENDENTE_EXTRATO = {"pendente", "em_revisao"}

# Tipos de conferência de fluxo que indicam pendência
_TIPOS_PENDENTE_FLUXO = {"nao_encontrado", "valor_diferente", "data_diferente", "possivel_correspondencia", "pendente_analise"}

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

LABELS_CONFERENCIA = {
    "encontrado": "Previsto no fluxo",
    "data_diferente": "Data diferente",
    "nao_encontrado": "Não encontrado",
    "valor_diferente": "Valor diferente",
    "possivel_correspondencia": "Revisar",
    "pendente_analise": "Pendente",
}


# ── helpers de estilo ─────────────────────────────────────────────────────────

def _sanitizar_nome(valor: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", valor.strip().lower())


def _estilo_cabecalho(ws, linha: int, num_colunas: int) -> None:
    fill = PatternFill("solid", fgColor="1F4E79")
    font = Font(bold=True, color="FFFFFF")
    for col in range(1, num_colunas + 1):
        cell = ws.cell(row=linha, column=col)
        cell.fill = fill
        cell.font = font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _ajustar_largura(ws) -> None:
    for col in ws.columns:
        max_len = max((len(str(c.value)) if c.value is not None else 0) for c in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width = min(max_len + 4, 60)


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


# ── aba Resumo Mensal ─────────────────────────────────────────────────────────

def _aba_resumo_mensal(
    ws,
    empresa_nome: str,
    tipo_conciliacao: str,
    ano: int,
    mes: int,
    fechamentos: list[FechamentoFinanceiro],
    lancamentos: list,
) -> None:
    ws.title = "Resumo Mensal"

    fill_azul = PatternFill("solid", fgColor="1F4E79")
    font_branca = Font(bold=True, color="FFFFFF")
    fill_claro = PatternFill("solid", fgColor="EBF3FB")

    ws.column_dimensions["A"].width = 35
    ws.column_dimensions["B"].width = 45

    periodo = f"{MESES_PT.get(mes, str(mes))}/{ano}"

    # Totais calculados dos lançamentos (para extrato_anotado)
    total_entradas = sum(
        float(l.valor) for l in lancamentos
        if hasattr(l, "tipo_movimento") and l.tipo_movimento == "entrada"
    )
    total_saidas = sum(
        float(l.valor) for l in lancamentos
        if hasattr(l, "tipo_movimento") and l.tipo_movimento == "saida"
    )
    total_lancamentos = len(lancamentos)
    encontrados = sum(
        1 for l in lancamentos
        if hasattr(l, "tipo_conferencia_fluxo") and l.tipo_conferencia_fluxo == "encontrado"
    )
    nao_encontrados = sum(
        1 for l in lancamentos
        if hasattr(l, "tipo_conferencia_fluxo") and l.tipo_conferencia_fluxo == "nao_encontrado"
    )
    pendentes = sum(
        1 for l in lancamentos
        if hasattr(l, "status_revisao") and l.status_revisao in _STATUS_PENDENTE_EXTRATO
    )
    aprovados = sum(1 for f in fechamentos if f.status == "aprovado")
    com_divergencias = sum(1 for f in fechamentos if f.status == "com_divergencias")

    primeiro_dia = _fmt_data(fechamentos[0].periodo_inicio) if fechamentos else ""
    ultimo_dia = _fmt_data(fechamentos[-1].periodo_inicio) if fechamentos else ""

    campos = [
        ("Empresa", empresa_nome),
        ("Tipo de Conciliação", tipo_conciliacao),
        ("Período", periodo),
        ("Primeiro Dia Incluído", primeiro_dia),
        ("Último Dia Incluído", ultimo_dia),
        ("Quantidade de Conciliações", len(fechamentos)),
        ("Conciliações Aprovadas", aprovados),
        ("Conciliações com Divergências", com_divergencias),
        ("Total de Lançamentos", total_lancamentos),
        ("Total de Entradas (R$)", total_entradas),
        ("Total de Saídas (R$)", total_saidas),
        ("Lançamentos Encontrados no Fluxo", encontrados),
        ("Lançamentos Não Encontrados no Fluxo", nao_encontrados),
        ("Lançamentos Pendentes de Revisão", pendentes),
    ]

    for i, (campo, valor) in enumerate(campos, start=1):
        cell_a = ws.cell(row=i, column=1, value=campo)
        cell_a.fill = fill_azul
        cell_a.font = font_branca
        cell_b = ws.cell(row=i, column=2, value=valor)
        cell_b.fill = fill_claro


# ── aba Conciliação Mensal (extrato_anotado) ──────────────────────────────────

def _aba_conciliacao_mensal_extrato(
    ws,
    fechamentos: list[FechamentoFinanceiro],
    lancamentos: list[LancamentoExtratoAnotado],
    titulo_por_fechamento: dict,
) -> None:
    ws.title = "Conciliação Mensal"

    tem_conferencia = any(l.tipo_conferencia_fluxo is not None for l in lancamentos)

    cabecalho = [
        "DATA", "TÍTULO DA CONCILIAÇÃO", "STATUS CONCILIAÇÃO",
        "DESCRIÇÃO LANÇAMENTO BANCO", "DESCRIÇÃO FORNECEDOR/CLIENTE",
        "NF / DOC", "VALOR NF/DOC",
        "ENTRADA EXTRATO", "SAÍDA EXTRATO", "SALDO",
        "CATEGORIA", "STATUS REVISÃO",
    ]
    if tem_conferencia:
        cabecalho += ["STATUS NO FLUXO", "DATA PREVISTA", "VALOR PREVISTO", "DESCRIÇÃO PREVISTA",
                      "OBSERVAÇÃO SISTEMA", "OBSERVAÇÃO MANUAL"]

    ws.append(cabecalho)
    _estilo_cabecalho(ws, 1, len(cabecalho))

    # Indexar status do fechamento por fechamento_id
    status_por_fechamento = {str(f.id): f.status for f in fechamentos}

    for l in lancamentos:
        entrada = float(l.valor) if l.tipo_movimento == "entrada" else ""
        saida = float(l.valor) if l.tipo_movimento == "saida" else ""
        saldo = float(l.saldo) if l.saldo is not None else ""
        fech_id = str(l.fechamento_id)
        titulo = titulo_por_fechamento.get(fech_id, "")
        status_conc = status_por_fechamento.get(fech_id, "")

        linha = [
            _fmt_data(l.data_lancamento),
            titulo,
            status_conc,
            l.descricao_banco or "",
            l.descricao_negocio or "",
            l.nf_doc or "",
            _fmt_decimal(l.valor_nf_doc),
            entrada,
            saida,
            saldo,
            l.categoria or l.categoria_sugerida or "",
            l.status_revisao,
        ]
        if tem_conferencia:
            linha += [
                LABELS_CONFERENCIA.get(l.tipo_conferencia_fluxo or "", l.tipo_conferencia_fluxo or ""),
                _fmt_data(l.data_prevista),
                _fmt_decimal(l.valor_previsto),
                l.descricao_prevista or "",
                l.observacao_sistema or "",
                l.observacao or "",
            ]
        ws.append(linha)

    _ajustar_largura(ws)


# ── aba Conciliação Mensal (bilateral) ────────────────────────────────────────

def _aba_conciliacao_mensal_bilateral(
    ws,
    fechamentos: list[FechamentoFinanceiro],
    itens: list[ItemConciliacao],
    titulo_por_fechamento: dict,
) -> None:
    ws.title = "Conciliação Mensal"

    cabecalho = [
        "DATA PREVISTA", "DATA REALIZADA", "TÍTULO DA CONCILIAÇÃO", "STATUS CONCILIAÇÃO",
        "DESCRIÇÃO PREVISTA", "DESCRIÇÃO REALIZADA", "TIPO MOVIMENTO",
        "VALOR PREVISTO", "VALOR REALIZADO", "DIFERENÇA DE VALOR",
        "DIFERENÇA EM DIAS", "CONFIANÇA",
    ]
    ws.append(cabecalho)
    _estilo_cabecalho(ws, 1, len(cabecalho))

    status_por_fechamento = {str(f.id): f.status for f in fechamentos}

    for item in itens:
        fech_id = str(item.fechamento_id)
        ws.append([
            _fmt_data(item.data_prevista),
            _fmt_data(item.data_realizada),
            titulo_por_fechamento.get(fech_id, ""),
            status_por_fechamento.get(fech_id, ""),
            item.descricao_prevista or "",
            item.descricao_realizada or "",
            item.tipo_movimento,
            _fmt_decimal(item.valor_previsto),
            _fmt_decimal(item.valor_realizado),
            _fmt_decimal(item.diferenca_valor),
            item.diferenca_dias if item.diferenca_dias is not None else "",
            _fmt_decimal(item.confianca),
        ])

    _ajustar_largura(ws)


# ── aba Dias Incluídos ────────────────────────────────────────────────────────

def _aba_dias_incluidos(
    ws,
    fechamentos: list[FechamentoFinanceiro],
    lancamentos_por_fechamento: dict[str, list],
) -> None:
    ws.title = "Dias Incluídos"

    cabecalho = [
        "DATA", "ID FECHAMENTO", "TÍTULO", "STATUS",
        "QUANTIDADE DE LANÇAMENTOS", "LANÇAMENTOS ENCONTRADOS",
        "LANÇAMENTOS NÃO ENCONTRADOS", "TOTAL ENTRADAS (R$)", "TOTAL SAÍDAS (R$)",
    ]
    ws.append(cabecalho)
    _estilo_cabecalho(ws, 1, len(cabecalho))

    for f in fechamentos:
        fech_id = str(f.id)
        lances = lancamentos_por_fechamento.get(fech_id, [])
        encontrados = sum(
            1 for l in lances
            if hasattr(l, "tipo_conferencia_fluxo") and l.tipo_conferencia_fluxo == "encontrado"
        )
        nao_enc = sum(
            1 for l in lances
            if hasattr(l, "tipo_conferencia_fluxo") and l.tipo_conferencia_fluxo == "nao_encontrado"
        )
        total_ent = sum(
            float(l.valor) for l in lances
            if hasattr(l, "tipo_movimento") and l.tipo_movimento == "entrada"
        )
        total_sai = sum(
            float(l.valor) for l in lances
            if hasattr(l, "tipo_movimento") and l.tipo_movimento == "saida"
        )
        ws.append([
            _fmt_data(f.periodo_inicio),
            fech_id[:8],
            f.titulo,
            f.status,
            len(lances),
            encontrados,
            nao_enc,
            total_ent,
            total_sai,
        ])

    _ajustar_largura(ws)


# ── aba Pendências ────────────────────────────────────────────────────────────

def _aba_pendencias_mensal(
    ws,
    fechamentos: list[FechamentoFinanceiro],
    pendentes: list,
    titulo_por_fechamento: dict,
) -> None:
    ws.title = "Pendências"

    # Detectar se são lançamentos de extrato ou divergências bilaterais
    eh_extrato = pendentes and hasattr(pendentes[0], "descricao_banco")

    if eh_extrato:
        cabecalho = [
            "DATA", "TÍTULO DA CONCILIAÇÃO", "STATUS CONCILIAÇÃO",
            "DESCRIÇÃO BANCO", "RAZÃO SOCIAL", "VALOR", "TIPO",
            "CATEGORIA SUGERIDA", "STATUS REVISÃO", "STATUS NO FLUXO",
            "OBSERVAÇÃO",
        ]
        ws.append(cabecalho)
        _estilo_cabecalho(ws, 1, len(cabecalho))
        status_por_fechamento = {str(f.id): f.status for f in fechamentos}
        for l in pendentes:
            fech_id = str(l.fechamento_id)
            ws.append([
                _fmt_data(l.data_lancamento),
                titulo_por_fechamento.get(fech_id, ""),
                status_por_fechamento.get(fech_id, ""),
                l.descricao_banco or "",
                getattr(l, "razao_social", "") or "",
                float(l.valor),
                l.tipo_movimento,
                l.categoria_sugerida or "",
                l.status_revisao,
                LABELS_CONFERENCIA.get(l.tipo_conferencia_fluxo or "", l.tipo_conferencia_fluxo or ""),
                l.observacao or "",
            ])
    else:
        cabecalho = [
            "TIPO DIVERGÊNCIA", "SEVERIDADE", "STATUS REVISÃO",
            "TÍTULO DA CONCILIAÇÃO", "DESCRIÇÃO",
            "VALOR PREVISTO", "VALOR REALIZADO",
            "DATA PREVISTA", "DATA REALIZADA", "OBSERVAÇÃO",
        ]
        ws.append(cabecalho)
        _estilo_cabecalho(ws, 1, len(cabecalho))
        status_por_fechamento = {str(f.id): f.status for f in fechamentos}
        for d in pendentes:
            fech_id = str(d.fechamento_id)
            ws.append([
                d.tipo_divergencia,
                d.severidade,
                d.status,
                titulo_por_fechamento.get(fech_id, ""),
                d.descricao,
                _fmt_decimal(d.valor_previsto),
                _fmt_decimal(d.valor_realizado),
                _fmt_data(d.data_prevista),
                _fmt_data(d.data_realizada),
                d.observacao or "",
            ])

    _ajustar_largura(ws)


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
    Gera o Excel consolidado mensal para uma empresa, tipo de conciliação e mês.

    Retorna (bytes_do_arquivo, nome_do_arquivo).
    Levanta ValueError se não houver fechamentos no período.
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
    titulo_por_fechamento = {str(f.id): f.titulo for f in fechamentos}

    wb = openpyxl.Workbook()

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

        lancamentos_por_fechamento: dict[str, list] = {str(f.id): [] for f in fechamentos}
        for l in lancamentos:
            lancamentos_por_fechamento[str(l.fechamento_id)].append(l)

        pendentes = [
            l for l in lancamentos
            if l.status_revisao in _STATUS_PENDENTE_EXTRATO
            or (l.tipo_conferencia_fluxo and l.tipo_conferencia_fluxo in _TIPOS_PENDENTE_FLUXO)
        ]

        ws_resumo = wb.active
        _aba_resumo_mensal(ws_resumo, empresa_nome, tipo_conciliacao, ano, mes, fechamentos, lancamentos)
        _aba_conciliacao_mensal_extrato(wb.create_sheet(), fechamentos, lancamentos, titulo_por_fechamento)
        _aba_dias_incluidos(wb.create_sheet(), fechamentos, lancamentos_por_fechamento)
        _aba_pendencias_mensal(wb.create_sheet(), fechamentos, pendentes, titulo_por_fechamento)

    else:
        # Tipo bilateral: consolida ItemConciliacao e DivergenciaConciliacao
        itens = (
            db.query(ItemConciliacao)
            .filter(ItemConciliacao.fechamento_id.in_(ids_fechamentos))
            .order_by(ItemConciliacao.fechamento_id, ItemConciliacao.data_prevista)
            .all()
        )

        divergencias = (
            db.query(DivergenciaConciliacao)
            .filter(
                DivergenciaConciliacao.fechamento_id.in_(ids_fechamentos),
                DivergenciaConciliacao.status.in_(["aberta", "em_analise"]),
            )
            .order_by(DivergenciaConciliacao.fechamento_id)
            .all()
        )

        # Para a aba Dias Incluídos, agrupa itens por fechamento
        itens_por_fechamento: dict[str, list] = {str(f.id): [] for f in fechamentos}
        for item in itens:
            itens_por_fechamento[str(item.fechamento_id)].append(item)

        ws_resumo = wb.active
        # Para bilateral, o resumo usa quantidades dos modelos de fechamento
        _aba_resumo_mensal_bilateral(ws_resumo, empresa_nome, tipo_conciliacao, ano, mes, fechamentos)
        _aba_conciliacao_mensal_bilateral(wb.create_sheet(), fechamentos, itens, titulo_por_fechamento)
        _aba_dias_incluidos(wb.create_sheet(), fechamentos, itens_por_fechamento)
        _aba_pendencias_mensal(wb.create_sheet(), fechamentos, divergencias, titulo_por_fechamento)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    conteudo = buffer.read()

    empresa_slug = _sanitizar_nome(empresa_nome)
    tipo_slug = _sanitizar_nome(tipo_conciliacao)
    nome_arquivo = f"ia16_consolidado_{empresa_slug}_{tipo_slug}_{ano}_{mes:02d}.xlsx"

    return conteudo, nome_arquivo


def _aba_resumo_mensal_bilateral(
    ws,
    empresa_nome: str,
    tipo_conciliacao: str,
    ano: int,
    mes: int,
    fechamentos: list[FechamentoFinanceiro],
) -> None:
    """Resumo mensal para tipos bilaterais (não extrato_anotado)."""
    ws.title = "Resumo Mensal"

    fill_azul = PatternFill("solid", fgColor="1F4E79")
    font_branca = Font(bold=True, color="FFFFFF")
    fill_claro = PatternFill("solid", fgColor="EBF3FB")

    ws.column_dimensions["A"].width = 35
    ws.column_dimensions["B"].width = 45

    periodo = f"{MESES_PT.get(mes, str(mes))}/{ano}"
    primeiro_dia = _fmt_data(fechamentos[0].periodo_inicio) if fechamentos else ""
    ultimo_dia = _fmt_data(fechamentos[-1].periodo_inicio) if fechamentos else ""
    aprovados = sum(1 for f in fechamentos if f.status == "aprovado")
    com_diverg = sum(1 for f in fechamentos if f.status == "com_divergencias")
    total_registros = sum(f.quantidade_registros for f in fechamentos)
    total_conciliados = sum(f.quantidade_conciliados for f in fechamentos)
    total_divergentes = sum(f.quantidade_divergentes for f in fechamentos)
    total_pendentes = sum(f.quantidade_pendentes for f in fechamentos)
    total_processado = sum(float(f.valor_total_processado or 0) for f in fechamentos)
    total_conciliado_val = sum(float(f.valor_total_conciliado or 0) for f in fechamentos)
    total_divergente_val = sum(float(f.valor_total_divergente or 0) for f in fechamentos)

    campos = [
        ("Empresa", empresa_nome),
        ("Tipo de Conciliação", tipo_conciliacao),
        ("Período", periodo),
        ("Primeiro Dia Incluído", primeiro_dia),
        ("Último Dia Incluído", ultimo_dia),
        ("Quantidade de Conciliações", len(fechamentos)),
        ("Conciliações Aprovadas", aprovados),
        ("Conciliações com Divergências", com_diverg),
        ("Total de Registros", total_registros),
        ("Total de Conciliados", total_conciliados),
        ("Total de Divergentes", total_divergentes),
        ("Total de Pendentes", total_pendentes),
        ("Valor Total Processado (R$)", total_processado),
        ("Valor Total Conciliado (R$)", total_conciliado_val),
        ("Valor Total Divergente (R$)", total_divergente_val),
    ]

    for i, (campo, valor) in enumerate(campos, start=1):
        cell_a = ws.cell(row=i, column=1, value=campo)
        cell_a.fill = fill_azul
        cell_a.font = font_branca
        cell_b = ws.cell(row=i, column=2, value=valor)
        cell_b.fill = fill_claro
