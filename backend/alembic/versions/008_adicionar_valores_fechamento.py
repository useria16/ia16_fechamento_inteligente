"""adicionar campos de valor em fechamentos_financeiros

Revision ID: 008
Revises: 007
Create Date: 2026-06-08

"""
from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")


def upgrade() -> None:
    op.add_column(
        "fechamentos_financeiros",
        sa.Column("valor_total_processado", sa.Numeric(15, 2), nullable=False, server_default="0"),
        schema=SCHEMA,
    )
    op.add_column(
        "fechamentos_financeiros",
        sa.Column("valor_total_conciliado", sa.Numeric(15, 2), nullable=False, server_default="0"),
        schema=SCHEMA,
    )
    op.add_column(
        "fechamentos_financeiros",
        sa.Column("valor_total_divergente", sa.Numeric(15, 2), nullable=False, server_default="0"),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("fechamentos_financeiros", "valor_total_divergente", schema=SCHEMA)
    op.drop_column("fechamentos_financeiros", "valor_total_conciliado", schema=SCHEMA)
    op.drop_column("fechamentos_financeiros", "valor_total_processado", schema=SCHEMA)
