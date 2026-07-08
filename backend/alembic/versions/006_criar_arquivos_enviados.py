"""criar tabela arquivos_enviados

Revision ID: 006
Revises: 005
Create Date: 2026-06-06

"""
from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")


def upgrade() -> None:
    op.create_table(
        "arquivos_enviados",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("fechamento_id", sa.UUID(), nullable=False),
        sa.Column("fonte_dados_id", sa.UUID(), nullable=True),
        sa.Column("modelo_arquivo_id", sa.UUID(), nullable=True),
        sa.Column("criado_por_usuario_id", sa.UUID(), nullable=False),
        sa.Column("nome_original", sa.String(500), nullable=False),
        sa.Column("nome_armazenado", sa.String(500), nullable=False),
        sa.Column("tipo_arquivo", sa.String(50), nullable=False),
        sa.Column("caminho_storage", sa.Text(), nullable=False),
        sa.Column("tamanho_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(50), nullable=False, server_default="enviado"),
        sa.Column("mensagem_erro", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_arquivos_enviados"),
        sa.ForeignKeyConstraint(["empresa_id"], [f"{SCHEMA}.empresas.id"], name="fk_arquivos_empresa", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["fechamento_id"], [f"{SCHEMA}.fechamentos_financeiros.id"], name="fk_arquivos_fechamento", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["criado_por_usuario_id"], [f"{SCHEMA}.usuarios.id"], name="fk_arquivos_criado_por", ondelete="RESTRICT"),
        schema=SCHEMA,
    )

    op.create_index("ix_arquivos_empresa_id", "arquivos_enviados", ["empresa_id"], schema=SCHEMA)
    op.create_index("ix_arquivos_fechamento_id", "arquivos_enviados", ["fechamento_id"], schema=SCHEMA)
    op.create_index("ix_arquivos_status", "arquivos_enviados", ["status"], schema=SCHEMA)

    op.execute(f"ALTER TABLE {SCHEMA}.arquivos_enviados ENABLE ROW LEVEL SECURITY")

    op.execute(f"""
        CREATE POLICY "arquivos_select" ON {SCHEMA}.arquivos_enviados
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
        CREATE POLICY "arquivos_insert" ON {SCHEMA}.arquivos_enviados
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
        CREATE POLICY "arquivos_delete" ON {SCHEMA}.arquivos_enviados
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
    op.execute(f'DROP POLICY IF EXISTS "arquivos_delete" ON {SCHEMA}.arquivos_enviados')
    op.execute(f'DROP POLICY IF EXISTS "arquivos_insert" ON {SCHEMA}.arquivos_enviados')
    op.execute(f'DROP POLICY IF EXISTS "arquivos_select" ON {SCHEMA}.arquivos_enviados')
    op.drop_index("ix_arquivos_status", table_name="arquivos_enviados", schema=SCHEMA)
    op.drop_index("ix_arquivos_fechamento_id", table_name="arquivos_enviados", schema=SCHEMA)
    op.drop_index("ix_arquivos_empresa_id", table_name="arquivos_enviados", schema=SCHEMA)
    op.drop_table("arquivos_enviados", schema=SCHEMA)
