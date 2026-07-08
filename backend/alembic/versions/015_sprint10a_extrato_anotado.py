"""sprint 10A — tabela lancamentos_extrato_anotado

Revision ID: 015
Revises: 014
Create Date: 2026-06-10

Cria tabela para o fluxo de conciliação do tipo extrato_anotado:
  lançamentos bancários enriquecidos manualmente pelo operador.
"""
from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "015"
down_revision: Union[str, None] = "014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")


def upgrade() -> None:
    op.create_table(
        "lancamentos_extrato_anotado",
        sa.Column("id", UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("empresa_id",   UUID(), sa.ForeignKey(f"{SCHEMA}.empresas.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("fechamento_id",UUID(), sa.ForeignKey(f"{SCHEMA}.fechamentos_financeiros.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("arquivo_id",   UUID(), sa.ForeignKey(f"{SCHEMA}.arquivos_enviados.id", ondelete="RESTRICT"), nullable=False),

        sa.Column("data_lancamento",    sa.Date(),         nullable=False),
        sa.Column("descricao_banco",    sa.Text(),         nullable=False),
        sa.Column("razao_social",       sa.Text(),         nullable=True),
        sa.Column("documento",          sa.String(50),     nullable=True),
        sa.Column("valor",              sa.Numeric(15, 2), nullable=False),
        sa.Column("tipo_movimento",     sa.String(10),     nullable=False),  # entrada | saida
        sa.Column("saldo",              sa.Numeric(15, 2), nullable=True),
        sa.Column("linha_origem",       sa.Integer(),      nullable=True),

        # Campos anotáveis pelo operador
        sa.Column("categoria",          sa.Text(),         nullable=True),
        sa.Column("descricao_negocio",  sa.Text(),         nullable=True),
        sa.Column("nf_doc",             sa.String(100),    nullable=True),
        sa.Column("observacao",         sa.Text(),         nullable=True),

        # Sugestão automática
        sa.Column("categoria_sugerida", sa.Text(),         nullable=True),
        sa.Column("confianca_sugestao", sa.Numeric(4, 3),  nullable=True),

        # Status de revisão
        sa.Column("status_revisao",     sa.String(20),     nullable=False, server_default="pendente"),

        sa.Column("metadados",          JSONB,             nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("atualizado_por_usuario_id", UUID(),
                  sa.ForeignKey(f"{SCHEMA}.usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("criado_em",          sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("atualizado_em",      sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),

        schema=SCHEMA,
    )

    op.create_index(
        "ix_lancamentos_extrato_anotado_fechamento",
        "lancamentos_extrato_anotado",
        ["fechamento_id"],
        schema=SCHEMA,
    )

    op.create_index(
        "ix_lancamentos_extrato_anotado_empresa",
        "lancamentos_extrato_anotado",
        ["empresa_id"],
        schema=SCHEMA,
    )

    # RLS
    op.execute(f"""
        ALTER TABLE {SCHEMA}.lancamentos_extrato_anotado ENABLE ROW LEVEL SECURITY;
    """)
    op.execute(f"""
        CREATE POLICY "lancamentos_extrato_anotado_select" ON {SCHEMA}.lancamentos_extrato_anotado
        FOR SELECT TO authenticated
        USING (
            EXISTS (
                SELECT 1 FROM {SCHEMA}.usuarios u
                WHERE u.usuario_auth_id = auth.uid()
                  AND u.ativo = true
                  AND (u.perfil = 'admin_ia16' OR u.empresa_id = empresa_id)
            )
        );
    """)
    op.execute(f"""
        CREATE POLICY "lancamentos_extrato_anotado_update" ON {SCHEMA}.lancamentos_extrato_anotado
        FOR UPDATE TO authenticated
        USING (
            EXISTS (
                SELECT 1 FROM {SCHEMA}.usuarios u
                WHERE u.usuario_auth_id = auth.uid()
                  AND u.ativo = true
                  AND (u.perfil = 'admin_ia16' OR u.empresa_id = empresa_id)
            )
        )
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM {SCHEMA}.usuarios u
                WHERE u.usuario_auth_id = auth.uid()
                  AND u.ativo = true
                  AND (u.perfil = 'admin_ia16' OR u.empresa_id = empresa_id)
            )
        );
    """)


def downgrade() -> None:
    op.execute(f'DROP POLICY IF EXISTS "lancamentos_extrato_anotado_update" ON {SCHEMA}.lancamentos_extrato_anotado')
    op.execute(f'DROP POLICY IF EXISTS "lancamentos_extrato_anotado_select" ON {SCHEMA}.lancamentos_extrato_anotado')
    op.drop_index("ix_lancamentos_extrato_anotado_empresa", table_name="lancamentos_extrato_anotado", schema=SCHEMA)
    op.drop_index("ix_lancamentos_extrato_anotado_fechamento", table_name="lancamentos_extrato_anotado", schema=SCHEMA)
    op.drop_table("lancamentos_extrato_anotado", schema=SCHEMA)
