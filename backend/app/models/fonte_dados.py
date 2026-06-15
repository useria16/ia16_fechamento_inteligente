import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import String, DateTime, Enum, Boolean, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.core.database import Base


class FonteDados(Base):
    __tablename__ = "fontes_dados"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    empresa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{settings.DB_SCHEMA}.empresas.id", ondelete="RESTRICT"),
        nullable=False,
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[str] = mapped_column(
        Enum(
            "excel_manual",
            "banco",
            "adquirente",
            "erp",
            "google_drive",
            "outro",
            name="tipo_fonte_dados",
            schema=settings.DB_SCHEMA,
        ),
        nullable=False,
    )
    ativo: Mapped[bool] = mapped_column(
        Boolean(),
        server_default=text("true"),
        nullable=False,
    )
    configuracao: Mapped[dict[str, Any] | None] = mapped_column(JSONB(), nullable=True)
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
