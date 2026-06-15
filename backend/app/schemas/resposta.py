from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class Paginacao(BaseModel):
    pagina: int
    limite: int
    total: int
    total_paginas: int


class RespostaSucesso(BaseModel, Generic[T]):
    sucesso: bool = True
    dados: T
    mensagem: str = "Operação realizada com sucesso"


class RespostaLista(BaseModel, Generic[T]):
    sucesso: bool = True
    dados: list[T]
    paginacao: Paginacao


class ErroDetalhe(BaseModel):
    codigo: str
    mensagem: str
    detalhes: dict[str, Any] | None = None


class RespostaErro(BaseModel):
    sucesso: bool = False
    erro: ErroDetalhe


def paginar(total: int, pagina: int, limite: int) -> Paginacao:
    total_paginas = (total + limite - 1) // limite if total > 0 else 0
    return Paginacao(pagina=pagina, limite=limite, total=total, total_paginas=total_paginas)
