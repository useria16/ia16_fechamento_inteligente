"""sprint 6A — modelos de arquivo e normalização

Revision ID: 010
Revises: 009
Create Date: 2026-06-09

Alterações:
  - empresa_id nullable em modelos_arquivo (NULL = modelo global do sistema)
  - Adiciona: codigo, tipo_estrutura, descricao
  - Índice único em codigo (parcial: WHERE codigo IS NOT NULL)
  - Seeds globais: extrato_bancario_tabular_linha_10 e fluxo_caixa_transposto_diario
"""
from typing import Sequence, Union
import os
import json

from alembic import op
import sqlalchemy as sa

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")

SEED_EXTRATO = {
    "nome": "Extrato Bancário Tabular — Linha 10",
    "codigo": "extrato_bancario_tabular_linha_10",
    "tipo_arquivo": "extrato_bancario",
    "tipo_estrutura": "tabular",
    "descricao": (
        "Extrato bancário em formato tabular com metadados nas primeiras linhas "
        "e cabeçalho de dados na linha 10. Colunas: Data, Lançamento, Razão Social, "
        "CPF/CNPJ, Valor (R$), Saldo (R$). Linhas de saldo são ignoradas na normalização."
    ),
    "mapeamento_colunas": {
        "aba": "Lançamentos",
        "linha_cabecalho": 10,
        "linha_inicio_dados": 11,
        "coluna_data": "A",
        "coluna_descricao_operacao": "B",
        "coluna_razao_social": "C",
        "coluna_documento": "D",
        "coluna_valor": "E",
        "coluna_saldo": "F",
        "colunas_esperadas": ["Data", "Lançamento", "Razão Social", "CPF/CNPJ", "Valor (R$)", "Saldo (R$)"],
        "filtro_linhas_saldo": ["SALDO ANTERIOR", "SALDO TOTAL DISPONÍVEL DIA", "SALDO EM CONTA CORRENTE"],
    },
}

SEED_FLUXO = {
    "nome": "Fluxo de Caixa Transposto Diário",
    "codigo": "fluxo_caixa_transposto_diario",
    "tipo_arquivo": "planilha_interna",
    "tipo_estrutura": "transposto",
    "descricao": (
        "Fluxo de caixa com estrutura transposta: categorias nas linhas, "
        "datas nas colunas a partir da coluna D. Linha 1 contém as datas. "
        "Coluna A indica nível da categoria, coluna B contém o nome da categoria. "
        "Linhas com nome iniciando em TOTAL são ignoradas na normalização."
    ),
    "mapeamento_colunas": {
        "aba": "DAXX MIDIA PE",
        "linha_datas": 1,
        "coluna_nivel": "A",
        "coluna_categoria": "B",
        "coluna_inicio_valores": "D",
        "prefixos_totalizacao": ["TOTAL"],
    },
}


def upgrade() -> None:
    # ── 1. empresa_id nullable ────────────────────────────────────────────
    op.alter_column(
        "modelos_arquivo",
        "empresa_id",
        existing_type=sa.UUID(),
        nullable=True,
        schema=SCHEMA,
    )

    # ── 2. Novas colunas ──────────────────────────────────────────────────
    op.add_column(
        "modelos_arquivo",
        sa.Column("codigo", sa.String(100), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "modelos_arquivo",
        sa.Column("tipo_estrutura", sa.String(50), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "modelos_arquivo",
        sa.Column("descricao", sa.Text(), nullable=True),
        schema=SCHEMA,
    )

    # ── 3. Índice único parcial em codigo ─────────────────────────────────
    op.execute(f"""
        CREATE UNIQUE INDEX uq_modelos_arquivo_codigo
        ON {SCHEMA}.modelos_arquivo (codigo)
        WHERE codigo IS NOT NULL
    """)

    # ── 4. Seeds globais (empresa_id = NULL) ──────────────────────────────
    for seed in [SEED_EXTRATO, SEED_FLUXO]:
        op.execute(f"""
            INSERT INTO {SCHEMA}.modelos_arquivo
              (nome, codigo, tipo_arquivo, tipo_estrutura, descricao, mapeamento_colunas, ativo)
            VALUES (
              {_sql_str(seed["nome"])},
              {_sql_str(seed["codigo"])},
              {_sql_str(seed["tipo_arquivo"])},
              {_sql_str(seed["tipo_estrutura"])},
              {_sql_str(seed["descricao"])},
              {_sql_jsonb(seed["mapeamento_colunas"])},
              true
            )
            ON CONFLICT DO NOTHING
        """)


def downgrade() -> None:
    op.execute(f"""
        DELETE FROM {SCHEMA}.modelos_arquivo
        WHERE codigo IN ('extrato_bancario_tabular_linha_10', 'fluxo_caixa_transposto_diario')
    """)
    op.execute(f"DROP INDEX IF EXISTS {SCHEMA}.uq_modelos_arquivo_codigo")
    op.drop_column("modelos_arquivo", "descricao", schema=SCHEMA)
    op.drop_column("modelos_arquivo", "tipo_estrutura", schema=SCHEMA)
    op.drop_column("modelos_arquivo", "codigo", schema=SCHEMA)
    op.alter_column(
        "modelos_arquivo",
        "empresa_id",
        existing_type=sa.UUID(),
        nullable=False,
        schema=SCHEMA,
    )


def _sql_str(value: str) -> str:
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def _sql_jsonb(value: dict) -> str:
    escaped = json.dumps(value, ensure_ascii=False).replace("'", "''")
    return f"'{escaped}'::jsonb"
