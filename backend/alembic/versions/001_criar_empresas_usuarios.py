"""criar tabelas empresas e usuarios

Revision ID: 001
Revises:
Create Date: 2026-06-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "empresas",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("cnpj", sa.String(14), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ativa", "inativa", name="status_empresa"),
            nullable=False,
            server_default="ativa",
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
        sa.PrimaryKeyConstraint("id", name="pk_empresas"),
        sa.UniqueConstraint("cnpj", name="uq_empresas_cnpj"),
    )
    op.create_index("ix_empresas_cnpj", "empresas", ["cnpj"])

    op.create_table(
        "usuarios",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("empresa_id", sa.UUID(), nullable=True),
        sa.Column("usuario_auth_id", sa.UUID(), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column(
            "perfil",
            sa.Enum(
                "admin_ia16",
                "cliente_admin",
                "cliente_operador",
                name="perfil_usuario",
            ),
            nullable=False,
        ),
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
        sa.PrimaryKeyConstraint("id", name="pk_usuarios"),
        sa.UniqueConstraint("usuario_auth_id", name="uq_usuarios_auth_id"),
        sa.UniqueConstraint("email", name="uq_usuarios_email"),
        sa.ForeignKeyConstraint(
            ["empresa_id"],
            ["empresas.id"],
            name="fk_usuarios_empresa",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["usuario_auth_id"],
            ["auth.users.id"],
            name="fk_usuarios_auth",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"])
    op.create_index("ix_usuarios_empresa_id", "usuarios", ["empresa_id"])


def downgrade() -> None:
    op.drop_index("ix_usuarios_empresa_id", table_name="usuarios")
    op.drop_index("ix_usuarios_email", table_name="usuarios")
    op.drop_table("usuarios")
    op.drop_index("ix_empresas_cnpj", table_name="empresas")
    op.drop_table("empresas")
    op.execute("DROP TYPE perfil_usuario")
    op.execute("DROP TYPE status_empresa")
