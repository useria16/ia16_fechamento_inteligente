"""
Parser genérico de comentários de células para normalizadores de fluxo de caixa.

Extrai lançamentos individuais de texto livre quando possível.
Conservador: só desmembra quando encontrar valores monetários claros.
"""
import re
from decimal import Decimal, InvalidOperation
from typing import Any


# ── Regex ─────────────────────────────────────────────────────────────────────

# Datas em formatos comuns — usadas apenas para REMOVER antes de buscar valores
_RE_DATA = re.compile(r'\b\d{1,2}[/\.]\d{1,2}[/\.]\d{2,4}\b')

# TOTAL R$ 1.234,56
_RE_TOTAL_RS = re.compile(r'TOTAL\s+R\$\s*([\d\.]+,\d{2})', re.IGNORECASE)

# R$ 1.234,56 (exige centavos para ser conservador)
_RE_VALOR_RS = re.compile(r'R\$\s*([\d\.]+,\d{2})')

# + 1.234,56 ou + 1.234 no início ou após espaço (sem R$)
_RE_VALOR_MAIS = re.compile(r'(?:^|\s)\+\s*([\d\.]+(?:,\d{2})?)\b')

# Referências estruturadas
_RE_OC = re.compile(r'\bOC\s+([\w/]+)', re.IGNORECASE)
_RE_PI = re.compile(r'\bPI\s+(\d+)', re.IGNORECASE)
_RE_NF = re.compile(r'\bNF[\.;]?\s*(\d+)', re.IGNORECASE)
_RE_PP = re.compile(r'\bPP\s+(\d+)', re.IGNORECASE)

# Linhas de controle/saldo — nunca geram lançamentos
_CONTROLES = frozenset({
    'SALDO INICIAL', 'ENTRADAS', 'SAIDAS', 'SAÍDAS',
    'SALDO FINAL', 'TOTAL DISPONIBILIDADES',
})


# ── API pública ───────────────────────────────────────────────────────────────

def parsear_itens_comentario(texto: str) -> list[dict[str, Any]]:
    """
    Extrai itens individuais de um comentário de célula.

    Retorna lista de dicts com:
      - descricao (str)
      - valor (Decimal)
      - oc, pi, nf, pp (str | None)
      - linha_original (str)

    Retorna lista vazia se não encontrar itens confiáveis.
    """
    if not texto or not texto.strip():
        return []

    linhas = texto.split('\n')

    # Primeira linha costuma ser "Autor - data" — pular se não tiver valor monetário
    if linhas and not _tem_valor_monetario(linhas[0]):
        linhas = linhas[1:]

    itens: list[dict[str, Any]] = []

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue

        if _e_linha_controle(linha):
            continue

        # Formato sinalizado: + X.XXX - desc + X.XXX - desc (múltiplos na mesma linha)
        if _tem_prefixo_sinal(linha):
            sub = _extrair_itens_sinalizados(linha)
            if sub:
                itens.extend(sub)
                continue

        # Linha simples com R$
        item = _extrair_item_linha_rs(linha)
        if item:
            itens.append(item)

    return itens


# ── Extração por linha ────────────────────────────────────────────────────────

def _extrair_item_linha_rs(linha: str) -> dict[str, Any] | None:
    """Extrai item de linha com R$ ou TOTAL R$."""
    sem_datas = _RE_DATA.sub(' ', linha)

    total = _RE_TOTAL_RS.search(sem_datas)
    trecho_item = sem_datas[:total.start()] if total else sem_datas

    # Se a linha tem valor individual antes do TOTAL, o TOTAL é apenas conferência.
    m = _RE_VALOR_RS.search(trecho_item)
    if m:
        valor = _parse_valor_br(m.group(1))
        if valor:
            return _montar_item(linha, valor)

    # Quando só existe TOTAL R$, usar esse valor como valor do item.
    if total:
        valor = _parse_valor_br(total.group(1))
        if valor:
            return _montar_item(linha, valor)

    return None


def _extrair_itens_sinalizados(linha: str) -> list[dict[str, Any]]:
    """
    Divide linha com múltiplos blocos "+ valor - desc" em itens individuais.
    Ex: "+ 4.000 - João + 2.000 - Lucas"
    """
    sem_datas = _RE_DATA.sub(' ', linha)
    # Dividir antes de cada ocorrência de "+NUMERO"
    segmentos = re.split(r'(?=\+\s*[\d])', sem_datas)
    itens = []
    for seg in segmentos:
        seg = seg.strip()
        if not seg:
            continue
        m = _RE_VALOR_MAIS.search(seg)
        if m:
            valor = _parse_valor_br(m.group(1))
            if valor:
                # Linha original do segmento (aproximada)
                itens.append(_montar_item(seg, valor))
    return itens


# ── Montagem de item ──────────────────────────────────────────────────────────

def _montar_item(linha_original: str, valor: Decimal) -> dict[str, Any]:
    oc = m.group(1) if (m := _RE_OC.search(linha_original)) else None
    pi = m.group(1) if (m := _RE_PI.search(linha_original)) else None
    nf = m.group(1) if (m := _RE_NF.search(linha_original)) else None
    pp = m.group(1) if (m := _RE_PP.search(linha_original)) else None

    # Descrição: tudo antes do primeiro R$ ou sinal+número
    desc_match = re.split(r'R\$|\+\s*[\d]', linha_original)
    desc = desc_match[0].strip().strip('-. ')
    desc = re.sub(r'\s+', ' ', desc)
    if not desc:
        desc = linha_original[:80].strip()

    return {
        'descricao': desc,
        'valor': valor,
        'oc': oc,
        'pi': pi,
        'nf': nf,
        'pp': pp,
        'linha_original': linha_original,
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_valor_br(texto: str) -> Decimal | None:
    """Converte "1.234,56" → Decimal(1234.56). Retorna None se inválido."""
    if not texto:
        return None
    try:
        limpo = texto.strip().replace('.', '').replace(',', '.')
        d = Decimal(limpo)
        return d if d > 0 else None
    except (InvalidOperation, ValueError):
        return None


def _tem_valor_monetario(linha: str) -> bool:
    return bool(_RE_VALOR_RS.search(linha) or _RE_TOTAL_RS.search(linha))


def _e_linha_controle(linha: str) -> bool:
    upper = linha.upper()
    return any(ctrl in upper for ctrl in _CONTROLES)


def _tem_prefixo_sinal(linha: str) -> bool:
    return bool(re.match(r'^\s*\+', linha))
