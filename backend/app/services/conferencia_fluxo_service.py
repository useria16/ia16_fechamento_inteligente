"""
Serviço de conferência entre lançamentos do extrato e previstos do fluxo de caixa.

Estratégia: categoria semântica + data (janela de tolerância).

Hierarquia de match:
  1. encontrado            — categoria compatível + mesma data
  2. data_diferente        — categoria compatível + data próxima (≤ tolerancia_dias)
  3. possivel_correspondencia — mesmo tipo_movimento + data compatível, sem categoria compatível
  4. nao_encontrado        — nenhuma correspondência encontrada

Múltiplos lançamentos do extrato podem referenciar o mesmo previsto do fluxo (1:N)
porque o fluxo de caixa agrega por categoria/dia enquanto o extrato é granular.
"""
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

TOLERANCIA_DIAS_PADRAO = 3

# ── Grupos semânticos ─────────────────────────────────────────────────────────
#
# Palavras-chave em texto do extrato → grupo semântico (ordem importa — mais específico primeiro)
_PALAVRAS_GRUPO_EXTRATO: list[tuple[list[str], str]] = [
    (["SALARIO", "FOLHA", "PROLABORE", "PRÓ-LABORE", "REMUNER", "FUNCIONARIO"],             "remuneracao"),
    (["TRIBUTO", "DARF", "GPS ", "GNRE", "IMPOSTO", "FISCAL"],                               "tributo"),
    (["REND PAGO", "REND RECEBIDO", "RENDIMENTO", "APLIC AUT", "INVESTIMENTO", "CDB"],       "rendimento"),
    (["TARIFA", "TAR ", "ANUIDADE", "IOF"],                                                   "tarifa"),
    (["PIX RECEBIDO", "TED RECEBIDA", "DOC RECEBIDO", "RECEBIMENTO"],                        "recebimento"),
    (["PIX ENVIADO", "PIX QR-CODE", "PIX PAGO", "BOLETO PAGO", "BOLETO",
      "PAGAMENTOS TRANSF", "TRANSF CC", "TED ENVIADA", "SISPAG", "PAGAMENTO FORNEC"],        "pagamento"),
]

# Palavras-chave em descricao_prevista do fluxo → grupo semântico (ordem importa)
_PALAVRAS_GRUPO_FLUXO: list[tuple[list[str], str]] = [
    (["SALARIO", "FOLHA", "PROLABORE", "REMUNER", "FUNCIONARIO", "COLABORAD", "PESSOAL"],   "remuneracao"),
    (["TRIBUTO", "DARF", "GPS ", "GNRE", "IMPOSTO", "FISCAL"],                               "tributo"),
    (["RENDIMENTO", "REND ", "APLIC", "INVESTIMENTO", "RETORNO", "JUROS", "CDB", "FUNDO"],   "rendimento"),
    (["TARIFA", "TAR ", "ANUIDADE", "IOF", "ENCARGO", "DESPESA BANC"],                       "tarifa"),
    (["RECEBIMENTO", "RECEITA", "FATURAMENTO", "COBRANÇA", "CLIENTE", "VENDA"],               "recebimento"),
    (["PAGAMENTO", "PAGO", "FORNEC", "DESPESA", "CUSTO", "COMPRA",
      "PIX ", "BOLETO", "TRANSF", "TED ", "SAIDA", "TRANSFERE"],                             "pagamento"),
]


def _grupo_extrato(descricao_realizada: str | None) -> str | None:
    """Deriva o grupo semântico a partir da descrição do lançamento bancário."""
    if not descricao_realizada:
        return None
    desc_upper = descricao_realizada.upper()
    for palavras, grupo in _PALAVRAS_GRUPO_EXTRATO:
        if any(p in desc_upper for p in palavras):
            return grupo
    return None


def _grupo_fluxo(descricao_prevista: str | None) -> str | None:
    """Deriva o grupo semântico a partir da categoria do fluxo de caixa."""
    if not descricao_prevista:
        return None
    desc_upper = descricao_prevista.upper()
    for palavras, grupo in _PALAVRAS_GRUPO_FLUXO:
        if any(p in desc_upper for p in palavras):
            return grupo
    return None


def _grupos_compativeis(grupo_e: str | None, grupo_f: str | None) -> bool:
    return grupo_e is not None and grupo_f is not None and grupo_e == grupo_f


# ── Dataclass de resultado ────────────────────────────────────────────────────

@dataclass
class ConferenciaFluxo:
    previsto_no_fluxo: bool | None
    tipo_conferencia_fluxo: str | None
    confianca_conferencia: Decimal | None
    observacao_sistema: str | None
    data_prevista: date | None
    valor_previsto: Decimal | None
    descricao_prevista: str | None


# ── Funções públicas ──────────────────────────────────────────────────────────

def conferir_lancamentos(
    realizados: list[Any],
    previstos: list[Any],
    tolerancia_dias: int = TOLERANCIA_DIAS_PADRAO,
) -> list[ConferenciaFluxo]:
    """
    Para cada realizado, encontra o melhor match no fluxo de caixa.

    Args:
        realizados:      Lista de LancamentoRealizado (extrato normalizado).
        previstos:       Lista de LancamentoPrevisto (fluxo normalizado).
                         Pode estar vazia — retorna campos NULL para todos.
        tolerancia_dias: Janela de dias para match próximo.

    Returns:
        Lista de ConferenciaFluxo com o mesmo tamanho que realizados.
    """
    if not previstos:
        return [_sem_fluxo() for _ in realizados]

    # Índice: (data, tipo_movimento) → lista de previstos
    idx: dict[tuple[date, str], list[Any]] = {}
    for p in previstos:
        chave = (p.data_prevista, p.tipo_movimento)
        idx.setdefault(chave, []).append(p)

    return [_conferir_um(r, idx, tolerancia_dias) for r in realizados]


