"""
Serviço de normalização de arquivos.

Orquestra: download do Storage → detecção do modelo → normalização.
Retorna dados padronizados em memória (sem persistência de linhas brutas).
"""
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.arquivo_enviado import ArquivoEnviado
from app.models.modelo_arquivo import ModeloArquivo
from app.schemas.normalizacao import ResultadoDeteccao, ResultadoNormalizacaoArquivo
from app.services.detectores_modelo_arquivo_service import detectar_modelo

BUCKET = "arquivos-originais"


def baixar_conteudo(caminho: str) -> bytes:
    url = f"{settings.SUPABASE_URL}/storage/v1/object/{BUCKET}/{caminho}"
    headers = {"Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"}
    resp = httpx.get(url, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise ValueError(f"Falha ao baixar arquivo do Storage: HTTP {resp.status_code}")
    return resp.content


def normalizar_arquivo(
    arquivo: ArquivoEnviado,
    db: Session,
    conteudo: bytes | None = None,
) -> tuple[ResultadoDeteccao, ResultadoNormalizacaoArquivo | None]:
    """
    Detecta o modelo e normaliza o arquivo.

    Retorna:
        (ResultadoDeteccao, ResultadoNormalizacaoArquivo | None)
        Se detecção falhar, ResultadoNormalizacaoArquivo será None.
    """
    if conteudo is None:
        conteudo = baixar_conteudo(arquivo.caminho_storage)

    deteccao = detectar_modelo(conteudo, arquivo.tipo_arquivo, db)

    if not deteccao.detectado:
        return deteccao, None

    modelo = db.query(ModeloArquivo).filter(
        ModeloArquivo.id == deteccao.modelo_arquivo_id
    ).first()

    if not modelo:
        deteccao.detectado = False
        deteccao.motivos.append("Modelo detectado mas não encontrado no banco")
        return deteccao, None

    realizados, previstos = _executar_normalizacao(conteudo, modelo, str(arquivo.id))

    resultado = ResultadoNormalizacaoArquivo(
        arquivo_id=str(arquivo.id),
        tipo_arquivo=arquivo.tipo_arquivo,
        codigo_modelo=modelo.codigo or "",
        tipo_estrutura=modelo.tipo_estrutura or "",
        quantidade_registros=len(realizados) + len(previstos),
        realizados=realizados,
        previstos=previstos,
    )
    return deteccao, resultado


def _executar_normalizacao(
    conteudo: bytes,
    modelo: ModeloArquivo,
    arquivo_id: str,
) -> tuple[list, list]:
    """
    Despacha para o normalizador correto conforme tipo_estrutura do modelo.
    Retorna (realizados, previstos).
    """
    config = modelo.mapeamento_colunas or {}

    if modelo.tipo_estrutura == "tabular":
        from app.normalizadores.extrato_bancario_tabular import normalizar
        realizados = normalizar(conteudo, config, arquivo_id)
        return realizados, []

    if modelo.tipo_estrutura == "transposto":
        from app.normalizadores.fluxo_caixa_transposto import normalizar
        previstos = normalizar(conteudo, config, arquivo_id)
        return [], previstos

    raise ValueError(f"Normalizador não implementado para tipo_estrutura='{modelo.tipo_estrutura}'")
