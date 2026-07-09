"""clientes: separação entre grupo/cliente e empresa/CNPJ conciliável

Revision ID: 019
Revises: 018
Create Date: 2026-07-09

"""
from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision: str = "019"
down_revision: Union[str, None] = "018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")


def upgrade() -> None:
    # 1. Cria tabela clientes
    op.create_table(
        "clientes",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("nome", sa.String(255), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name="pk_clientes"),
        schema=SCHEMA,
    )
    op.create_index("ix_clientes_nome", "clientes", ["nome"], schema=SCHEMA)

    # 2. Adiciona cliente_id em empresas (nullable para migração)
    op.add_column(
        "empresas",
        sa.Column(
            "cliente_id",
            sa.UUID(),
            sa.ForeignKey(f"{SCHEMA}.clientes.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_empresas_cliente_id", "empresas", ["cliente_id"], schema=SCHEMA)

    # 3. Adiciona cliente_id em usuarios (nullable — admin_ia16 fica sem cliente)
    op.add_column(
        "usuarios",
        sa.Column(
            "cliente_id",
            sa.UUID(),
            sa.ForeignKey(f"{SCHEMA}.clientes.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_usuarios_cliente_id", "usuarios", ["cliente_id"], schema=SCHEMA)

    # 4. Migração de dados: cria um cliente por empresa existente e associa
    conn = op.get_bind()
    empresas = conn.execute(
        text(f"SELECT id, nome FROM {SCHEMA}.empresas")
    ).fetchall()

    for empresa_id, empresa_nome in empresas:
        resultado = conn.execute(
            text(
                f"INSERT INTO {SCHEMA}.clientes (nome, ativo) "
                f"VALUES (:nome, true) RETURNING id"
            ),
            {"nome": empresa_nome},
        )
        cliente_id = resultado.scalar()

        conn.execute(
            text(f"UPDATE {SCHEMA}.empresas SET cliente_id = :cid WHERE id = :eid"),
            {"cid": cliente_id, "eid": str(empresa_id)},
        )
        conn.execute(
            text(
                f"UPDATE {SCHEMA}.usuarios "
                f"SET cliente_id = :cid "
                f"WHERE empresa_id = :eid"
            ),
            {"cid": cliente_id, "eid": str(empresa_id)},
        )

    # 5. RLS para clientes — apenas admin_ia16 acessa
    op.execute(f"ALTER TABLE {SCHEMA}.clientes ENABLE ROW LEVEL SECURITY")
    op.execute(f"""
        CREATE POLICY "clientes_select" ON {SCHEMA}.clientes
        FOR SELECT TO authenticated
        USING (
          EXISTS (
            SELECT 1 FROM {SCHEMA}.usuarios u
            WHERE u.usuario_auth_id = auth.uid()
              AND u.ativo = true
              AND (
                u.perfil = 'admin_ia16'
                OR u.cliente_id = {SCHEMA}.clientes.id
              )
          )
        )
    """)
    op.execute(f"""
        CREATE POLICY "clientes_insert" ON {SCHEMA}.clientes
        FOR INSERT TO authenticated
        WITH CHECK (
          EXISTS (
            SELECT 1 FROM {SCHEMA}.usuarios u
            WHERE u.usuario_auth_id = auth.uid()
              AND u.ativo = true
              AND u.perfil = 'admin_ia16'
          )
        )
    """)
    op.execute(f"""
        CREATE POLICY "clientes_update" ON {SCHEMA}.clientes
        FOR UPDATE TO authenticated
        USING (
          EXISTS (
            SELECT 1 FROM {SCHEMA}.usuarios u
            WHERE u.usuario_auth_id = auth.uid()
              AND u.ativo = true
              AND u.perfil = 'admin_ia16'
          )
        )
    """)


def downgrade() -> None:
    op.execute(f"DROP POLICY IF EXISTS \"clientes_update\" ON {SCHEMA}.clientes")
    op.execute(f"DROP POLICY IF EXISTS \"clientes_insert\" ON {SCHEMA}.clientes")
    op.execute(f"DROP POLICY IF EXISTS \"clientes_select\" ON {SCHEMA}.clientes")
    op.execute(f"ALTER TABLE {SCHEMA}.clientes DISABLE ROW LEVEL SECURITY")

    op.drop_index("ix_usuarios_cliente_id", table_name="usuarios", schema=SCHEMA)
    op.drop_column("usuarios", "cliente_id", schema=SCHEMA)

    op.drop_index("ix_empresas_cliente_id", table_name="empresas", schema=SCHEMA)
    op.drop_column("empresas", "cliente_id", schema=SCHEMA)

    op.drop_index("ix_clientes_nome", table_name="clientes", schema=SCHEMA)
    op.drop_table("clientes", schema=SCHEMA)
