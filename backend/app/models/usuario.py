import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    empresa_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{settings.DB_SCHEMA}.empresas.id", ondelete="RESTRICT"),
        nullable=True,
    )
    usuario_auth_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    perfil: Mapped[str] = mapped_column(
        Enum(
            "admin_ia16",
            "cliente_admin",
            "cliente_operador",
            name="perfil_usuario",
            schema=settings.DB_SCHEMA,
        ),
        nullable=False,
    )
    ativo: Mapped[bool] = mapped_column(
        Boolean(),
        server_default=text("true"),
        nullable=False,
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )

    empresa: Mapped["Empresa"] = relationship("Empresa", lazy="select")  # noqa: F821
