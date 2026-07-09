"""adicionar controle de troca obrigatoria de senha em usuarios

Revision ID: 018
Revises: 017
Create Date: 2026-07-08

"""
from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa

revision: str = "018"
down_revision: Union[str, None] = "017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column(
            "troca_senha_obrigatoria",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("usuarios", "troca_senha_obrigatoria", schema=SCHEMA)
