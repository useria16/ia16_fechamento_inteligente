import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Text, DateTime, CheckConstraint, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.core.database import Base

SCHEMA = settings.DB_SCHEMA

EVENTOS_VALIDOS = (
    "arquivo_agendado_para_exclusao",
    "arquivo_excluido_por_retencao",
    "falha_ao_excluir_arquivo",
    "arquivo_nao_encontrado_no_bucket",
    "arquivo_marcado_como_expirado",
)


class LogRetencaoArquivo(Base):
    __tablename__ = "logs_retencao_arquivos"
    __table_args__ = (
        CheckConstraint(
            f"evento IN {str(EVENTOS_VALIDOS)}",
            name="ck_logs_retencao_arquivos_evento",
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    arquivo_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    evento: Mapped[str] = mapped_column(Text(), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text(), nullable=False)
    detalhes: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
