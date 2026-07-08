import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel

TipoArquivo = Literal[
    "extrato_bancario", "relatorio_vendas", "relatorio_recebiveis",
    "planilha_interna", "taxas_adquirente", "outro",
]

StatusArquivo = Literal["enviado", "lido", "invalido", "processado", "erro"]

ModoRetencao = Literal["somente_memoria", "temporario", "persistente"]


class ArquivoResponse(BaseModel):
    id: uuid.UUID
    empresa_id: uuid.UUID
    conciliacao_id: uuid.UUID
    nome_original: str
    tipo_arquivo: str
    status: str
    tamanho_bytes: int
    # Campos de retenção — nullable para arquivos anteriores à migration 009
    modo_retencao: ModoRetencao | None = None
    arquivo_persistido: bool = True
    expira_em: datetime | None = None
    excluido_em: datetime | None = None
    hash_arquivo: str | None = None
    metadados: dict[str, Any] = {}
    arquivo_disponivel: bool = True
    permitir_download_original: bool = True
    permitir_reprocessamento_sem_reenvio: bool = True
    criado_em: datetime

    model_config = {"from_attributes": True}
