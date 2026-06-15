import uuid
from datetime import datetime

from sqlalchemy import Boolean, Integer, DateTime, String, text, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, ENUM as PgEnum
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


class PoliticaRetencaoArquivo(Base):
    __tablename__ = "politicas_retencao_arquivos"
    __table_args__ = (
        UniqueConstraint("empresa_id", name="uq_politicas_retencao_arquivos_empresa"),
        CheckConstraint(
            "tempo_retencao_horas IS NULL OR tempo_retencao_horas > 0",
            name="ck_politicas_retencao_tempo_valido",
        ),
        CheckConstraint(
            "modo_retencao <> 'temporario' OR tempo_retencao_horas IS NOT NULL",
            name="ck_politicas_retencao_temporario_com_tempo",
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    modo_retencao: Mapped[str] = mapped_column(ModoRetencaoEnum, nullable=False, server_default="temporario")

    salvar_arquivo_original: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default=text("true"))
    salvar_resultado_processado: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default=text("true"))
    salvar_linhas_processadas: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default=text("false"))
    salvar_metadados: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default=text("true"))

    tempo_retencao_horas: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    excluir_arquivo_original_apos_processamento: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default=text("false"))

    permitir_download_original: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default=text("true"))
    permitir_reprocessamento_sem_reenvio: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default=text("true"))

    ativo: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default=text("true"))

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
