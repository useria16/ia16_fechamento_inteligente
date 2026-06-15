import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import String, DateTime, Text, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.core.database import Base

SCHEMA = settings.DB_SCHEMA


class LogProcessamento(Base):
    __tablename__ = "logs_processamento"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.empresas.id", ondelete="RESTRICT"), nullable=False)
    fechamento_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.fechamentos_financeiros.id", ondelete="RESTRICT"), nullable=False)
    arquivo_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    nivel: Mapped[str] = mapped_column(String(20), nullable=False, server_default="info")
    evento: Mapped[str] = mapped_column(String(100), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text(), nullable=False)
    detalhes: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
