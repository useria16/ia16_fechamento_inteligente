"""
Script de reset para demonstração do fluxo extrato_anotado.

USO EXCLUSIVO EM AMBIENTE DE DESENVOLVIMENTO/PILOTO.
NÃO EXECUTAR EM PRODUÇÃO.

Uso:
    python scripts/dev/resetar_demo_extrato_anotado.py <conciliacao_id>

O script:
    1. Exibe o estado atual da conciliação.
    2. Imprime o que será alterado.
    3. Aguarda confirmação explícita antes de executar.
    4. Reseta o fechamento para status=com_divergencias.
    5. Zera todos os campos de aprovação.
    6. Marca todos os lançamentos como status_revisao=pendente.
    7. Limpa os campos anotados (categoria, descricao_negocio, nf_doc, observacao).
"""
import sys
import os

# Permite executar a partir da raiz do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid


def obter_engine():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "Variável DATABASE_URL não definida. "
            "Execute: export DATABASE_URL='postgresql://...' antes de rodar o script."
        )
    return create_engine(url)


def main():
    if len(sys.argv) != 2:
        print("Uso: python scripts/dev/resetar_demo_extrato_anotado.py <conciliacao_id>")
        sys.exit(1)

    conciliacao_id = sys.argv[1]
    try:
        uuid.UUID(conciliacao_id)
    except ValueError:
        print(f"Erro: '{conciliacao_id}' não é um UUID válido.")
        sys.exit(1)

    engine = obter_engine()
    Session = sessionmaker(bind=engine)

    with Session() as db:
        schema = os.environ.get("DB_SCHEMA", "ia16_fechamento_dev")

        row = db.execute(text(f"""
            SELECT id, titulo, tipo_conciliacao, status, aprovado_em, reaberto_em
            FROM {schema}.fechamentos_financeiros
            WHERE id = :id
        """), {"id": conciliacao_id}).fetchone()

        if not row:
            print(f"Erro: conciliação '{conciliacao_id}' não encontrada.")
            sys.exit(1)

        print("\n=== ESTADO ATUAL ===")
        print(f"  ID:               {row.id}")
        print(f"  Título:           {row.titulo}")
        print(f"  Tipo:             {row.tipo_conciliacao}")
        print(f"  Status:           {row.status}")
        print(f"  Aprovado em:      {row.aprovado_em}")
        print(f"  Reaberto em:      {row.reaberto_em}")

        contagem = db.execute(text(f"""
            SELECT status_revisao, COUNT(*) AS qtd
            FROM {schema}.lancamentos_extrato_anotado
            WHERE fechamento_id = :id
            GROUP BY status_revisao ORDER BY status_revisao
        """), {"id": conciliacao_id}).fetchall()

        print("\n=== LANÇAMENTOS POR STATUS ===")
        total = 0
        for c in contagem:
            print(f"  {c.status_revisao:<15} {c.qtd}")
            total += c.qtd
        print(f"  {'TOTAL':<15} {total}")

        print("\n=== ALTERAÇÕES QUE SERÃO FEITAS ===")
        print(f"  fechamentos_financeiros.status               → com_divergencias")
        print(f"  fechamentos_financeiros.aprovado_em          → NULL")
        print(f"  fechamentos_financeiros.aprovado_por_usuario_id → NULL")
        print(f"  fechamentos_financeiros.observacao_aprovacao → NULL")
        print(f"  fechamentos_financeiros.reaberto_em          → NULL")
        print(f"  fechamentos_financeiros.reaberto_por_usuario_id → NULL")
        print(f"  lancamentos_extrato_anotado.status_revisao   → pendente (todos)")
        print(f"  lancamentos_extrato_anotado.categoria        → NULL (todos)")
        print(f"  lancamentos_extrato_anotado.descricao_negocio → NULL (todos)")
        print(f"  lancamentos_extrato_anotado.nf_doc           → NULL (todos)")
        print(f"  lancamentos_extrato_anotado.observacao       → NULL (todos)")

        print("\n⚠️  ATENÇÃO: USE APENAS EM AMBIENTE DE DESENVOLVIMENTO/PILOTO ⚠️")
        resposta = input("\nDigite CONFIRMAR para executar o reset: ").strip()

        if resposta != "CONFIRMAR":
            print("Operação cancelada.")
            sys.exit(0)

        db.execute(text(f"""
            UPDATE {schema}.fechamentos_financeiros SET
                status = 'com_divergencias',
                aprovado_em = NULL,
                aprovado_por_usuario_id = NULL,
                observacao_aprovacao = NULL,
                reaberto_em = NULL,
                reaberto_por_usuario_id = NULL
            WHERE id = :id
        """), {"id": conciliacao_id})

        db.execute(text(f"""
            UPDATE {schema}.lancamentos_extrato_anotado SET
                status_revisao = 'pendente',
                categoria = NULL,
                descricao_negocio = NULL,
                nf_doc = NULL,
                observacao = NULL,
                atualizado_por_usuario_id = NULL
            WHERE fechamento_id = :id
        """), {"id": conciliacao_id})

        db.commit()

        print("\n✅ Reset executado com sucesso.")
        print(f"   Fechamento: {conciliacao_id}")
        print(f"   Status:     com_divergencias")
        print(f"   Lançamentos resetados: {total}")


if __name__ == "__main__":
    main()
