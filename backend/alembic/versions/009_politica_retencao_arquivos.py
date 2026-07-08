"""sprint 5.5 — politica retencao arquivos

Revision ID: 009
Revises: 008
Create Date: 2026-06-08

Cria:
  - enum modo_retencao_arquivo
  - função atualizar_coluna_atualizado_em()
  - tabela politicas_retencao_arquivos + índices + trigger + RLS
  - tabela logs_retencao_arquivos + índices + RLS
  - novas colunas em arquivos_enviados + índices
  - política padrão para empresas existentes
  - configuração da Daxx (ILIKE '%Daxx%')
"""
from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ENUM as PgEnum

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")


def upgrade() -> None:
    # Tipo PgEnum referenciando enum já criado no banco (create_type=False evita DDL)
    modo_retencao_type = PgEnum(
        "somente_memoria", "temporario", "persistente",
        name="modo_retencao_arquivo",
        schema=SCHEMA,
        create_type=False,
    )

    # ── 1. Enum modo_retencao_arquivo ────────────────────────────────────────
    op.execute(f"""
        DO $$ BEGIN
            CREATE TYPE {SCHEMA}.modo_retencao_arquivo AS ENUM (
                'somente_memoria', 'temporario', 'persistente'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # ── 2. Função de trigger para atualizado_em ──────────────────────────────
    op.execute(f"""
        CREATE OR REPLACE FUNCTION {SCHEMA}.atualizar_coluna_atualizado_em()
        RETURNS trigger AS $$
        BEGIN
            NEW.atualizado_em = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # ── 3. Tabela politicas_retencao_arquivos ─────────────────────────────────
    op.create_table(
        "politicas_retencao_arquivos",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("modo_retencao", modo_retencao_type, nullable=False, server_default="temporario"),
        sa.Column("salvar_arquivo_original", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("salvar_resultado_processado", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("salvar_linhas_processadas", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("salvar_metadados", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("tempo_retencao_horas", sa.Integer(), nullable=True),
        sa.Column("excluir_arquivo_original_apos_processamento", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("permitir_download_original", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("permitir_reprocessamento_sem_reenvio", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_politicas_retencao_arquivos"),
        sa.ForeignKeyConstraint(
            ["empresa_id"], [f"{SCHEMA}.empresas.id"],
            name="fk_politicas_retencao_empresa", ondelete="CASCADE",
        ),
        sa.UniqueConstraint("empresa_id", name="uq_politicas_retencao_arquivos_empresa"),
        sa.CheckConstraint(
            "tempo_retencao_horas IS NULL OR tempo_retencao_horas > 0",
            name="ck_politicas_retencao_tempo_valido",
        ),
        sa.CheckConstraint(
            "modo_retencao <> 'temporario' OR tempo_retencao_horas IS NOT NULL",
            name="ck_politicas_retencao_temporario_com_tempo",
        ),
        schema=SCHEMA,
    )

    op.create_index(
        "idx_politicas_retencao_arquivos_empresa_id",
        "politicas_retencao_arquivos", ["empresa_id"], schema=SCHEMA,
    )
    op.create_index(
        "idx_politicas_retencao_arquivos_modo_retencao",
        "politicas_retencao_arquivos", ["modo_retencao"], schema=SCHEMA,
    )
    op.create_index(
        "idx_politicas_retencao_arquivos_ativo",
        "politicas_retencao_arquivos", ["ativo"], schema=SCHEMA,
    )

    op.execute(f"ALTER TABLE {SCHEMA}.politicas_retencao_arquivos ENABLE ROW LEVEL SECURITY")
    op.execute(f"""
        CREATE POLICY "politicas_retencao_select" ON {SCHEMA}.politicas_retencao_arquivos
        FOR SELECT TO authenticated
        USING (
            ({SCHEMA}.usuario_atual()).perfil = 'admin_ia16'
            OR empresa_id = ({SCHEMA}.usuario_atual()).empresa_id
        )
    """)
    op.execute(f"""
        CREATE POLICY "politicas_retencao_insert" ON {SCHEMA}.politicas_retencao_arquivos
        FOR INSERT TO authenticated
        WITH CHECK (({SCHEMA}.usuario_atual()).perfil = 'admin_ia16')
    """)
    op.execute(f"""
        CREATE POLICY "politicas_retencao_update" ON {SCHEMA}.politicas_retencao_arquivos
        FOR UPDATE TO authenticated
        USING (({SCHEMA}.usuario_atual()).perfil = 'admin_ia16')
    """)

    op.execute(f"""
        CREATE TRIGGER trg_politicas_retencao_arquivos_atualizado_em
        BEFORE UPDATE ON {SCHEMA}.politicas_retencao_arquivos
        FOR EACH ROW
        EXECUTE FUNCTION {SCHEMA}.atualizar_coluna_atualizado_em()
    """)

    # ── 4. Tabela logs_retencao_arquivos ─────────────────────────────────────
    op.create_table(
        "logs_retencao_arquivos",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("arquivo_id", sa.UUID(), nullable=True),
        sa.Column("evento", sa.Text(), nullable=False),
        sa.Column("mensagem", sa.Text(), nullable=False),
        sa.Column("detalhes", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_logs_retencao_arquivos"),
        sa.ForeignKeyConstraint(
            ["empresa_id"], [f"{SCHEMA}.empresas.id"],
            name="fk_logs_retencao_empresa", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["arquivo_id"], [f"{SCHEMA}.arquivos_enviados.id"],
            name="fk_logs_retencao_arquivo", ondelete="SET NULL",
        ),
        sa.CheckConstraint(
            "evento IN ("
            "'arquivo_agendado_para_exclusao',"
            "'arquivo_excluido_por_retencao',"
            "'falha_ao_excluir_arquivo',"
            "'arquivo_nao_encontrado_no_bucket',"
            "'arquivo_marcado_como_expirado'"
            ")",
            name="ck_logs_retencao_arquivos_evento",
        ),
        schema=SCHEMA,
    )

    op.create_index(
        "idx_logs_retencao_arquivos_empresa_id",
        "logs_retencao_arquivos", ["empresa_id"], schema=SCHEMA,
    )
    op.create_index(
        "idx_logs_retencao_arquivos_arquivo_id",
        "logs_retencao_arquivos", ["arquivo_id"], schema=SCHEMA,
    )
    op.create_index(
        "idx_logs_retencao_arquivos_evento",
        "logs_retencao_arquivos", ["evento"], schema=SCHEMA,
    )
    op.create_index(
        "idx_logs_retencao_arquivos_criado_em",
        "logs_retencao_arquivos", ["criado_em"], schema=SCHEMA, postgresql_ops={"criado_em": "DESC"},
    )

    op.execute(f"ALTER TABLE {SCHEMA}.logs_retencao_arquivos ENABLE ROW LEVEL SECURITY")
    op.execute(f"""
        CREATE POLICY "logs_retencao_select" ON {SCHEMA}.logs_retencao_arquivos
        FOR SELECT TO authenticated
        USING (
            ({SCHEMA}.usuario_atual()).perfil = 'admin_ia16'
            OR empresa_id = ({SCHEMA}.usuario_atual()).empresa_id
        )
    """)
    op.execute(f"""
        CREATE POLICY "logs_retencao_insert" ON {SCHEMA}.logs_retencao_arquivos
        FOR INSERT TO authenticated
        WITH CHECK (
            ({SCHEMA}.usuario_atual()).perfil = 'admin_ia16'
            OR empresa_id = ({SCHEMA}.usuario_atual()).empresa_id
        )
    """)

    # ── 5. Novas colunas em arquivos_enviados ─────────────────────────────────
    op.add_column(
        "arquivos_enviados",
        sa.Column("modo_retencao", modo_retencao_type, nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "arquivos_enviados",
        sa.Column("arquivo_persistido", sa.Boolean(), nullable=False, server_default=sa.true()),
        schema=SCHEMA,
    )
    op.add_column(
        "arquivos_enviados",
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "arquivos_enviados",
        sa.Column("excluido_em", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "arquivos_enviados",
        sa.Column("hash_arquivo", sa.Text(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "arquivos_enviados",
        sa.Column("metadados", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        schema=SCHEMA,
    )

    op.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_arquivos_enviados_modo_retencao
        ON {SCHEMA}.arquivos_enviados (modo_retencao)
    """)
    op.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_arquivos_enviados_expira_em
        ON {SCHEMA}.arquivos_enviados (expira_em)
        WHERE expira_em IS NOT NULL AND excluido_em IS NULL
    """)
    op.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_arquivos_enviados_arquivo_persistido
        ON {SCHEMA}.arquivos_enviados (arquivo_persistido)
    """)
    op.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_arquivos_enviados_excluido_em
        ON {SCHEMA}.arquivos_enviados (excluido_em)
    """)

    # ── 6. Política padrão para empresas existentes ───────────────────────────
    op.execute(f"""
        INSERT INTO {SCHEMA}.politicas_retencao_arquivos (
            empresa_id, modo_retencao,
            salvar_arquivo_original, salvar_resultado_processado,
            salvar_linhas_processadas, salvar_metadados,
            tempo_retencao_horas, excluir_arquivo_original_apos_processamento,
            permitir_download_original, permitir_reprocessamento_sem_reenvio, ativo
        )
        SELECT
            e.id, 'temporario',
            true, true, false, true,
            168, false, true, true, true
        FROM {SCHEMA}.empresas e
        WHERE NOT EXISTS (
            SELECT 1 FROM {SCHEMA}.politicas_retencao_arquivos p
            WHERE p.empresa_id = e.id
        )
    """)

    # ── 7. Garantir configuração Daxx ─────────────────────────────────────────
    op.execute(f"""
        UPDATE {SCHEMA}.politicas_retencao_arquivos p
        SET
            modo_retencao = 'temporario',
            salvar_arquivo_original = true,
            salvar_resultado_processado = true,
            salvar_linhas_processadas = false,
            salvar_metadados = true,
            tempo_retencao_horas = 168,
            excluir_arquivo_original_apos_processamento = false,
            permitir_download_original = true,
            permitir_reprocessamento_sem_reenvio = true,
            ativo = true,
            atualizado_em = now()
        FROM {SCHEMA}.empresas e
        WHERE p.empresa_id = e.id
          AND e.nome ILIKE '%Daxx%'
    """)


def downgrade() -> None:
    # Políticas RLS e triggers
    op.execute(f'DROP POLICY IF EXISTS "logs_retencao_insert" ON {SCHEMA}.logs_retencao_arquivos')
    op.execute(f'DROP POLICY IF EXISTS "logs_retencao_select" ON {SCHEMA}.logs_retencao_arquivos')
    op.execute(f'DROP POLICY IF EXISTS "politicas_retencao_update" ON {SCHEMA}.politicas_retencao_arquivos')
    op.execute(f'DROP POLICY IF EXISTS "politicas_retencao_insert" ON {SCHEMA}.politicas_retencao_arquivos')
    op.execute(f'DROP POLICY IF EXISTS "politicas_retencao_select" ON {SCHEMA}.politicas_retencao_arquivos')
    op.execute(f'DROP TRIGGER IF EXISTS trg_politicas_retencao_arquivos_atualizado_em ON {SCHEMA}.politicas_retencao_arquivos')

    # Índices de arquivos_enviados
    op.execute(f"DROP INDEX IF EXISTS {SCHEMA}.idx_arquivos_enviados_excluido_em")
    op.execute(f"DROP INDEX IF EXISTS {SCHEMA}.idx_arquivos_enviados_arquivo_persistido")
    op.execute(f"DROP INDEX IF EXISTS {SCHEMA}.idx_arquivos_enviados_expira_em")
    op.execute(f"DROP INDEX IF EXISTS {SCHEMA}.idx_arquivos_enviados_modo_retencao")

    # Colunas de arquivos_enviados
    op.drop_column("arquivos_enviados", "metadados", schema=SCHEMA)
    op.drop_column("arquivos_enviados", "hash_arquivo", schema=SCHEMA)
    op.drop_column("arquivos_enviados", "excluido_em", schema=SCHEMA)
    op.drop_column("arquivos_enviados", "expira_em", schema=SCHEMA)
    op.drop_column("arquivos_enviados", "arquivo_persistido", schema=SCHEMA)
    op.drop_column("arquivos_enviados", "modo_retencao", schema=SCHEMA)

    # Índices
    op.drop_index("idx_logs_retencao_arquivos_criado_em", table_name="logs_retencao_arquivos", schema=SCHEMA)
    op.drop_index("idx_logs_retencao_arquivos_evento", table_name="logs_retencao_arquivos", schema=SCHEMA)
    op.drop_index("idx_logs_retencao_arquivos_arquivo_id", table_name="logs_retencao_arquivos", schema=SCHEMA)
    op.drop_index("idx_logs_retencao_arquivos_empresa_id", table_name="logs_retencao_arquivos", schema=SCHEMA)
    op.drop_index("idx_politicas_retencao_arquivos_ativo", table_name="politicas_retencao_arquivos", schema=SCHEMA)
    op.drop_index("idx_politicas_retencao_arquivos_modo_retencao", table_name="politicas_retencao_arquivos", schema=SCHEMA)
    op.drop_index("idx_politicas_retencao_arquivos_empresa_id", table_name="politicas_retencao_arquivos", schema=SCHEMA)

    # Tabelas
    op.drop_table("logs_retencao_arquivos", schema=SCHEMA)
    op.drop_table("politicas_retencao_arquivos", schema=SCHEMA)

    # Função e enum
    op.execute(f"DROP FUNCTION IF EXISTS {SCHEMA}.atualizar_coluna_atualizado_em()")
    op.execute(f"DROP TYPE IF EXISTS {SCHEMA}.modo_retencao_arquivo")
