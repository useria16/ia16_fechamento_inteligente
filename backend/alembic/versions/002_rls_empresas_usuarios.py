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
    op.execute(f"ALTER TABLE {SCHEMA}.empresas ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {SCHEMA}.usuarios ENABLE ROW LEVEL SECURITY")

    # --- Políticas de empresas ---
    op.execute(f"""
        CREATE POLICY "empresas_select" ON {SCHEMA}.empresas
        FOR SELECT TO authenticated
        USING (
          EXISTS (
            SELECT 1 FROM {SCHEMA}.usuarios u
            WHERE u.usuario_auth_id = auth.uid()
              AND u.ativo = true
              AND (u.perfil = 'admin_ia16' OR u.empresa_id = {SCHEMA}.empresas.id)
          )
        )
    """)
    op.execute(f"""
        CREATE POLICY "empresas_insert" ON {SCHEMA}.empresas
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
        CREATE POLICY "empresas_update" ON {SCHEMA}.empresas
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

    # --- Políticas de usuários ---
    op.execute(f"""
        CREATE POLICY "usuarios_select" ON {SCHEMA}.usuarios
        FOR SELECT TO authenticated
        USING (
          EXISTS (
            SELECT 1 FROM {SCHEMA}.usuarios u
            WHERE u.usuario_auth_id = auth.uid()
              AND u.ativo = true
              AND (u.perfil = 'admin_ia16' OR u.empresa_id = {SCHEMA}.usuarios.empresa_id)
          )
        )
    """)
    op.execute(f"""
        CREATE POLICY "usuarios_insert" ON {SCHEMA}.usuarios
        FOR INSERT TO authenticated
        WITH CHECK (
          EXISTS (
            SELECT 1 FROM {SCHEMA}.usuarios u
            WHERE u.usuario_auth_id = auth.uid()
              AND u.ativo = true
              AND u.perfil IN ('admin_ia16', 'cliente_admin')
          )
        )
    """)
    op.execute(f"""
        CREATE POLICY "usuarios_update" ON {SCHEMA}.usuarios
        FOR UPDATE TO authenticated
        USING (
          EXISTS (
            SELECT 1 FROM {SCHEMA}.usuarios u
            WHERE u.usuario_auth_id = auth.uid()
              AND u.ativo = true
              AND (u.perfil = 'admin_ia16' OR u.empresa_id = {SCHEMA}.usuarios.empresa_id)
          )
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
