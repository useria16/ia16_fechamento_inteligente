"""
Service de exportação do pacote final do fechamento em Excel.

Gera um arquivo .xlsx em memória com 5 abas:
  1. Resumo
  2. Itens Conciliados
  3. Divergências
  4. Pendências
  5. Observações da Revisão
"""
import io
import re
from datetime import datetime, timezone

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from sqlalchemy.orm import Session

from app.models.divergencia_conciliacao import DivergenciaConciliacao
from app.models.empresa import Empresa
from app.models.fechamento_financeiro import FechamentoFinanceiro
from app.models.item_conciliacao import ItemConciliacao
from app.models.lancamento_extrato_anotado import LancamentoExtratoAnotado
from app.models.usuario import Usuario


# ── helpers ────────────────────────────────────────────────────────────────────

def _sanitizar_nome(valor: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", valor.strip().lower())


def _estilizar_cabecalho(ws, linha: int, num_colunas: int) -> None:
    fill = PatternFill("solid", fgColor="1F4E79")
    font = Font(bold=True, color="FFFFFF")
    for col in range(1, num_colunas + 1):
        cell = ws.cell(row=linha, column=col)
        cell.fill = fill
        cell.font = font
        cell.alignment = Alignment(horizontal="center")


def _ajustar_largura(ws) -> None:
    for col in ws.columns:
        max_len = max((len(str(c.value)) if c.value is not None else 0) for c in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width = min(max_len + 4, 50)


def _fmt(valor) -> str:
    if valor is None:
        return ""
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d %H:%M")
    return str(valor)


# ── aba Resumo ─────────────────────────────────────────────────────────────────

def _aba_resumo(ws, fechamento: FechamentoFinanceiro, empresa_nome: str, aprovado_por: str | None, reaberto_por: str | None) -> None:
    ws.title = "Resumo"
    campos = [
        ("Empresa", empresa_nome),
        ("Título da Conciliação", fechamento.titulo),
        ("Tipo de Conciliação", fechamento.tipo_conciliacao),
        ("Status", fechamento.status),
        ("Período Início", _fmt(fechamento.periodo_inicio)),
        ("Período Fim", _fmt(fechamento.periodo_fim)),
        ("Data de Criação", _fmt(fechamento.criado_em)),
        ("Data de Processamento", _fmt(fechamento.atualizado_em)),
        ("Data de Aprovação", _fmt(fechamento.aprovado_em)),
        ("Aprovado por", aprovado_por or ""),
        ("Observação de Aprovação", fechamento.observacao_aprovacao or ""),
        ("Motivo da Reabertura", fechamento.motivo_reabertura or ""),
        ("Reaberto em", _fmt(fechamento.reaberto_em)),
        ("Reaberto por", reaberto_por or ""),
        ("Quantidade de Registros", fechamento.quantidade_registros),
        ("Quantidade de Conciliados", fechamento.quantidade_conciliados),
        ("Quantidade de Divergentes", fechamento.quantidade_divergentes),
        ("Quantidade de Pendentes", fechamento.quantidade_pendentes),
        ("Valor Total Processado", float(fechamento.valor_total_processado or 0)),
        ("Valor Total Conciliado", float(fechamento.valor_total_conciliado or 0)),
        ("Valor Total Divergente", float(fechamento.valor_total_divergente or 0)),
    ]

    header_fill = PatternFill("solid", fgColor="1F4E79")
    header_font = Font(bold=True, color="FFFFFF")

    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 40

    for i, (campo, valor) in enumerate(campos, start=1):
        cell_a = ws.cell(row=i, column=1, value=campo)
        cell_a.fill = header_fill
        cell_a.font = header_font
        ws.cell(row=i, column=2, value=valor)


# ── aba Itens Conciliados ──────────────────────────────────────────────────────

def _aba_itens_conciliados(ws, itens: list[ItemConciliacao]) -> None:
    ws.title = "Itens Conciliados"
    cabecalho = [
        "Data Prevista", "Data Realizada", "Descrição Prevista", "Descrição Realizada",
        "Tipo de Movimento", "Valor Previsto", "Valor Realizado",
        "Diferença de Valor", "Diferença em Dias", "Confiança",
    ]
    ws.append(cabecalho)
    _estilizar_cabecalho(ws, 1, len(cabecalho))

    for item in itens:
        ws.append([
            _fmt(item.data_prevista),
            _fmt(item.data_realizada),
            item.descricao_prevista or "",
            item.descricao_realizada or "",
            item.tipo_movimento,
            float(item.valor_previsto) if item.valor_previsto is not None else "",
            float(item.valor_realizado) if item.valor_realizado is not None else "",
            float(item.diferenca_valor) if item.diferenca_valor is not None else "",
            item.diferenca_dias if item.diferenca_dias is not None else "",
            float(item.confianca) if item.confianca is not None else "",
        ])
    _ajustar_largura(ws)


# ── aba Divergências ───────────────────────────────────────────────────────────

def _aba_divergencias(ws, divergencias: list[DivergenciaConciliacao]) -> None:
    ws.title = "Divergências"
    cabecalho = [
        "Tipo de Divergência", "Severidade", "Status da Revisão", "Descrição",
        "Valor Previsto", "Valor Realizado", "Diferença de Valor",
        "Data Prevista", "Data Realizada", "Diferença em Dias",
        "Observação", "Resolvido em", "Atualizado em",
    ]
    ws.append(cabecalho)
    _estilizar_cabecalho(ws, 1, len(cabecalho))

    for d in divergencias:
        ws.append([
            d.tipo_divergencia,
            d.severidade,
            d.status,
            d.descricao,
            float(d.valor_previsto) if d.valor_previsto is not None else "",
            float(d.valor_realizado) if d.valor_realizado is not None else "",
            float(d.diferenca_valor) if d.diferenca_valor is not None else "",
            _fmt(d.data_prevista),
            _fmt(d.data_realizada),
            d.diferenca_dias if d.diferenca_dias is not None else "",
            d.observacao or "",
            _fmt(d.resolvido_em),
            _fmt(d.atualizado_em),
        ])
    _ajustar_largura(ws)


# ── aba Pendências ─────────────────────────────────────────────────────────────

def _aba_pendencias(ws, pendencias: list[DivergenciaConciliacao]) -> None:
    ws.title = "Pendências"
    cabecalho = [
        "Tipo", "Severidade", "Status da Revisão", "Descrição",
        "Valor Previsto", "Valor Realizado",
        "Data Prevista", "Data Realizada",
        "Observação", "Resolvido em", "Atualizado em",
    ]
    ws.append(cabecalho)
    _estilizar_cabecalho(ws, 1, len(cabecalho))

    for p in pendencias:
        ws.append([
            p.tipo_divergencia,
            p.severidade,
            p.status,
            p.descricao,
            float(p.valor_previsto) if p.valor_previsto is not None else "",
            float(p.valor_realizado) if p.valor_realizado is not None else "",
            _fmt(p.data_prevista),
            _fmt(p.data_realizada),
            p.observacao or "",
            _fmt(p.resolvido_em),
            _fmt(p.atualizado_em),
        ])
    _ajustar_largura(ws)


# ── aba Observações da Revisão ─────────────────────────────────────────────────

def _aba_observacoes(ws, divergencias_com_obs: list[DivergenciaConciliacao]) -> None:
    ws.title = "Observações da Revisão"
    cabecalho = [
        "Tipo de Divergência", "Status da Revisão", "Observação",
        "Atualizado por (ID)", "Atualizado em", "Resolvido em",
    ]
    ws.append(cabecalho)
    _estilizar_cabecalho(ws, 1, len(cabecalho))

    for d in divergencias_com_obs:
        ws.append([
            d.tipo_divergencia,
            d.status,
            d.observacao or "",
            str(d.atualizado_por_usuario_id) if d.atualizado_por_usuario_id else "",
            _fmt(d.atualizado_em),
            _fmt(d.resolvido_em),
        ])
    _ajustar_largura(ws)


# ── aba Extrato Anotado ────────────────────────────────────────────────────────

_LABELS_CONFERENCIA = {
    "encontrado":             "Previsto no fluxo",
    "data_diferente":         "Data diferente",
    "nao_encontrado":         "Não encontrado",
    "valor_diferente":        "Valor diferente",
    "possivel_correspondencia": "Revisar",
    "pendente_analise":       "Pendente",
}


def _aba_extrato_anotado(ws, lancamentos: list[LancamentoExtratoAnotado]) -> None:
    ws.title = "Extrato Anotado"
    tem_conferencia = any(l.tipo_conferencia_fluxo is not None for l in lancamentos)
    cabecalho = [
        "DATA", "DESCRIÇÃO LANÇAMENTO BANCO", "DESCRIÇÃO FORNECEDOR/CLIENTE",
        "NF / DOC", "VALOR NF/DOC",
        "ENTRADA EXTRATO", "SAÍDA EXTRATO", "SALDO",
        "OBSERVAÇÃO", "CATEGORIA", "STATUS REVISÃO",
    ]
    if tem_conferencia:
        cabecalho.append("STATUS NO FLUXO")

    ws.append(cabecalho)
    _estilizar_cabecalho(ws, 1, len(cabecalho))

    for l in lancamentos:
        entrada = float(l.valor) if l.tipo_movimento == "entrada" else ""
        saida   = float(l.valor) if l.tipo_movimento == "saida"   else ""
        saldo   = float(l.saldo) if l.saldo is not None else ""
        linha = [
            _fmt(l.data_lancamento),
            l.descricao_banco or "",
            l.descricao_negocio or "",
            l.nf_doc or "",
            float(l.valor_nf_doc) if l.valor_nf_doc is not None else "",
            entrada,
            saida,
            saldo,
            l.observacao or "",
            l.categoria or l.categoria_sugerida or "",
            l.status_revisao,
        ]
        if tem_conferencia:
            linha.append(_LABELS_CONFERENCIA.get(l.tipo_conferencia_fluxo or "", ""))
        ws.append(linha)
    _ajustar_largura(ws)


def _aba_conferencia_fluxo(ws, lancamentos: list[LancamentoExtratoAnotado]) -> None:
    ws.title = "Conferência com Fluxo"
    cabecalho = [
        "DATA EXTRATO", "DESCRIÇÃO BANCO", "TIPO MOVIMENTO",
        "VALOR EXTRATO", "STATUS NO FLUXO",
        "DATA PREVISTA", "VALOR PREVISTO", "DESCRIÇÃO PREVISTA",
        "OBSERVAÇÃO SISTEMA", "CONFIANÇA",
    ]
    ws.append(cabecalho)
    _estilizar_cabecalho(ws, 1, len(cabecalho))

    for l in lancamentos:
        ws.append([
            _fmt(l.data_lancamento),
            l.descricao_banco or "",
            l.tipo_movimento,
            float(l.valor),
            _LABELS_CONFERENCIA.get(l.tipo_conferencia_fluxo or "", l.tipo_conferencia_fluxo or ""),
            _fmt(l.data_prevista) if l.data_prevista else "",
            float(l.valor_previsto) if l.valor_previsto is not None else "",
            l.descricao_prevista or "",
            l.observacao_sistema or "",
            float(l.confianca_conferencia) if l.confianca_conferencia is not None else "",
        ])
    _ajustar_largura(ws)


def _aba_pendencias_extrato(ws, pendentes: list[LancamentoExtratoAnotado]) -> None:
    ws.title = "Pendências de Revisão"
    cabecalho = ["DATA", "DESCRIÇÃO BANCO", "RAZÃO SOCIAL", "VALOR", "TIPO", "CATEGORIA SUGERIDA", "STATUS"]
    ws.append(cabecalho)
    _estilizar_cabecalho(ws, 1, len(cabecalho))
    for l in pendentes:
        ws.append([
            _fmt(l.data_lancamento), l.descricao_banco or "", l.razao_social or "",
            float(l.valor), l.tipo_movimento,
            l.categoria_sugerida or "", l.status_revisao,
        ])
    _ajustar_largura(ws)


def _aba_observacoes_extrato(ws, com_obs: list[LancamentoExtratoAnotado]) -> None:
    ws.title = "Observações"
    cabecalho = ["DATA", "DESCRIÇÃO BANCO", "CATEGORIA", "OBSERVAÇÃO", "ATUALIZADO EM", "STATUS"]
    ws.append(cabecalho)
    _estilizar_cabecalho(ws, 1, len(cabecalho))
    for l in com_obs:
        ws.append([
            _fmt(l.data_lancamento), l.descricao_banco or "",
            l.categoria or l.categoria_sugerida or "",
            l.observacao or "", _fmt(l.atualizado_em), l.status_revisao,
        ])
    _ajustar_largura(ws)


# ── função principal ───────────────────────────────────────────────────────────

def gerar_excel_fechamento(db: Session, fechamento: FechamentoFinanceiro) -> tuple[bytes, str]:
    if fechamento.tipo_conciliacao == "extrato_anotado":
        return _gerar_excel_extrato_anotado(db, fechamento)
    return _gerar_excel_bilateral(db, fechamento)


def _gerar_excel_extrato_anotado(db: Session, fechamento: FechamentoFinanceiro) -> tuple[bytes, str]:
    empresa = db.query(Empresa).filter(Empresa.id == fechamento.empresa_id).first()
    empresa_nome = empresa.nome if empresa else str(fechamento.empresa_id)

    lancamentos = (
        db.query(LancamentoExtratoAnotado)
        .filter(LancamentoExtratoAnotado.fechamento_id == fechamento.id)
        .order_by(LancamentoExtratoAnotado.data_lancamento, LancamentoExtratoAnotado.linha_origem)
        .all()
    )

    pendentes = [l for l in lancamentos if l.status_revisao == "pendente"]
    com_obs   = [l for l in lancamentos if l.observacao]

    wb = openpyxl.Workbook()
    ws_resumo = wb.active
    ws_resumo.title = "Resumo"

    fill_h = PatternFill("solid", fgColor="1F4E79")
    font_h = Font(bold=True, color="FFFFFF")
    ws_resumo.column_dimensions["A"].width = 35
    ws_resumo.column_dimensions["B"].width = 40

    resumo_campos = [
        ("Empresa", empresa_nome),
        ("Conciliação", fechamento.titulo),
        ("Tipo", "Extrato Anotado"),
        ("Status", fechamento.status),
        ("Período Início", _fmt(fechamento.periodo_inicio)),
        ("Período Fim", _fmt(fechamento.periodo_fim)),
        ("Aprovado em", _fmt(fechamento.aprovado_em)),
        ("", ""),
        ("Total de Lançamentos", len(lancamentos)),
        ("Revisados", sum(1 for l in lancamentos if l.status_revisao == "revisado")),
        ("Pendentes", len(pendentes)),
        ("Ignorados", sum(1 for l in lancamentos if l.status_revisao == "ignorado")),
        ("Com sugestão automática", sum(1 for l in lancamentos if l.categoria_sugerida)),
        ("", ""),
        ("Valor Total Entradas", float(sum(l.valor for l in lancamentos if l.tipo_movimento == "entrada"))),
        ("Valor Total Saídas",   float(sum(l.valor for l in lancamentos if l.tipo_movimento == "saida"))),
    ]

    tem_conferencia = any(l.tipo_conferencia_fluxo is not None for l in lancamentos)
    if tem_conferencia:
        resumo_campos += [
            ("", ""),
            ("Conferência com Fluxo de Caixa", ""),
            ("Encontrados (categoria + data)",    sum(1 for l in lancamentos if l.tipo_conferencia_fluxo == "encontrado")),
            ("Possível correspondência (revisar)", sum(1 for l in lancamentos if l.tipo_conferencia_fluxo == "possivel_correspondencia")),
            ("Data diferente",                    sum(1 for l in lancamentos if l.tipo_conferencia_fluxo == "data_diferente")),
            ("Não encontrados no fluxo",          sum(1 for l in lancamentos if l.tipo_conferencia_fluxo == "nao_encontrado")),
        ]

    for i, (campo, valor) in enumerate(resumo_campos, start=1):
        ca = ws_resumo.cell(row=i, column=1, value=campo)
        ws_resumo.cell(row=i, column=2, value=valor)
        if campo:
            ca.fill = fill_h
            ca.font = font_h

    _aba_extrato_anotado(wb.create_sheet(), lancamentos)
    _aba_pendencias_extrato(wb.create_sheet(), pendentes)
    _aba_observacoes_extrato(wb.create_sheet(), com_obs)

    tem_conferencia = any(l.tipo_conferencia_fluxo is not None for l in lancamentos)
    if tem_conferencia:
        _aba_conferencia_fluxo(wb.create_sheet(), lancamentos)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    conteudo = buffer.read()

    empresa_slug = _sanitizar_nome(empresa_nome)
    data_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    id_curto = str(fechamento.id)[:8]
    nome = f"ia16_extrato_anotado_{empresa_slug}_{data_str}_{id_curto}.xlsx"

    return conteudo, nome


def _gerar_excel_bilateral(db: Session, fechamento: FechamentoFinanceiro) -> tuple[bytes, str]:
    """
    Gera o Excel do pacote final do fechamento.
    Retorna (bytes_do_arquivo, nome_do_arquivo).
    """
    empresa = db.query(Empresa).filter(Empresa.id == fechamento.empresa_id).first()
    empresa_nome = empresa.nome if empresa else str(fechamento.empresa_id)

    aprovado_por: str | None = None
    if fechamento.aprovado_por_usuario_id:
        u = db.query(Usuario).filter(Usuario.id == fechamento.aprovado_por_usuario_id).first()
        aprovado_por = u.email if u else str(fechamento.aprovado_por_usuario_id)

    reaberto_por: str | None = None
    if fechamento.reaberto_por_usuario_id:
        u = db.query(Usuario).filter(Usuario.id == fechamento.reaberto_por_usuario_id).first()
        reaberto_por = u.email if u else str(fechamento.reaberto_por_usuario_id)

    # Buscar itens conciliados
    itens_conciliados = (
        db.query(ItemConciliacao)
        .filter(
            ItemConciliacao.fechamento_id == fechamento.id,
            ItemConciliacao.status == "conciliado",
        )
        .all()
    )

    # Buscar todas as divergências
    todas_divergencias = (
        db.query(DivergenciaConciliacao)
        .filter(DivergenciaConciliacao.fechamento_id == fechamento.id)
        .all()
    )

    divergencias_normais = [d for d in todas_divergencias if d.tipo_divergencia != "pendente_analise_manual"]
    pendencias = [d for d in todas_divergencias if d.tipo_divergencia == "pendente_analise_manual"]
    com_observacao = [d for d in todas_divergencias if d.observacao]

    # Montar workbook
    wb = openpyxl.Workbook()
    ws_resumo = wb.active
    _aba_resumo(ws_resumo, fechamento, empresa_nome, aprovado_por, reaberto_por)

    _aba_itens_conciliados(wb.create_sheet(), itens_conciliados)
    _aba_divergencias(wb.create_sheet(), divergencias_normais)
    _aba_pendencias(wb.create_sheet(), pendencias)
    _aba_observacoes(wb.create_sheet(), com_observacao)

    # Gerar bytes em memória
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    conteudo = buffer.read()

    # Nome do arquivo
    empresa_slug = _sanitizar_nome(empresa_nome)
    data_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    id_curto = str(fechamento.id)[:8]
    nome_arquivo = f"ia16_fechamento_inteligente_{empresa_slug}_{data_str}_{id_curto}.xlsx"

    return conteudo, nome_arquivo
