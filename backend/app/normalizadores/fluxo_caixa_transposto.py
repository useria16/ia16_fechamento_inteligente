"""
Normalizador para fluxo de caixa em formato transposto diário.

Estrutura esperada:
  - Aba configurável (configurada no modelo, mas detecção é por estrutura)
  - Linha 1: datas nas colunas a partir de D
  - Coluna A: nível da categoria (1, 2, ou vazio)
  - Coluna B: nome da categoria
  - Células: valor previsto para aquela categoria naquela data

Regras:
  - Linhas cujo nome começa com prefixo de totalização (ex: "TOTAL") são ignoradas
  - Células None, zero ou string são ignoradas
  - Coluna ACUMULADO (não é date) é ignorada automaticamente
  - Valor positivo = entrada, negativo = saída
"""
import io
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import openpyxl
from openpyxl.utils import column_index_from_string, get_column_letter


@dataclass
class LancamentoPrevisto:
    data_prevista: date
    descricao_prevista: str
    categoria: str
    valor_previsto: Decimal
    tipo_movimento: str  # "entrada" | "saida"
    arquivo_id: str
    linha_origem: int
    coluna_origem: str
    metadados: dict[str, Any] = field(default_factory=dict)


def normalizar(conteudo: bytes, config: dict, arquivo_id: str) -> list[LancamentoPrevisto]:
    """
    Normaliza um fluxo de caixa transposto e retorna lista de lançamentos previstos.

    Args:
        conteudo:   Bytes do arquivo .xlsx
        config:     mapeamento_colunas do ModeloArquivo
        arquivo_id: UUID do ArquivoEnviado (como string)
    """
    aba_nome_config    = config.get("aba")
    linha_datas        = config.get("linha_datas", 1)
    col_cat_idx        = column_index_from_string(config.get("coluna_categoria", "B"))
    col_inicio_val_idx = column_index_from_string(config.get("coluna_inicio_valores", "D"))
    prefixos_total     = [p.upper() for p in config.get("prefixos_totalizacao", ["TOTAL"])]

    wb = openpyxl.load_workbook(io.BytesIO(conteudo), read_only=True, data_only=True)

    # Selecionar aba: usar config se existir, senão detectar pela estrutura
    ws = _selecionar_aba(wb, aba_nome_config, linha_datas, col_inicio_val_idx)
    if ws is None:
        wb.close()
        raise ValueError(
            f"Nenhuma aba com estrutura de fluxo transposto encontrada. "
            f"Aba esperada: '{aba_nome_config}', abas disponíveis: {wb.sheetnames}"
        )

    # Ler mapa de datas da linha 1 (col_idx → date)
    datas_por_coluna: dict[int, date] = {}
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i + 1 != linha_datas:
            continue
        for col_idx, val in enumerate(row, 1):
            if col_idx < col_inicio_val_idx:
                continue
            d = _val_para_date(val)
            if d is not None:
                datas_por_coluna[col_idx] = d
        break

    if not datas_por_coluna:
        wb.close()
        raise ValueError(
            f"Nenhuma data encontrada na linha {linha_datas} "
            f"a partir da coluna {get_column_letter(col_inicio_val_idx)}."
        )

    # Normalizar lançamentos
    previstos: list[LancamentoPrevisto] = []

    for i, row in enumerate(ws.iter_rows(values_only=True)):
        num_linha = i + 1
        if num_linha <= linha_datas:
            continue
        if len(row) < col_cat_idx:
            continue

        categoria_raw = row[col_cat_idx - 1]
        if categoria_raw is None:
            continue
        categoria = str(categoria_raw).strip()
        if not categoria:
            continue

        # Ignorar linhas de totalização
        if any(categoria.upper().startswith(p) for p in prefixos_total):
            continue

        for col_idx, data in datas_por_coluna.items():
            if col_idx > len(row):
                continue
            val = row[col_idx - 1]
            if val is None:
                continue

            valor = _parse_decimal(val)
            if valor is None or valor == 0:
                continue

            tipo_mov = "entrada" if valor > 0 else "saida"

            previstos.append(LancamentoPrevisto(
                data_prevista=data,
                descricao_prevista=categoria,
                categoria=categoria,
                valor_previsto=valor,
                tipo_movimento=tipo_mov,
                arquivo_id=arquivo_id,
                linha_origem=num_linha,
                coluna_origem=get_column_letter(col_idx),
                metadados={},
            ))

    wb.close()
    return previstos


def _selecionar_aba(wb, aba_nome: str | None, linha_datas: int, col_inicio_idx: int):
    """Retorna a worksheet correta: por nome se existir, senão pela estrutura."""
    if aba_nome and aba_nome in wb.sheetnames:
        return wb[aba_nome]

    # Detectar pela estrutura: sheet que tem datas em linha 1 a partir de col D
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        date_count = 0
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i + 1 != linha_datas:
                continue
            for col_idx, val in enumerate(row, 1):
                if col_idx >= col_inicio_idx and _val_para_date(val) is not None:
                    date_count += 1
            break
        if date_count >= 3:  # pelo menos 3 datas para ser candidato
            return ws
    return None


def _val_para_date(val: Any) -> date | None:
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    return None


def _parse_decimal(val: Any) -> Decimal | None:
    if val is None:
        return None
    try:
        d = Decimal(str(val)).normalize()
        return d if d != 0 else None
    except (InvalidOperation, ValueError):
        return None
