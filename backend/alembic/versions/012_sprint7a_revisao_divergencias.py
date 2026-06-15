"""sprint 7A — revisão de divergências: resolvido_em, atualizado_por_usuario_id e RLS UPDATE

Revision ID: 012
Revises: 011
Create Date: 2026-06-09

Adiciona:
  - coluna resolvido_em em divergencias_conciliacao
  - coluna atualizado_por_usuario_id em divergencias_conciliacao
  - política RLS UPDATE em divergencias_conciliacao
"""
from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa

revision: str = "012"
down_revision: Union[str, None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")


def upgrade() -> None:
    # ── 1. resolvido_em ───────────────────────────────────────────────────
    op.add_column(
        "divergencias_conciliacao",
        sa.Column("resolvido_em", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )

    # ── 2. atualizado_por_usuario_id ──────────────────────────────────────
    op.add_column(
        "divergencias_conciliacao",
        sa.Column(
            "atualizado_por_usuario_id",
            sa.UUID(),
            sa.ForeignKey(f"{SCHEMA}.usuarios.id", ondelete="SET NULL"),
            nullable=True,
        ),
        schema=SCHEMA,
    )

    # ── 3. RLS UPDATE ─────────────────────────────────────────────────────
    op.execute(f"""
        CREATE POLICY "divergencias_conciliacao_update" ON {SCHEMA}.divergencias_conciliacao
        FOR UPDATE TO authenticated
        USING (
            ({SCHEMA}.usuario_atual()).perfil = 'admin_ia16'
            OR empresa_id = ({SCHEMA}.usuario_atual()).empresa_id
        )
        WITH CHECK (
            ({SCHEMA}.usuario_atual()).perfil = 'admin_ia16'
            OR empresa_id = ({SCHEMA}.usuario_atual()).empresa_id
        )
    """)


def downgrade() -> None:
    op.execute(
        f'DROP POLICY IF EXISTS "divergencias_conciliacao_update" ON {SCHEMA}.divergencias_conciliacao'
    )
    op.drop_column("divergencias_conciliacao", "atualizado_por_usuario_id", schema=SCHEMA)
    op.drop_column("divergencias_conciliacao", "resolvido_em", schema=SCHEMA)
