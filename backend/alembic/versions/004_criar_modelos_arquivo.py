"""criar tabela modelos_arquivo

Revision ID: 004
Revises: 003
Create Date: 2026-06-06

"""
from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")


def upgrade() -> None:
    op.create_table(
        "modelos_arquivo",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column(
            "tipo_arquivo",
            sa.Enum(
                "extrato_bancario",
                "relatorio_vendas",
                "relatorio_recebiveis",
                "planilha_interna",
                "taxas_adquirente",
                "outro",
                name="tipo_arquivo",
            ),
            nullable=False,
        ),
        sa.Column("mapeamento_colunas", postgresql.JSONB(), nullable=False),
        sa.Column(
            "ativo",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_modelos_arquivo"),
        sa.ForeignKeyConstraint(
            ["empresa_id"],
            ["empresas.id"],
            name="fk_modelos_arquivo_empresa",
            ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_modelos_arquivo_empresa_id", "modelos_arquivo", ["empresa_id"])

    op.execute(f"ALTER TABLE {SCHEMA}.modelos_arquivo ENABLE ROW LEVEL SECURITY")

    op.execute(f"""
        CREATE POLICY "modelos_arquivo_select" ON {SCHEMA}.modelos_arquivo
        FOR SELECT TO authenticated
        USING (
          ({SCHEMA}.usuario_atual()).perfil = 'admin_ia16'
          OR empresa_id = ({SCHEMA}.usuario_atual()).empresa_id
        )
    """)
    op.execute(f"""
        CREATE POLICY "modelos_arquivo_insert" ON {SCHEMA}.modelos_arquivo
        FOR INSERT TO authenticated
        WITH CHECK (
          ({SCHEMA}.usuario_atual()).perfil IN ('admin_ia16', 'cliente_admin')
        )
    """)
    op.execute(f"""
        CREATE POLICY "modelos_arquivo_update" ON {SCHEMA}.modelos_arquivo
        FOR UPDATE TO authenticated
        USING (
          ({SCHEMA}.usuario_atual()).perfil = 'admin_ia16'
          OR empresa_id = ({SCHEMA}.usuario_atual()).empresa_id
        )
    """)


def downgrade() -> None:
    op.execute(f"DROP POLICY IF EXISTS \"modelos_arquivo_update\" ON {SCHEMA}.modelos_arquivo")
    op.execute(f"DROP POLICY IF EXISTS \"modelos_arquivo_insert\" ON {SCHEMA}.modelos_arquivo")
    op.execute(f"DROP POLICY IF EXISTS \"modelos_arquivo_select\" ON {SCHEMA}.modelos_arquivo")
    op.execute(f"ALTER TABLE {SCHEMA}.modelos_arquivo DISABLE ROW LEVEL SECURITY")
    op.drop_index("ix_modelos_arquivo_empresa_id", table_name="modelos_arquivo")
    op.drop_table("modelos_arquivo")
    op.execute("DROP TYPE tipo_arquivo")
