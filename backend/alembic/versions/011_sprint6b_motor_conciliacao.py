"""sprint 6B — motor de conciliação: itens e divergências

Revision ID: 011
Revises: 010
Create Date: 2026-06-09

Cria:
  - tabela itens_conciliacao com RLS
  - tabela divergencias_conciliacao com RLS (FK → itens ON DELETE CASCADE)
  - coluna quantidade_pendentes em fechamentos_financeiros
"""
from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")


def upgrade() -> None:
    # ── 1. quantidade_pendentes em fechamentos_financeiros ────────────────
    op.add_column(
        "fechamentos_financeiros",
        sa.Column("quantidade_pendentes", sa.Integer(), nullable=False, server_default=sa.text("0")),
        schema=SCHEMA,
    )

    # ── 2. itens_conciliacao ──────────────────────────────────────────────
    op.create_table(
        "itens_conciliacao",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("fechamento_id", sa.UUID(), nullable=False),
        sa.Column("arquivo_extrato_id", sa.UUID(), nullable=True),
        sa.Column("arquivo_fluxo_id", sa.UUID(), nullable=True),
        sa.Column("tipo_item", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("tipo_movimento", sa.String(20), nullable=False),
        sa.Column("data_prevista", sa.Date(), nullable=True),
        sa.Column("data_realizada", sa.Date(), nullable=True),
        sa.Column("descricao_prevista", sa.Text(), nullable=True),
        sa.Column("descricao_realizada", sa.Text(), nullable=True),
        sa.Column("valor_previsto", sa.Numeric(15, 2), nullable=True),
        sa.Column("valor_realizado", sa.Numeric(15, 2), nullable=True),
        sa.Column("diferenca_valor", sa.Numeric(15, 2), nullable=True),
        sa.Column("diferenca_dias", sa.Integer(), nullable=True),
        sa.Column("confianca", sa.Numeric(5, 4), nullable=True),
        sa.Column("metadados", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_itens_conciliacao"),
        sa.ForeignKeyConstraint(
            ["empresa_id"], [f"{SCHEMA}.empresas.id"],
            name="fk_itens_conciliacao_empresa", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["fechamento_id"], [f"{SCHEMA}.fechamentos_financeiros.id"],
            name="fk_itens_conciliacao_fechamento", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["arquivo_extrato_id"], [f"{SCHEMA}.arquivos_enviados.id"],
            name="fk_itens_conciliacao_extrato", ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["arquivo_fluxo_id"], [f"{SCHEMA}.arquivos_enviados.id"],
            name="fk_itens_conciliacao_fluxo", ondelete="SET NULL",
        ),
        schema=SCHEMA,
    )

    op.create_index("ix_itens_conciliacao_fechamento_id", "itens_conciliacao", ["fechamento_id"], schema=SCHEMA)
    op.create_index("ix_itens_conciliacao_empresa_id", "itens_conciliacao", ["empresa_id"], schema=SCHEMA)
    op.create_index("ix_itens_conciliacao_status", "itens_conciliacao", ["status"], schema=SCHEMA)

    op.execute(f"ALTER TABLE {SCHEMA}.itens_conciliacao ENABLE ROW LEVEL SECURITY")
    op.execute(f"""
        CREATE POLICY "itens_conciliacao_select" ON {SCHEMA}.itens_conciliacao
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
        CREATE POLICY "itens_conciliacao_insert" ON {SCHEMA}.itens_conciliacao
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
        CREATE POLICY "itens_conciliacao_delete" ON {SCHEMA}.itens_conciliacao
        FOR DELETE TO authenticated
        USING (
            EXISTS (
                SELECT 1 FROM {SCHEMA}.usuarios u
                WHERE u.usuario_auth_id = auth.uid()
                  AND u.ativo = true
                  AND (u.perfil = 'admin_ia16' OR u.empresa_id = empresa_id)
            )
        )
    """)

    # ── 3. divergencias_conciliacao ───────────────────────────────────────
    op.create_table(
        "divergencias_conciliacao",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("fechamento_id", sa.UUID(), nullable=False),
        sa.Column("item_conciliacao_id", sa.UUID(), nullable=False),
        sa.Column("tipo_divergencia", sa.String(50), nullable=False),
        sa.Column("severidade", sa.String(20), nullable=False, server_default="media"),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("valor_previsto", sa.Numeric(15, 2), nullable=True),
        sa.Column("valor_realizado", sa.Numeric(15, 2), nullable=True),
        sa.Column("diferenca_valor", sa.Numeric(15, 2), nullable=True),
        sa.Column("data_prevista", sa.Date(), nullable=True),
        sa.Column("data_realizada", sa.Date(), nullable=True),
        sa.Column("diferenca_dias", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="aberta"),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.Column("metadados", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_divergencias_conciliacao"),
        sa.ForeignKeyConstraint(
            ["empresa_id"], [f"{SCHEMA}.empresas.id"],
            name="fk_divergencias_empresa", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["fechamento_id"], [f"{SCHEMA}.fechamentos_financeiros.id"],
            name="fk_divergencias_fechamento", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["item_conciliacao_id"], [f"{SCHEMA}.itens_conciliacao.id"],
            name="fk_divergencias_item", ondelete="CASCADE",
        ),
        schema=SCHEMA,
    )

    op.create_index("ix_divergencias_fechamento_id", "divergencias_conciliacao", ["fechamento_id"], schema=SCHEMA)
    op.create_index("ix_divergencias_empresa_id", "divergencias_conciliacao", ["empresa_id"], schema=SCHEMA)
    op.create_index("ix_divergencias_tipo", "divergencias_conciliacao", ["tipo_divergencia"], schema=SCHEMA)
    op.create_index("ix_divergencias_status", "divergencias_conciliacao", ["status"], schema=SCHEMA)

    op.execute(f"ALTER TABLE {SCHEMA}.divergencias_conciliacao ENABLE ROW LEVEL SECURITY")
    op.execute(f"""
        CREATE POLICY "divergencias_conciliacao_select" ON {SCHEMA}.divergencias_conciliacao
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
        CREATE POLICY "divergencias_conciliacao_insert" ON {SCHEMA}.divergencias_conciliacao
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
        CREATE POLICY "divergencias_conciliacao_delete" ON {SCHEMA}.divergencias_conciliacao
        FOR DELETE TO authenticated
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
    for policy in ["divergencias_conciliacao_delete", "divergencias_conciliacao_insert", "divergencias_conciliacao_select"]:
        op.execute(f'DROP POLICY IF EXISTS "{policy}" ON {SCHEMA}.divergencias_conciliacao')
    op.drop_index("ix_divergencias_status", table_name="divergencias_conciliacao", schema=SCHEMA)
    op.drop_index("ix_divergencias_tipo", table_name="divergencias_conciliacao", schema=SCHEMA)
    op.drop_index("ix_divergencias_empresa_id", table_name="divergencias_conciliacao", schema=SCHEMA)
    op.drop_index("ix_divergencias_fechamento_id", table_name="divergencias_conciliacao", schema=SCHEMA)
    op.drop_table("divergencias_conciliacao", schema=SCHEMA)

    for policy in ["itens_conciliacao_delete", "itens_conciliacao_insert", "itens_conciliacao_select"]:
        op.execute(f'DROP POLICY IF EXISTS "{policy}" ON {SCHEMA}.itens_conciliacao')
    op.drop_index("ix_itens_conciliacao_status", table_name="itens_conciliacao", schema=SCHEMA)
    op.drop_index("ix_itens_conciliacao_empresa_id", table_name="itens_conciliacao", schema=SCHEMA)
    op.drop_index("ix_itens_conciliacao_fechamento_id", table_name="itens_conciliacao", schema=SCHEMA)
    op.drop_table("itens_conciliacao", schema=SCHEMA)

    op.drop_column("fechamentos_financeiros", "quantidade_pendentes", schema=SCHEMA)
