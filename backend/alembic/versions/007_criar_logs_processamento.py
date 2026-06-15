"""criar tabela logs_processamento

Revision ID: 007
Revises: 006
Create Date: 2026-06-08

"""
from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")


def upgrade() -> None:
    op.create_table(
        "logs_processamento",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("fechamento_id", sa.UUID(), nullable=False),
        sa.Column("arquivo_id", sa.UUID(), nullable=True),
        sa.Column("nivel", sa.String(20), nullable=False, server_default="info"),
        sa.Column("evento", sa.String(100), nullable=False),
        sa.Column("mensagem", sa.Text(), nullable=False),
        sa.Column("detalhes", JSONB, nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_logs_processamento"),
        sa.ForeignKeyConstraint(
            ["empresa_id"], [f"{SCHEMA}.empresas.id"],
            name="fk_logs_empresa", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["fechamento_id"], [f"{SCHEMA}.fechamentos_financeiros.id"],
            name="fk_logs_fechamento", ondelete="RESTRICT",
        ),
        schema=SCHEMA,
    )

    op.create_index("ix_logs_fechamento_id", "logs_processamento", ["fechamento_id"], schema=SCHEMA)
    op.create_index("ix_logs_empresa_id", "logs_processamento", ["empresa_id"], schema=SCHEMA)
    op.create_index("ix_logs_criado_em", "logs_processamento", ["criado_em"], schema=SCHEMA)

    op.execute(f"ALTER TABLE {SCHEMA}.logs_processamento ENABLE ROW LEVEL SECURITY")

    op.execute(f"""
        CREATE POLICY "logs_select" ON {SCHEMA}.logs_processamento
        FOR SELECT TO authenticated
        USING (
            ({SCHEMA}.usuario_atual()).perfil = 'admin_ia16'
            OR empresa_id = ({SCHEMA}.usuario_atual()).empresa_id
        )
    """)
    op.execute(f"""
        CREATE POLICY "logs_insert" ON {SCHEMA}.logs_processamento
        FOR INSERT TO authenticated
        WITH CHECK (
            ({SCHEMA}.usuario_atual()).perfil = 'admin_ia16'
            OR empresa_id = ({SCHEMA}.usuario_atual()).empresa_id
        )
    """)


def downgrade() -> None:
    op.execute(f'DROP POLICY IF EXISTS "logs_insert" ON {SCHEMA}.logs_processamento')
    op.execute(f'DROP POLICY IF EXISTS "logs_select" ON {SCHEMA}.logs_processamento')
    op.drop_index("ix_logs_criado_em", table_name="logs_processamento", schema=SCHEMA)
    op.drop_index("ix_logs_empresa_id", table_name="logs_processamento", schema=SCHEMA)
    op.drop_index("ix_logs_fechamento_id", table_name="logs_processamento", schema=SCHEMA)
    op.drop_table("logs_processamento", schema=SCHEMA)
