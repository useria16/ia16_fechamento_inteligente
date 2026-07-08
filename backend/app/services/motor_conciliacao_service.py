"""
Motor de conciliação — Sprint 6B (v2).

Aplica 8 regras determinísticas em ordem para classificar lançamentos:
  1. Separar entrada/saída
  2. Detectar duplicidade no extrato
  3. Detectar duplicidade no fluxo
  4. Match perfeito (mesmo valor, mesma data)
  5. Divergência de data (mesmo valor, data diferente ≤ TOLERANCIA_DIAS)
  6. Divergência de valor (data próxima, valor diferente dentro de 30%)
  7. Previsto não realizado
  8. Realizado não previsto / Pendente análise manual

Tolerâncias padrão utilizadas enquanto Sprint 3.1 (configurações de regras) não existe.

Semântica dos contadores em fechamentos_financeiros:
  quantidade_conciliados  = itens com status "conciliado"
  quantidade_divergentes  = itens com status "divergente"  (todas as divergências específicas)
  quantidade_pendentes    = itens com status "pendente"    (pendente_analise_manual)
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Any
import uuid

from sqlalchemy.orm import Session

from app.models.divergencia_conciliacao import DivergenciaConciliacao
from app.models.item_conciliacao import ItemConciliacao

# Sprint 3.1 substituirá estas constantes por leitura das regras configuradas
TOLERANCIA_DIAS_PADRAO: int = 3
TOLERANCIA_VALOR_EXATO: Decimal = Decimal("0.01")  # centavo — para match perfeito
LIMIAR_DIVERGENCIA_VALOR: float = 0.30              # 30% — máximo para divergência de valor

# Indicadores bancários de "sem identificação" — marcam razao_social como genérica
_RAZOES_SEM_IDENTIFICACAO: tuple[str, ...] = (
    "s/identificacao", "s/identif", "sem identificacao", "sem identif",
    "transf s/ident", "s/id", "sem id",
)


@dataclass
class ResultadoMotor:
    quantidade_conciliados: int
    quantidade_divergentes: int
    quantidade_pendentes: int
    valor_total_processado: Decimal
    valor_total_conciliado: Decimal
    valor_total_divergente: Decimal


# ── Helpers ──────────────────────────────────────────────────────────────────

def _valor_igual(v_r: Decimal, v_p: Decimal) -> bool:
    return abs(abs(v_r) - abs(v_p)) <= TOLERANCIA_VALOR_EXATO


def _diff_dias(data_r, data_p) -> int:
    return abs((data_r - data_p).days)


def _diferenca_valor_relativa(v_r: Decimal, v_p: Decimal) -> float:
    denom = max(abs(v_r), abs(v_p))
    if denom == 0:
        return 0.0
    return float(abs(abs(v_r) - abs(v_p)) / denom)


def _documento_e_placeholder(doc: str) -> bool:
    """CPF/CNPJ com apenas zeros, separadores e espaços = placeholder sem identificação."""
    return bool(doc) and all(c in "0./- " for c in doc)


def _e_pendente_analise_manual(realizado: Any) -> bool:
    """
    Classifica como pendente_analise_manual quando não há identificação suficiente:
    (razao_social vazia OU contém indicador bancário de "sem identificação")
    E (documento vazio OU é placeholder de zeros).
    """
    razao_raw = str(getattr(realizado, "razao_social", "") or "").strip()
    razao_lower = razao_raw.lower()
    sem_razao = (
        not razao_raw or
        any(padrao in razao_lower for padrao in _RAZOES_SEM_IDENTIFICACAO)
    )
    doc_raw = str(getattr(realizado, "documento", "") or "").strip()
    sem_doc = not doc_raw or _documento_e_placeholder(doc_raw)
    return sem_razao and sem_doc


def _detectar_duplicatas(
    registros: list[tuple[uuid.UUID, Any]],
    campo_valor: str,
    campo_data: str,
) -> set[int]:
    """
    Retorna os índices dos registros duplicados (2ª+ ocorrência).
    Agrupa por (tipo_movimento, abs(valor), data).
    A 1ª ocorrência de cada grupo é mantida para conciliação.
    """
    vistos: dict[tuple, int] = {}
    duplicados: set[int] = set()
    for i, (_, reg) in enumerate(registros):
        chave = (
            reg.tipo_movimento,
            abs(getattr(reg, campo_valor)),
            getattr(reg, campo_data),
        )
        if chave in vistos:
            duplicados.add(i)
        else:
            vistos[chave] = i
    return duplicados


def _item_base(
    *,
    empresa_id: uuid.UUID,
    fechamento_id: uuid.UUID,
    tipo_item: str,
    status: str,
    tipo_movimento: str,
    data_prevista=None,
    data_realizada=None,
    descricao_prevista=None,
    descricao_realizada=None,
    valor_previsto=None,
    valor_realizado=None,
    diferenca_valor=None,
    diferenca_dias=None,
    confianca: Decimal = Decimal("1.0"),
    arquivo_extrato_id=None,
    arquivo_fluxo_id=None,
    metadados: dict | None = None,
) -> ItemConciliacao:
    return ItemConciliacao(
        empresa_id=empresa_id,
        fechamento_id=fechamento_id,
        arquivo_extrato_id=arquivo_extrato_id,
        arquivo_fluxo_id=arquivo_fluxo_id,
        tipo_item=tipo_item,
        status=status,
        tipo_movimento=tipo_movimento,
        data_prevista=data_prevista,
        data_realizada=data_realizada,
        descricao_prevista=descricao_prevista,
        descricao_realizada=descricao_realizada,
        valor_previsto=valor_previsto,
        valor_realizado=valor_realizado,
        diferenca_valor=diferenca_valor,
        diferenca_dias=diferenca_dias,
        confianca=confianca,
        metadados=metadados or {},
    )


def _div(
    tipo: str,
    severidade: str,
    descricao: str,
    **campos,
) -> dict:
    return {"tipo_divergencia": tipo, "severidade": severidade, "descricao": descricao, **campos}


# ── Motor principal ───────────────────────────────────────────────────────────

def executar_motor(
    fechamento_id: uuid.UUID,
    empresa_id: uuid.UUID,
    realizados: list[tuple[uuid.UUID, Any]],  # (arquivo_id, LancamentoRealizado)
    previstos: list[tuple[uuid.UUID, Any]],   # (arquivo_id, LancamentoPrevisto)
    db: Session,
    tolerancia_dias: int = TOLERANCIA_DIAS_PADRAO,
) -> ResultadoMotor:
    """
    Executa o motor e persiste itens e divergências.
    Remove registros anteriores (suporte a reprocessamento).
    Não faz commit — responsabilidade do chamador.
    """
    # ── Limpar conciliação anterior ───────────────────────────────────────
    db.query(DivergenciaConciliacao).filter(
        DivergenciaConciliacao.fechamento_id == fechamento_id
    ).delete(synchronize_session=False)
    db.query(ItemConciliacao).filter(
        ItemConciliacao.fechamento_id == fechamento_id
    ).delete(synchronize_session=False)

    itens_div: list[tuple[ItemConciliacao, dict | None]] = []
    usados_r: set[int] = set()
    usados_p: set[int] = set()

    # ── Passo 2: Detectar duplicatas no extrato ───────────────────────────
    dup_r = _detectar_duplicatas(realizados, "valor_realizado", "data_realizada")

    for i in dup_r:
        arq_id, r = realizados[i]
        usados_r.add(i)
        item = _item_base(
            empresa_id=empresa_id,
            fechamento_id=fechamento_id,
            tipo_item="duplicidade_extrato",
            status="divergente",
            tipo_movimento=r.tipo_movimento,
            data_realizada=r.data_realizada,
            descricao_realizada=r.descricao_realizada,
            valor_realizado=abs(r.valor_realizado),
            arquivo_extrato_id=arq_id,
            confianca=Decimal("0.9"),
            metadados={"criterio": "duplicidade_extrato"},
        )
        itens_div.append((item, _div(
            "duplicidade_extrato", "alta",
            f"Lançamento duplicado no extrato: '{r.descricao_realizada}' "
            f"em {r.data_realizada} (R${abs(r.valor_realizado):.2f}) — "
            f"mesmo valor e data já registrados.",
            valor_realizado=abs(r.valor_realizado),
            data_realizada=r.data_realizada,
        )))

    # ── Passo 3: Detectar duplicatas no fluxo ────────────────────────────
    dup_p = _detectar_duplicatas(previstos, "valor_previsto", "data_prevista")

    for i in dup_p:
        arq_id, p = previstos[i]
        usados_p.add(i)
        item = _item_base(
            empresa_id=empresa_id,
            fechamento_id=fechamento_id,
            tipo_item="duplicidade_fluxo",
            status="divergente",
            tipo_movimento=p.tipo_movimento,
            data_prevista=p.data_prevista,
            descricao_prevista=p.descricao_prevista,
            valor_previsto=abs(p.valor_previsto),
            arquivo_fluxo_id=arq_id,
            confianca=Decimal("0.9"),
            metadados={"criterio": "duplicidade_fluxo"},
        )
        itens_div.append((item, _div(
            "duplicidade_fluxo", "media",
            f"Lançamento duplicado no fluxo: '{p.descricao_prevista}' "
            f"em {p.data_prevista} (R${abs(p.valor_previsto):.2f}) — "
            f"mesmo valor e data já registrados.",
            valor_previsto=abs(p.valor_previsto),
            data_prevista=p.data_prevista,
        )))

    # ── Candidatos após remoção das duplicatas ────────────────────────────
    def _candidatos_p(tipo_mov: str) -> list[tuple[int, uuid.UUID, Any]]:
        return [
            (i, arq_id, p)
            for i, (arq_id, p) in enumerate(previstos)
            if i not in usados_p and p.tipo_movimento == tipo_mov
        ]

    # ── Passo 4: Match perfeito ───────────────────────────────────────────
    for i, (arq_r, r) in enumerate(realizados):
        if i in usados_r:
            continue
        v_r = abs(r.valor_realizado)
        for j, arq_p, p in _candidatos_p(r.tipo_movimento):
            if j in usados_p:
                continue
            v_p = abs(p.valor_previsto)
            dd = _diff_dias(r.data_realizada, p.data_prevista)
            if dd == 0 and _valor_igual(v_r, v_p):
                usados_r.add(i)
                usados_p.add(j)
                item = _item_base(
                    empresa_id=empresa_id, fechamento_id=fechamento_id,
                    tipo_item="conciliado", status="conciliado",
                    tipo_movimento=r.tipo_movimento,
                    data_realizada=r.data_realizada, data_prevista=p.data_prevista,
                    descricao_realizada=r.descricao_realizada, descricao_prevista=p.descricao_prevista,
                    valor_realizado=v_r, valor_previsto=v_p,
                    diferenca_valor=Decimal("0"), diferenca_dias=0,
                    arquivo_extrato_id=arq_r, arquivo_fluxo_id=arq_p,
                    confianca=Decimal("1.0"),
                    metadados={"criterio": "match_perfeito"},
                )
                itens_div.append((item, None))
                break

    # ── Passo 5: Divergência de data (mesmo valor, data 1–N dias) ────────
    for i, (arq_r, r) in enumerate(realizados):
        if i in usados_r:
            continue
        v_r = abs(r.valor_realizado)
        melhor_data: tuple[int, int, uuid.UUID, Any] | None = None
        for j, arq_p, p in _candidatos_p(r.tipo_movimento):
            if j in usados_p:
                continue
            v_p = abs(p.valor_previsto)
            dd = _diff_dias(r.data_realizada, p.data_prevista)
            if 1 <= dd <= tolerancia_dias and _valor_igual(v_r, v_p):
                if melhor_data is None or dd < melhor_data[1]:
                    melhor_data = (j, dd, arq_p, p)
        if melhor_data:
            j, dd, arq_p, p = melhor_data
            usados_r.add(i)
            usados_p.add(j)
            v_p = abs(p.valor_previsto)
            sinal = (r.data_realizada - p.data_prevista).days
            item = _item_base(
                empresa_id=empresa_id, fechamento_id=fechamento_id,
                tipo_item="divergencia_data", status="divergente",
                tipo_movimento=r.tipo_movimento,
                data_realizada=r.data_realizada, data_prevista=p.data_prevista,
                descricao_realizada=r.descricao_realizada, descricao_prevista=p.descricao_prevista,
                valor_realizado=v_r, valor_previsto=v_p,
                diferenca_valor=Decimal("0"), diferenca_dias=sinal,
                arquivo_extrato_id=arq_r, arquivo_fluxo_id=arq_p,
                confianca=Decimal("0.9"),
                metadados={"criterio": "divergencia_data"},
            )
            descricao_div = (
                f"Data divergente: realizado em {r.data_realizada}, "
                f"previsto para {p.data_prevista} "
                f"(diferença: {dd} dia(s)). Valor R${v_r:.2f} idêntico."
            )
            itens_div.append((item, _div(
                "divergencia_data", "baixa", descricao_div,
                valor_realizado=v_r, valor_previsto=v_p,
                data_realizada=r.data_realizada, data_prevista=p.data_prevista,
                diferenca_dias=sinal,
            )))

    # ── Passo 6: Divergência de valor (data próxima, valor diferente ≤30%) ─
    for i, (arq_r, r) in enumerate(realizados):
        if i in usados_r:
            continue
        v_r = abs(r.valor_realizado)
        melhor_valor: tuple[int, int, Decimal, uuid.UUID, Any] | None = None
        for j, arq_p, p in _candidatos_p(r.tipo_movimento):
            if j in usados_p:
                continue
            v_p = abs(p.valor_previsto)
            dd = _diff_dias(r.data_realizada, p.data_prevista)
            if dd > tolerancia_dias:
                continue
            if _valor_igual(v_r, v_p):
                continue  # seria match/divergencia_data — já tratado
            diff_rel = _diferenca_valor_relativa(v_r, v_p)
            if diff_rel <= LIMIAR_DIVERGENCIA_VALOR:
                if melhor_valor is None or dd < melhor_valor[1]:
                    melhor_valor = (j, dd, v_p, arq_p, p)
        if melhor_valor:
            j, dd, v_p, arq_p, p = melhor_valor
            usados_r.add(i)
            usados_p.add(j)
            diff_v = v_r - v_p
            sinal_d = (r.data_realizada - p.data_prevista).days
            item = _item_base(
                empresa_id=empresa_id, fechamento_id=fechamento_id,
                tipo_item="divergencia_valor", status="divergente",
                tipo_movimento=r.tipo_movimento,
                data_realizada=r.data_realizada, data_prevista=p.data_prevista,
                descricao_realizada=r.descricao_realizada, descricao_prevista=p.descricao_prevista,
                valor_realizado=v_r, valor_previsto=v_p,
                diferenca_valor=diff_v, diferenca_dias=sinal_d,
                arquivo_extrato_id=arq_r, arquivo_fluxo_id=arq_p,
                confianca=Decimal("0.7"),
                metadados={"criterio": "divergencia_valor"},
            )
            descricao_div = (
                f"Valor divergente: realizado R${v_r:.2f}, "
                f"previsto R${v_p:.2f} (diferença: R${abs(diff_v):.2f}). "
                f"Data próxima ({dd} dia(s))."
            )
            itens_div.append((item, _div(
                "divergencia_valor", "media", descricao_div,
                valor_realizado=v_r, valor_previsto=v_p,
                diferenca_valor=diff_v,
                data_realizada=r.data_realizada, data_prevista=p.data_prevista,
                diferenca_dias=sinal_d,
            )))

    # ── Passo 7: Previstos sem realização ─────────────────────────────────
    for i, (arq_p, p) in enumerate(previstos):
        if i in usados_p:
            continue
        v_p = abs(p.valor_previsto)
        item = _item_base(
            empresa_id=empresa_id, fechamento_id=fechamento_id,
            tipo_item="previsto_nao_realizado", status="divergente",
            tipo_movimento=p.tipo_movimento,
            data_prevista=p.data_prevista,
            descricao_prevista=p.descricao_prevista,
            valor_previsto=v_p,
            arquivo_fluxo_id=arq_p,
            confianca=Decimal("0"),
            metadados={"criterio": "previsto_nao_realizado"},
        )
        itens_div.append((item, _div(
            "previsto_nao_realizado", "media",
            f"Lançamento previsto sem realização no extrato: "
            f"'{p.descricao_prevista}' em {p.data_prevista} (R${v_p:.2f}).",
            valor_previsto=v_p,
            data_prevista=p.data_prevista,
        )))

    # ── Passo 8: Realizados sem previsão ──────────────────────────────────
    for i, (arq_r, r) in enumerate(realizados):
        if i in usados_r:
            continue
        v_r = abs(r.valor_realizado)
        e_pendente = _e_pendente_analise_manual(r)
        tipo_item = "pendente_analise_manual" if e_pendente else "realizado_nao_previsto"
        status_item = "pendente" if e_pendente else "divergente"
        tipo_div = "pendente_analise_manual" if e_pendente else "realizado_nao_previsto"
        severidade = "baixa" if e_pendente else "media"
        if e_pendente:
            descricao_div = (
                f"Lançamento sem identificação suficiente para análise automática: "
                f"'{r.descricao_realizada}' em {r.data_realizada} (R${v_r:.2f}). "
                f"Requer revisão manual."
            )
        else:
            descricao_div = (
                f"Lançamento realizado sem correspondência no fluxo previsto: "
                f"'{r.descricao_realizada}' em {r.data_realizada} (R${v_r:.2f})."
            )
        item = _item_base(
            empresa_id=empresa_id, fechamento_id=fechamento_id,
            tipo_item=tipo_item, status=status_item,
            tipo_movimento=r.tipo_movimento,
            data_realizada=r.data_realizada,
            descricao_realizada=r.descricao_realizada,
            valor_realizado=v_r,
            arquivo_extrato_id=arq_r,
            confianca=Decimal("0"),
            metadados={"criterio": tipo_item},
        )
        itens_div.append((item, _div(
            tipo_div, severidade, descricao_div,
            valor_realizado=v_r,
            data_realizada=r.data_realizada,
        )))

    # ── Persistir itens em lote e divergências ────────────────────────────
    for item, _ in itens_div:
        db.add(item)
    db.flush()

    for item, div_data in itens_div:
        if div_data is None:
            continue
        db.add(DivergenciaConciliacao(
            empresa_id=empresa_id,
            fechamento_id=fechamento_id,
            item_conciliacao_id=item.id,
            **div_data,
        ))

    # ── Calcular contadores ───────────────────────────────────────────────
    qtd_conciliados = sum(1 for item, _ in itens_div if item.status == "conciliado")
    qtd_divergentes = sum(1 for item, _ in itens_div if item.status == "divergente")
    qtd_pendentes = sum(1 for item, _ in itens_div if item.status == "pendente")

    valor_total_processado = Decimal("0")
    for _, r in realizados:
        valor_total_processado += abs(r.valor_realizado)

    valor_total_conciliado = Decimal("0")
    valor_total_divergente = Decimal("0")
    for item, _ in itens_div:
        if item.valor_realizado is None:
            continue
        if item.status == "conciliado":
            valor_total_conciliado += item.valor_realizado
        elif item.status == "divergente":
            valor_total_divergente += item.valor_realizado

    return ResultadoMotor(
        quantidade_conciliados=qtd_conciliados,
        quantidade_divergentes=qtd_divergentes,
        quantidade_pendentes=qtd_pendentes,
        valor_total_processado=valor_total_processado,
        valor_total_conciliado=valor_total_conciliado,
        valor_total_divergente=valor_total_divergente,
    )
