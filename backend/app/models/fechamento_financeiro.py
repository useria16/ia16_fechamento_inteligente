import uuid
from decimal import Decimal
from datetime import datetime, date

from sqlalchemy import String, Text, DateTime, Date, Integer, Numeric, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database import Base

SCHEMA = settings.DB_SCHEMA


class FechamentoFinanceiro(Base):
    __tablename__ = "fechamentos_financeiros"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.empresas.id", ondelete="RESTRICT"), nullable=False)
    criado_por_usuario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.usuarios.id", ondelete="RESTRICT"), nullable=False)
    aprovado_por_usuario_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.usuarios.id", ondelete="RESTRICT"), nullable=True)

    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo_conciliacao: Mapped[str] = mapped_column(String(100), nullable=False)
    periodo_inicio: Mapped[date] = mapped_column(Date(), nullable=False)
    periodo_fim: Mapped[date] = mapped_column(Date(), nullable=False)

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="rascunho",
    )

    quantidade_registros: Mapped[int] = mapped_column(Integer(), nullable=False, server_default=text("0"))
    quantidade_conciliados: Mapped[int] = mapped_column(Integer(), nullable=False, server_default=text("0"))
    quantidade_divergentes: Mapped[int] = mapped_column(Integer(), nullable=False, server_default=text("0"))
    quantidade_pendentes: Mapped[int] = mapped_column(Integer(), nullable=False, server_default=text("0"))

    valor_total_processado: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, server_default=text("0"))
    valor_total_conciliado: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, server_default=text("0"))
    valor_total_divergente: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, server_default=text("0"))

    observacao_aprovacao: Mapped[str | None] = mapped_column(Text(), nullable=True)
    aprovado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reaberto_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reaberto_por_usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.usuarios.id", ondelete="SET NULL"), nullable=True
    )
    motivo_reabertura: Mapped[str | None] = mapped_column(Text(), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)

    empresa = relationship("Empresa", foreign_keys=[empresa_id])
