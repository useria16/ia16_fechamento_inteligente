import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, String, Text, Integer, Date, DateTime, Numeric, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.core.database import Base

SCHEMA = settings.DB_SCHEMA


class LancamentoExtratoAnotado(Base):
    __tablename__ = "lancamentos_extrato_anotado"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.empresas.id", ondelete="RESTRICT"), nullable=False)
    fechamento_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.fechamentos_financeiros.id", ondelete="RESTRICT"), nullable=False)
    arquivo_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.arquivos_enviados.id", ondelete="RESTRICT"), nullable=False)

    data_lancamento: Mapped[date] = mapped_column(Date(), nullable=False)
    descricao_banco: Mapped[str] = mapped_column(Text(), nullable=False)
    razao_social: Mapped[str | None] = mapped_column(Text(), nullable=True)
    documento: Mapped[str | None] = mapped_column(String(50), nullable=True)
    valor: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    tipo_movimento: Mapped[str] = mapped_column(String(10), nullable=False)
    saldo: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    linha_origem: Mapped[int | None] = mapped_column(Integer(), nullable=True)

    # Campos anotáveis
    categoria: Mapped[str | None] = mapped_column(Text(), nullable=True)
    descricao_negocio: Mapped[str | None] = mapped_column(Text(), nullable=True)
    nf_doc: Mapped[str | None] = mapped_column(String(100), nullable=True)
    valor_nf_doc: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    observacao: Mapped[str | None] = mapped_column(Text(), nullable=True)

    # Sugestão automática
    categoria_sugerida: Mapped[str | None] = mapped_column(Text(), nullable=True)
    confianca_sugestao: Mapped[Decimal | None] = mapped_column(Numeric(4, 3), nullable=True)

    status_revisao: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pendente")
    metadados: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    # Conferência com fluxo de caixa (nullable — lançamentos sem fluxo ficam como None)
    previsto_no_fluxo: Mapped[bool | None] = mapped_column(Boolean(), nullable=True)
    tipo_conferencia_fluxo: Mapped[str | None] = mapped_column(String(30), nullable=True)
    confianca_conferencia: Mapped[Decimal | None] = mapped_column(Numeric(4, 3), nullable=True)
    observacao_sistema: Mapped[str | None] = mapped_column(Text(), nullable=True)
    data_prevista: Mapped[date | None] = mapped_column(Date(), nullable=True)
    valor_previsto: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    descricao_prevista: Mapped[str | None] = mapped_column(Text(), nullable=True)

    atualizado_por_usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.usuarios.id", ondelete="SET NULL"), nullable=True
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
