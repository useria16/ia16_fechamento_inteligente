import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import String, Text, DateTime, Enum, Boolean, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.core.database import Base


class ModeloArquivo(Base):
    __tablename__ = "modelos_arquivo"
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
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    codigo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tipo_estrutura: Mapped[str | None] = mapped_column(String(50), nullable=True)
    descricao: Mapped[str | None] = mapped_column(Text(), nullable=True)
    tipo_arquivo: Mapped[str] = mapped_column(
        Enum(
            "extrato_bancario",
            "relatorio_vendas",
            "relatorio_recebiveis",
            "planilha_interna",
            "taxas_adquirente",
            "outro",
            name="tipo_arquivo",
            schema=settings.DB_SCHEMA,
        ),
        nullable=False,
    )
    mapeamento_colunas: Mapped[dict[str, Any]] = mapped_column(JSONB(), nullable=False)
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