# ── Lógica de match ───────────────────────────────────────────────────────────

def _conferir_um(
    realizado: Any,
    idx: dict[tuple[date, str], list[Any]],
    tolerancia_dias: int,
) -> ConferenciaFluxo:
    data_r = realizado.data_realizada
    tipo = realizado.tipo_movimento
    grupo_e = _grupo_extrato(getattr(realizado, "descricao_realizada", None))

    # ── Coletar candidatos por data ────────────────────────────────────────

    # data exata
    candidatos_exatos = idx.get((data_r, tipo), [])

    # data próxima: melhor candidato por offset mínimo
    melhor_proximo: Any | None = None
    melhor_diff: int | None = None
    for offset in range(1, tolerancia_dias + 1):
        for data_alt in [data_r - timedelta(days=offset), data_r + timedelta(days=offset)]:
            for p in idx.get((data_alt, tipo), []):
                if melhor_diff is None or offset < melhor_diff:
                    melhor_diff = offset
                    melhor_proximo = p

    # ── 1. Encontrado forte: categoria compatível + data exata ────────────
    for p in candidatos_exatos:
        if _grupos_compativeis(grupo_e, _grupo_fluxo(p.descricao_prevista)):
            valor_ext = abs(Decimal(str(getattr(realizado, "valor_realizado", 0) or 0)))
            valor_prev = abs(p.valor_previsto)
            valor_difere = abs(valor_ext - valor_prev) > Decimal("0.01")
            if valor_difere:
                obs = (
                    f"Lançamento encontrado no fluxo de caixa para a mesma categoria e data "
                    f"({p.descricao_prevista}), mas o valor do extrato "
                    f"(R$ {valor_ext:.2f}) difere do valor previsto "
                    f"(R$ {valor_prev:.2f}). Revisar manualmente."
                )
            else:
                obs = (
                    f"Lançamento encontrado no fluxo de caixa para a mesma categoria e data "
                    f"({p.descricao_prevista})."
                )
            return ConferenciaFluxo(
                previsto_no_fluxo=True,
                tipo_conferencia_fluxo="encontrado",
                confianca_conferencia=Decimal("0.85"),
                observacao_sistema=obs,
                data_prevista=p.data_prevista,
                valor_previsto=valor_prev,
                descricao_prevista=p.descricao_prevista,
            )

    # ── 2. Data diferente: categoria compatível + data próxima ────────────
    if melhor_proximo is not None and melhor_diff is not None:
        if _grupos_compativeis(grupo_e, _grupo_fluxo(melhor_proximo.descricao_prevista)):
            p = melhor_proximo
            return ConferenciaFluxo(
                previsto_no_fluxo=True,
                tipo_conferencia_fluxo="data_diferente",
                confianca_conferencia=Decimal("0.60"),
                observacao_sistema=(
                    f"Possível correspondência com '{p.descricao_prevista}' "
                    f"previsto para {p.data_prevista} "
                    f"(diferença de {melhor_diff} dia(s))."
                ),
                data_prevista=p.data_prevista,
                valor_previsto=abs(p.valor_previsto),
                descricao_prevista=p.descricao_prevista,
            )

    # ── 3. Possível correspondência: tipo_movimento + data, sem categoria ──
    # Há candidatos por tipo/data mas sem categoria compatível
    melhor_possivel = (
        candidatos_exatos[0]
        if candidatos_exatos
        else melhor_proximo
    )
    if melhor_possivel is not None:
        p = melhor_possivel
        diff_info = (
            f"data {data_r}"
            if p in candidatos_exatos
            else f"data próxima {p.data_prevista} (diferença de {melhor_diff} dia(s))"
        )
        return ConferenciaFluxo(
            previsto_no_fluxo=True,
            tipo_conferencia_fluxo="possivel_correspondencia",
            confianca_conferencia=Decimal("0.40"),
            observacao_sistema=(
                f"Possível correspondência encontrada no fluxo pelo tipo de movimento "
                f"e {diff_info}, mas sem categoria claramente compatível. "
                f"Revisar manualmente."
            ),
            data_prevista=p.data_prevista,
            valor_previsto=abs(p.valor_previsto),
            descricao_prevista=p.descricao_prevista,
        )

    # ── 4. Não encontrado ──────────────────────────────────────────────────
    return ConferenciaFluxo(
        previsto_no_fluxo=False,
        tipo_conferencia_fluxo="nao_encontrado",
        confianca_conferencia=Decimal("0.00"),
        observacao_sistema="Lançamento não localizado no fluxo de caixa.",
        data_prevista=None,
        valor_previsto=None,
        descricao_prevista=None,
    )


def _sem_fluxo() -> ConferenciaFluxo:
    """Retorna resultado vazio quando não há fluxo de caixa disponível."""
    return ConferenciaFluxo(
        previsto_no_fluxo=None,
        tipo_conferencia_fluxo=None,
        confianca_conferencia=None,
        observacao_sistema=None,
        data_prevista=None,
        valor_previsto=None,
        descricao_prevista=None,
    )
