"""sprint 8A — aprovação e reabertura de fechamento

Revision ID: 013
Revises: 012
Create Date: 2026-06-09

Adiciona em fechamentos_financeiros:
  - observacao_aprovacao text nullable
  - reaberto_em timestamptz nullable
  - reaberto_por_usuario_id uuid nullable FK usuarios(id)

Observação: aprovado_em e aprovado_por_usuario_id já existem desde a migration 001.
"""
from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa

revision: str = "013"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")


def upgrade() -> None:
    op.add_column(
        "fechamentos_financeiros",
        sa.Column("observacao_aprovacao", sa.Text(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "fechamentos_financeiros",
        sa.Column("reaberto_em", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "fechamentos_financeiros",
        sa.Column(
            "reaberto_por_usuario_id",
            sa.UUID(),
            sa.ForeignKey(f"{SCHEMA}.usuarios.id", ondelete="SET NULL"),
            nullable=True,
        ),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("fechamentos_financeiros", "reaberto_por_usuario_id", schema=SCHEMA)
    op.drop_column("fechamentos_financeiros", "reaberto_em", schema=SCHEMA)
    op.drop_column("fechamentos_financeiros", "observacao_aprovacao", schema=SCHEMA)
