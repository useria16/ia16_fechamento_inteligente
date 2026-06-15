"""sprint 8A — adiciona motivo_reabertura em fechamentos_financeiros

Revision ID: 014
Revises: 013
Create Date: 2026-06-09

Adiciona:
  - motivo_reabertura text nullable (auditoria da reabertura do fechamento)
"""
from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa

revision: str = "014"
down_revision: Union[str, None] = "013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")


def upgrade() -> None:
    op.add_column(
        "fechamentos_financeiros",
        sa.Column("motivo_reabertura", sa.Text(), nullable=True),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("fechamentos_financeiros", "motivo_reabertura", schema=SCHEMA)
