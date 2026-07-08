"""sprint 10B.2 — fluxo de referência no extrato anotado

Revision ID: 016
Revises: 015
Create Date: 2026-06-10

Adiciona colunas de conferência com o fluxo de caixa à tabela
lancamentos_extrato_anotado.

Todas as colunas são nullable para compatibilidade com lançamentos
existentes processados sem fluxo de caixa.
"""
from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa

revision: str = "016"
down_revision: Union[str, None] = "015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")


def upgrade() -> None:
    op.add_column(
        "lancamentos_extrato_anotado",
        sa.Column("previsto_no_fluxo", sa.Boolean(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "lancamentos_extrato_anotado",
        sa.Column("tipo_conferencia_fluxo", sa.String(30), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "lancamentos_extrato_anotado",
        sa.Column("confianca_conferencia", sa.Numeric(4, 3), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "lancamentos_extrato_anotado",
        sa.Column("observacao_sistema", sa.Text(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "lancamentos_extrato_anotado",
        sa.Column("data_prevista", sa.Date(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "lancamentos_extrato_anotado",
        sa.Column("valor_previsto", sa.Numeric(15, 2), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "lancamentos_extrato_anotado",
        sa.Column("descricao_prevista", sa.Text(), nullable=True),
        schema=SCHEMA,
    )

    op.create_check_constraint(
        "ck_tipo_conferencia_fluxo",
        "lancamentos_extrato_anotado",
        sa.text(
            "tipo_conferencia_fluxo IS NULL OR tipo_conferencia_fluxo IN ("
            "'encontrado','nao_encontrado','data_diferente',"
            "'valor_diferente','possivel_correspondencia','pendente_analise')"
        ),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_constraint("ck_tipo_conferencia_fluxo", "lancamentos_extrato_anotado", schema=SCHEMA, type_="check")
    for col in [
        "descricao_prevista", "valor_previsto", "data_prevista",
        "observacao_sistema", "confianca_conferencia",
        "tipo_conferencia_fluxo", "previsto_no_fluxo",
    ]:
        op.drop_column("lancamentos_extrato_anotado", col, schema=SCHEMA)
