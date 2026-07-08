import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import String, Text, Integer, Date, DateTime, Numeric, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.core.database import Base

SCHEMA = settings.DB_SCHEMA


class ItemConciliacao(Base):
    __tablename__ = "itens_conciliacao"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.empresas.id", ondelete="RESTRICT"), nullable=False)
    fechamento_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.fechamentos_financeiros.id", ondelete="RESTRICT"), nullable=False)
    arquivo_extrato_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    arquivo_fluxo_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    tipo_item: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    tipo_movimento: Mapped[str] = mapped_column(String(20), nullable=False)

    data_prevista: Mapped[date | None] = mapped_column(Date(), nullable=True)
    data_realizada: Mapped[date | None] = mapped_column(Date(), nullable=True)
    descricao_prevista: Mapped[str | None] = mapped_column(Text(), nullable=True)
    descricao_realizada: Mapped[str | None] = mapped_column(Text(), nullable=True)

    valor_previsto: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_realizado: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    diferenca_valor: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    diferenca_dias: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    confianca: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)

    metadados: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
