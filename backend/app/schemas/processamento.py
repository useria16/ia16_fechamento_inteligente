import uuid
from decimal import Decimal

from pydantic import BaseModel, computed_field

from app.schemas.fechamento import StatusFechamento


class ResultadoProcessamento(BaseModel):
    conciliacao_id: uuid.UUID
    status: StatusFechamento
    quantidade_arquivos: int
    quantidade_registros: int
    quantidade_conciliados: int
    quantidade_divergentes: int
    quantidade_pendentes: int
    valor_total_processado: Decimal
    mensagem_processamento: str

    @computed_field
    @property
    def pronto_para_revisao(self) -> bool:
        return self.status in ("processado", "com_divergencias")

    model_config = {"from_attributes": True}
