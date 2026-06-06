# Escopo do cliente piloto, Daxx Omnimedia, conciliação bancária

## 1. Contexto

A Daxx Omnimedia será o primeiro cliente piloto do iA16 Fechamento Inteligente.

O primeiro caso de uso validado é a conciliação bancária, dentro do projeto de adoção de IA e Aceleração IA.

A escolha foi feita por ser um processo repetitivo, baseado em regras claras, com alto volume de conferência manual e risco de erro humano.

## 2. Objetivo do piloto

Construir uma primeira versão funcional para processar arquivos financeiros enviados manualmente, identificar divergências e gerar uma planilha final marcada para revisão do time financeiro.

## 3. Usuários envolvidos

- Alice
- Cristina
- Victória Braga
- Gabriel Corneta
- Eliézio Mesquita
- equipe financeira da Daxx
- equipe iA16

## 4. Dor principal

O processo atual exige conferências repetitivas entre planilhas, extratos e plataformas externas.

A dor principal não é substituir todo o financeiro, mas reduzir o esforço manual da conciliação e deixar o time financeiro focado apenas nas exceções.

## 5. Entrada de dados inicial

O MVP deve considerar upload manual de arquivos.

Arquivos esperados:

- extratos bancários
- planilhas financeiras internas
- fluxo de caixa
- relatórios de plataformas externas
- arquivos complementares usados na rotina de conciliação

## 6. Fluxo operacional do piloto

1. Equipe financeira separa os arquivos do período.
2. Usuário acessa o iA16 Fechamento Inteligente.
3. Usuário cria um fechamento.
4. Usuário envia os arquivos.
5. Sistema valida os arquivos.
6. Sistema normaliza os dados.
7. Sistema executa conciliação.
8. Sistema apresenta registros conciliados e divergentes.
9. Usuário revisa exceções.
10. Usuário registra observações.
11. Usuário exporta a planilha final.

## 7. Saída esperada

A saída principal será uma planilha Excel contendo:

- status da conciliação
- tipo de divergência
- dados da origem 1
- dados da origem 2
- valor esperado
- valor encontrado
- diferença
- data esperada
- data encontrada
- observação
- ação sugerida

## 8. Regras iniciais

As regras finais dependem dos arquivos reais da Daxx, mas a primeira versão deve suportar:

- conciliar por documento e valor
- conciliar por data e valor
- identificar valores divergentes
- identificar datas divergentes
- identificar registros ausentes
- identificar duplicidades
- marcar registros pendentes
- permitir observação manual

## 9. Fora do piloto inicial

Não implementar neste primeiro ciclo:

- Open Finance
- API bancária
- integração com ERP
- integração automática com adquirente
- contas a pagar completo
- contas a receber completo
- BI avançado
- automação completa do financeiro

## 10. Critérios de aceite

O piloto será aceito quando:

- a Daxx conseguir enviar arquivos reais ou simulados
- o sistema conseguir ler e normalizar os arquivos
- o sistema conseguir processar conciliação inicial
- as divergências forem apresentadas de forma clara
- o time financeiro conseguir registrar observações
- a planilha final puder ser exportada
- o fluxo reduzir parte relevante da conferência manual

## 11. Perguntas pendentes para Alice e Cristina

1. Quais arquivos são usados hoje na conciliação?
2. Qual arquivo é considerado fonte de verdade?
3. Quais colunas são indispensáveis?
4. Como as divergências são marcadas hoje?
5. Quais são os erros mais comuns?
6. Existe tolerância de valor?
7. Existe tolerância de data?
8. O fechamento é diário, semanal ou mensal?
9. Quais casos devem ser ignorados?
10. Qual formato ideal da planilha final?
