"""sprint — campo valor_nf_doc na tabela lancamentos_extrato_anotado

Revision ID: 017
Revises: 016
Create Date: 2026-06-10

Adiciona campo numérico para o valor associado à NF ou documento informado
pelo operador durante a revisão do extrato anotado.
Corresponde à coluna VALOR NF/DOC do modelo de planilha da Daxx.
"""
from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa

revision: str = "017"
down_revision: Union[str, None] = "016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")


def upgrade() -> None:
    op.add_column(
        "lancamentos_extrato_anotado",
        sa.Column("valor_nf_doc", sa.Numeric(15, 2), nullable=True),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("lancamentos_extrato_anotado", "valor_nf_doc", schema=SCHEMA)
