from app.core.config import settings
from app.core.database import Base

from app.models.empresa import Empresa  # noqa: F401
from app.models.usuario import Usuario  # noqa: F401
from app.models.fonte_dados import FonteDados  # noqa: F401
from app.models.modelo_arquivo import ModeloArquivo  # noqa: F401
from app.models.fechamento_financeiro import FechamentoFinanceiro  # noqa: F401
from app.models.arquivo_enviado import ArquivoEnviado  # noqa: F401
from app.models.log_processamento import LogProcessamento  # noqa: F401
from app.models.politica_retencao_arquivo import PoliticaRetencaoArquivo  # noqa: F401
from app.models.log_retencao_arquivo import LogRetencaoArquivo  # noqa: F401

SCHEMA = settings.DB_SCHEMA

__all__ = [
    "Base", "SCHEMA",
    "Empresa", "Usuario", "FonteDados", "ModeloArquivo",
    "FechamentoFinanceiro", "ArquivoEnviado",
    "LogProcessamento", "PoliticaRetencaoArquivo", "LogRetencaoArquivo",
]
