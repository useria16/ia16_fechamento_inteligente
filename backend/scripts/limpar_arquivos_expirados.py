"""
Script para limpeza manual de arquivos expirados.

Uso:
  cd backend
  DB_SCHEMA=ia16_fechamento_dev python -m scripts.limpar_arquivos_expirados

  # Ou via Makefile:
  make limpar-arquivos-expirados
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.retencao_arquivos_service import limpar_arquivos_expirados


def main() -> None:
    db = SessionLocal()
    try:
        print("Iniciando limpeza de arquivos expirados...")
        resultado = limpar_arquivos_expirados(db)
        print(f"  Candidatos encontrados : {resultado['total_candidatos']}")
        print(f"  Excluídos com sucesso  : {resultado['excluidos']}")
        print(f"  Falhas                 : {resultado['falhas']}")
        print(f"  Executado em           : {resultado['executado_em']}")
        if resultado["falhas"] > 0:
            print("AVISO: houve falhas. Verifique logs_retencao_arquivos no banco.")
            sys.exit(1)
        print("Limpeza concluída.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
