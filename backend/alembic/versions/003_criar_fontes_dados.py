"""criar tabela fontes_dados

Revision ID: 003
Revises: 002
Create Date: 2026-06-06

"""
from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")


def upgrade() -> None:
    op.create_table(
        "fontes_dados",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column(
            "tipo",
            sa.Enum(
                "excel_manual",
                "banco",
                "adquirente",
                "erp",
                "google_drive",
                "outro",
                name="tipo_fonte_dados",
            ),
            nullable=False,
        ),
        sa.Column(
            "ativo",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column("configuracao", postgresql.JSONB(), nullable=True),
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
        sa.PrimaryKeyConstraint("id", name="pk_fontes_dados"),
        sa.ForeignKeyConstraint(
            ["empresa_id"],
            ["empresas.id"],
            name="fk_fontes_dados_empresa",
            ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_fontes_dados_empresa_id", "fontes_dados", ["empresa_id"])

    op.execute(f"ALTER TABLE {SCHEMA}.fontes_dados ENABLE ROW LEVEL SECURITY")

    op.execute(f"""
        CREATE POLICY "fontes_dados_select" ON {SCHEMA}.fontes_dados
        FOR SELECT TO authenticated
        USING (
          ({SCHEMA}.usuario_atual()).perfil = 'admin_ia16'
          OR empresa_id = ({SCHEMA}.usuario_atual()).empresa_id
        )
    """)
    op.execute(f"""
        CREATE POLICY "fontes_dados_insert" ON {SCHEMA}.fontes_dados
        FOR INSERT TO authenticated
        WITH CHECK (
          ({SCHEMA}.usuario_atual()).perfil IN ('admin_ia16', 'cliente_admin')
        )
    """)
    op.execute(f"""
        CREATE POLICY "fontes_dados_update" ON {SCHEMA}.fontes_dados
        FOR UPDATE TO authenticated
        USING (
          ({SCHEMA}.usuario_atual()).perfil = 'admin_ia16'
          OR empresa_id = ({SCHEMA}.usuario_atual()).empresa_id
        )
    """)


def downgrade() -> None:
    op.execute(f"DROP POLICY IF EXISTS \"fontes_dados_update\" ON {SCHEMA}.fontes_dados")
    op.execute(f"DROP POLICY IF EXISTS \"fontes_dados_insert\" ON {SCHEMA}.fontes_dados")
    op.execute(f"DROP POLICY IF EXISTS \"fontes_dados_select\" ON {SCHEMA}.fontes_dados")
    op.execute(f"ALTER TABLE {SCHEMA}.fontes_dados DISABLE ROW LEVEL SECURITY")
    op.drop_index("ix_fontes_dados_empresa_id", table_name="fontes_dados")
    op.drop_table("fontes_dados")
    op.execute("DROP TYPE tipo_fonte_dados")
