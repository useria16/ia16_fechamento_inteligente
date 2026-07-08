import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import String, DateTime, BigInteger, Boolean, Text, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database import Base

SCHEMA = settings.DB_SCHEMA

ModoRetencaoEnum = PgEnum(
    "somente_memoria", "temporario", "persistente",
    name="modo_retencao_arquivo",
    schema=SCHEMA,
    create_type=False,
)


class ArquivoEnviado(Base):
    __tablename__ = "arquivos_enviados"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.empresas.id", ondelete="RESTRICT"), nullable=False)
    fechamento_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.fechamentos_financeiros.id", ondelete="RESTRICT"), nullable=False)
    fonte_dados_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    modelo_arquivo_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    criado_por_usuario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.usuarios.id", ondelete="RESTRICT"), nullable=False)

    nome_original: Mapped[str] = mapped_column(String(500), nullable=False)
    nome_armazenado: Mapped[str] = mapped_column(String(500), nullable=False)
    tipo_arquivo: Mapped[str] = mapped_column(String(50), nullable=False)
    caminho_storage: Mapped[str] = mapped_column(Text(), nullable=False)
    tamanho_bytes: Mapped[int] = mapped_column(BigInteger(), nullable=False, server_default=text("0"))
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="enviado")
    mensagem_erro: Mapped[str | None] = mapped_column(Text(), nullable=True)

    # Campos de retenção (adicionados na migration 009)
    modo_retencao: Mapped[str | None] = mapped_column(ModoRetencaoEnum, nullable=True)
    arquivo_persistido: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default=text("true"))
    expira_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    excluido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    hash_arquivo: Mapped[str | None] = mapped_column(Text(), nullable=True)
    metadados: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)

    empresa = relationship("Empresa", foreign_keys=[empresa_id])
    fechamento = relationship("FechamentoFinanceiro", foreign_keys=[fechamento_id])
