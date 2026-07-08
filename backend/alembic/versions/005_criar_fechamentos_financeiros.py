"""criar tabela fechamentos_financeiros

Revision ID: 005
Revises: 004
Create Date: 2026-06-06

"""
from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")


def upgrade() -> None:
    op.execute(f"""
        DO $$ BEGIN
            CREATE TYPE {SCHEMA}.status_fechamento AS ENUM (
                'rascunho', 'arquivos_enviados', 'em_processamento',
                'processado', 'com_divergencias', 'aprovado', 'erro', 'cancelado'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    op.create_table(
        "fechamentos_financeiros",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("criado_por_usuario_id", sa.UUID(), nullable=False),
        sa.Column("aprovado_por_usuario_id", sa.UUID(), nullable=True),
        sa.Column("titulo", sa.String(255), nullable=False),
        sa.Column("tipo_conciliacao", sa.String(100), nullable=False),
        sa.Column("periodo_inicio", sa.Date(), nullable=False),
        sa.Column("periodo_fim", sa.Date(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="rascunho"),
        sa.Column("quantidade_registros", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("quantidade_conciliados", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("quantidade_divergentes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("aprovado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_fechamentos_financeiros"),
        sa.ForeignKeyConstraint(["empresa_id"], [f"{SCHEMA}.empresas.id"], name="fk_fechamentos_empresa", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["criado_por_usuario_id"], [f"{SCHEMA}.usuarios.id"], name="fk_fechamentos_criado_por", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["aprovado_por_usuario_id"], [f"{SCHEMA}.usuarios.id"], name="fk_fechamentos_aprovado_por", ondelete="RESTRICT"),
        schema=SCHEMA,
    )

    op.create_index("ix_fechamentos_empresa_id", "fechamentos_financeiros", ["empresa_id"], schema=SCHEMA)
    op.create_index("ix_fechamentos_status", "fechamentos_financeiros", ["status"], schema=SCHEMA)
    op.create_index("ix_fechamentos_periodo", "fechamentos_financeiros", ["periodo_inicio", "periodo_fim"], schema=SCHEMA)

    op.execute(f"ALTER TABLE {SCHEMA}.fechamentos_financeiros ENABLE ROW LEVEL SECURITY")

    op.execute(f"""
        CREATE POLICY "fechamentos_select" ON {SCHEMA}.fechamentos_financeiros
        FOR SELECT TO authenticated
        USING (
            EXISTS (
                SELECT 1 FROM {SCHEMA}.usuarios u
                WHERE u.usuario_auth_id = auth.uid()
                  AND u.ativo = true
                  AND (u.perfil = 'admin_ia16' OR u.empresa_id = empresa_id)
            )
        )
    """)
    op.execute(f"""
        CREATE POLICY "fechamentos_insert" ON {SCHEMA}.fechamentos_financeiros
        FOR INSERT TO authenticated
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM {SCHEMA}.usuarios u
                WHERE u.usuario_auth_id = auth.uid()
                  AND u.ativo = true
                  AND (u.perfil = 'admin_ia16' OR u.empresa_id = empresa_id)
            )
        )
    """)
    op.execute(f"""
        CREATE POLICY "fechamentos_update" ON {SCHEMA}.fechamentos_financeiros
        FOR UPDATE TO authenticated
        USING (
            EXISTS (
                SELECT 1 FROM {SCHEMA}.usuarios u
                WHERE u.usuario_auth_id = auth.uid()
                  AND u.ativo = true
                  AND (u.perfil = 'admin_ia16' OR u.empresa_id = empresa_id)
            )
        )
    """)


def downgrade() -> None:
    op.execute(f'DROP POLICY IF EXISTS "fechamentos_update" ON {SCHEMA}.fechamentos_financeiros')
    op.execute(f'DROP POLICY IF EXISTS "fechamentos_insert" ON {SCHEMA}.fechamentos_financeiros')
    op.execute(f'DROP POLICY IF EXISTS "fechamentos_select" ON {SCHEMA}.fechamentos_financeiros')
    op.drop_index("ix_fechamentos_periodo", table_name="fechamentos_financeiros", schema=SCHEMA)
    op.drop_index("ix_fechamentos_status", table_name="fechamentos_financeiros", schema=SCHEMA)
    op.drop_index("ix_fechamentos_empresa_id", table_name="fechamentos_financeiros", schema=SCHEMA)
    op.drop_table("fechamentos_financeiros", schema=SCHEMA)
    op.execute(f"DROP TYPE IF EXISTS {SCHEMA}.status_fechamento")
