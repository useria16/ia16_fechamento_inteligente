"""rls empresas e usuarios

Revision ID: 002
Revises: 001
Create Date: 2026-06-06

"""
from typing import Sequence, Union
import os

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "ia16_fechamento_dev")


def upgrade() -> None:
    op.execute(f"""
        CREATE OR REPLACE FUNCTION {SCHEMA}.usuario_atual()
        RETURNS {SCHEMA}.usuarios
        LANGUAGE sql SECURITY DEFINER STABLE
        AS $$
          SELECT * FROM {SCHEMA}.usuarios
          WHERE usuario_auth_id = auth.uid()
            AND ativo = true
          LIMIT 1;
        $$
    """)

    op.execute(f"ALTER TABLE {SCHEMA}.empresas ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {SCHEMA}.usuarios ENABLE ROW LEVEL SECURITY")

    op.execute(f"""
        CREATE POLICY "empresas_select" ON {SCHEMA}.empresas
        FOR SELECT TO authenticated
        USING (
          ({SCHEMA}.usuario_atual()).perfil = 'admin_ia16'
          OR ({SCHEMA}.usuario_atual()).empresa_id = id
        )
    """)
    op.execute(f"""
        CREATE POLICY "empresas_insert" ON {SCHEMA}.empresas
        FOR INSERT TO authenticated
        WITH CHECK (({SCHEMA}.usuario_atual()).perfil = 'admin_ia16')
    """)
    op.execute(f"""
        CREATE POLICY "empresas_update" ON {SCHEMA}.empresas
        FOR UPDATE TO authenticated
        USING (({SCHEMA}.usuario_atual()).perfil = 'admin_ia16')
    """)

    op.execute(f"""
        CREATE POLICY "usuarios_select" ON {SCHEMA}.usuarios
        FOR SELECT TO authenticated
        USING (
          ({SCHEMA}.usuario_atual()).perfil = 'admin_ia16'
          OR empresa_id = ({SCHEMA}.usuario_atual()).empresa_id
        )
    """)
    op.execute(f"""
        CREATE POLICY "usuarios_insert" ON {SCHEMA}.usuarios
        FOR INSERT TO authenticated
        WITH CHECK (
          ({SCHEMA}.usuario_atual()).perfil IN ('admin_ia16', 'cliente_admin')
        )
    """)
    op.execute(f"""
        CREATE POLICY "usuarios_update" ON {SCHEMA}.usuarios
        FOR UPDATE TO authenticated
        USING (
          ({SCHEMA}.usuario_atual()).perfil = 'admin_ia16'
          OR empresa_id = ({SCHEMA}.usuario_atual()).empresa_id
        )
    """)


def downgrade() -> None:
    op.execute(f"DROP POLICY IF EXISTS \"usuarios_update\" ON {SCHEMA}.usuarios")
    op.execute(f"DROP POLICY IF EXISTS \"usuarios_insert\" ON {SCHEMA}.usuarios")
    op.execute(f"DROP POLICY IF EXISTS \"usuarios_select\" ON {SCHEMA}.usuarios")
    op.execute(f"DROP POLICY IF EXISTS \"empresas_update\" ON {SCHEMA}.empresas")
    op.execute(f"DROP POLICY IF EXISTS \"empresas_insert\" ON {SCHEMA}.empresas")
    op.execute(f"DROP POLICY IF EXISTS \"empresas_select\" ON {SCHEMA}.empresas")
    op.execute(f"ALTER TABLE {SCHEMA}.usuarios DISABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {SCHEMA}.empresas DISABLE ROW LEVEL SECURITY")
    op.execute(f"DROP FUNCTION IF EXISTS {SCHEMA}.usuario_atual()")
