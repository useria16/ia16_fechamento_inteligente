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


class DivergenciaConciliacao(Base):
    __tablename__ = "divergencias_conciliacao"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.empresas.id", ondelete="RESTRICT"), nullable=False)
    fechamento_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.fechamentos_financeiros.id", ondelete="RESTRICT"), nullable=False)
    item_conciliacao_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.itens_conciliacao.id", ondelete="CASCADE"), nullable=False)

    tipo_divergencia: Mapped[str] = mapped_column(String(50), nullable=False)
    severidade: Mapped[str] = mapped_column(String(20), nullable=False, server_default="media")
    descricao: Mapped[str] = mapped_column(Text(), nullable=False)

    valor_previsto: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_realizado: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    diferenca_valor: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    data_prevista: Mapped[date | None] = mapped_column(Date(), nullable=True)
    data_realizada: Mapped[date | None] = mapped_column(Date(), nullable=True)
    diferenca_dias: Mapped[int | None] = mapped_column(Integer(), nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="aberta")
    observacao: Mapped[str | None] = mapped_column(Text(), nullable=True)
    metadados: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    resolvido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    atualizado_por_usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.usuarios.id", ondelete="SET NULL"), nullable=True
    )

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
