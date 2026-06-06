# PRD, iA16 Fechamento Inteligente

## 1. Visão geral

O iA16 Fechamento Inteligente é uma aplicação para apoiar empresas que ainda executam rotinas financeiras com planilhas, conferências manuais e controles descentralizados.

A primeira versão do MVP será validada com a Daxx Omnimedia, tendo como primeiro caso de uso a conciliação bancária.

O produto permitirá que o cliente envie planilhas e extratos financeiros, crie fechamentos por período, processe conciliações, visualize divergências e exporte resultados organizados.

O MVP não será um ERP financeiro. O foco inicial será conciliação bancária, identificação de divergências, registro de observações e geração de planilha final marcada.

## 2. Cliente piloto

Cliente piloto: Daxx Omnimedia

Projeto: Adoção de IA, Aceleração IA

Primeiro caso de uso: conciliação bancária

Usuários de validação: time financeiro da Daxx, especialmente Alice e Cristina

Contexto validado: a conciliação bancária foi definida como primeiro caso de uso por ser um processo repetitivo, baseado em regras claras, com alto volume de conferências manuais e risco de erro humano.

## 2.1 Direção de produto para múltiplos clientes

A aplicação não deve ser construída como uma solução exclusiva para a Daxx.

A Daxx será o primeiro cliente piloto, com foco em conciliação bancária, mas o núcleo do produto deve ser genérico o suficiente para atender outros clientes com cenários como:

- conciliação bancária
- conciliação de caixa
- conciliação de recebíveis
- conciliação de caixa e recebíveis
- conciliação de vendas contra recebimentos
- conciliação de adquirentes
- conciliação entre planilhas internas e fontes externas

A aplicação deve funcionar como uma plataforma de conciliação financeira configurável por empresa.

O conceito central passa a ser:

```text
Fechamento financeiro
  possui empresa
  possui tipo de conciliação
  possui fontes de dados
  possui modelos de arquivo
  possui regras de conciliação
  gera transações normalizadas
  gera itens conciliados
  gera divergências
  gera relatórios
```

Essa decisão permite iniciar pela Daxx sem criar tabelas, regras ou telas específicas da Daxx.

## 3. Problema

A Daxx possui um processo financeiro que exige conferências repetitivas entre planilhas, extratos e plataformas externas.

Isso gera:

- retrabalho manual
- risco de erro humano
- dificuldade para identificar divergências
- tempo elevado para análise financeira
- dependência de conferência operacional
- falta de padronização na marcação dos problemas encontrados
- necessidade de revisar exceções manualmente

## 4. Objetivo do produto

Permitir que o time financeiro envie arquivos financeiros, processe a conciliação bancária e receba uma visão clara de:

- registros conciliados
- registros divergentes
- registros pendentes
- valores divergentes
- tipos de divergência
- observações do fechamento
- planilha final com marcações
- relatório resumido do processamento

## 5. Objetivo do MVP com a Daxx

O MVP deve entregar uma primeira versão funcional para conciliação bancária manual assistida.

O fluxo inicial será:

1. Usuário acessa a aplicação.
2. Cria um fechamento financeiro.
3. Envia planilhas e extratos.
4. Sistema valida os arquivos.
5. Sistema normaliza os dados.
6. Sistema processa a conciliação.
7. Sistema identifica divergências.
8. Usuário revisa as exceções.
9. Usuário registra observações.
10. Usuário baixa a planilha final conciliada.

## 6. Público-alvo

Usuários principais no cliente piloto:

- analista financeiro
- responsável por conciliação
- gestor financeiro
- equipe iA16 responsável pela operação assistida

Usuários futuros:

- dono da empresa
- diretor financeiro
- gestor administrativo
- analista financeiro
- equipe iA16 responsável pela operação assistida

## 7. Proposta de valor

A aplicação permite que a empresa comece usando os arquivos que já possui, sem depender de integração bancária, ERP ou adquirente no primeiro momento.

A proposta é reduzir a conferência manual, sinalizar divergências automaticamente e deixar para o time financeiro apenas a análise das exceções.

## 8. Escopo do MVP

### Entra no MVP

- login via Supabase Auth
- controle por empresa
- cadastro de empresas e usuários pela iA16
- upload de arquivos Excel
- cadastro simples de fontes de dados
- modelos de arquivo por cliente
- criação de fechamento financeiro
- associação de arquivos ao fechamento
- validação de arquivos enviados
- processamento com FastAPI, Pandas e OpenPyXL
- normalização dos dados financeiros
- conciliação bancária inicial
- identificação de registros conciliados, divergentes e pendentes
- tela de divergências
- observações manuais nas divergências
- relatório do fechamento
- exportação em Excel
- dashboard simples
- logs de processamento

### Não entra no MVP

- Open Finance
- integração bancária automática
- integração com ERP
- integração automática com adquirentes
- chat financeiro completo
- aplicativo mobile
- workflow avançado de aprovação
- contas a pagar completo
- contas a receber completo
- emissão de boletos
- gestão fiscal
- conciliação tributária
- BI avançado
- automação completa de fluxo de caixa

## 9. Funcionalidades principais

1. Autenticação e controle de acesso
2. Empresas e usuários
3. Fontes de dados
4. Modelos de arquivo
5. Upload de arquivos
6. Validação de arquivos
7. Fechamentos financeiros
8. Motor de conciliação bancária
9. Divergências e pendências
10. Observações nas divergências
11. Relatórios e exportações
12. Dashboard
13. Logs de processamento

## 10. Arquivos esperados no cliente piloto

O MVP deve estar preparado para receber arquivos como:

- extratos bancários
- planilhas internas de controle financeiro
- planilhas de fluxo de caixa
- relatórios financeiros exportados de plataformas externas
- arquivos complementares usados na conferência manual

A estrutura exata dos arquivos deve ser validada com a Daxx antes da implementação final das regras.

## 11. Regras iniciais de conciliação

A primeira versão do motor de conciliação deve usar regras determinísticas, não IA para decidir valores.

Critérios iniciais sugeridos:

1. documento igual e valor igual
2. data igual ou próxima e valor igual
3. descrição semelhante e valor igual
4. valor próximo dentro de tolerância configurada
5. registro presente em uma fonte e ausente em outra
6. registro duplicado
7. divergência de data
8. divergência de valor

A IA poderá ser usada apenas como camada auxiliar para resumo executivo, explicação das divergências e sugestão de observação, sem alterar dados financeiros.

## 12. Tipos de divergência do MVP

- valor diferente
- data diferente
- registro não encontrado
- registro duplicado
- recebimento pendente
- lançamento não identificado
- categoria inconsistente
- taxa divergente
- outro

## 13. Saída esperada

A saída principal do MVP deve ser uma planilha Excel com:

- registros conciliados
- registros divergentes
- registros pendentes
- origem do registro
- status da conciliação
- tipo de divergência
- valor esperado
- valor encontrado
- diferença
- data esperada
- data encontrada
- observação
- ação sugerida

Também deve existir um resumo do fechamento com:

- total processado
- total conciliado
- total divergente
- quantidade de pendências
- percentual de conciliação
- principais divergências
- pontos de atenção

## 14. Fluxo principal

1. Usuário acessa a aplicação.
2. Seleciona ou confirma a empresa.
3. Cria novo fechamento.
4. Informa período de referência.
5. Envia as planilhas necessárias.
6. Sistema valida os arquivos.
7. Usuário inicia o processamento.
8. FastAPI processa os arquivos.
9. Sistema grava transações, resultados e divergências.
10. Usuário revisa as divergências.
11. Usuário registra observações.
12. Usuário exporta o relatório ou planilha final.

## 15. Indicadores do MVP

O dashboard deve mostrar:

- quantidade de fechamentos
- total processado no período
- valor conciliado
- valor divergente
- percentual conciliado
- quantidade de divergências
- divergências abertas
- fechamentos com erro
- últimos fechamentos

## 16. Requisitos não funcionais

- aplicação responsiva para desktop
- autenticação obrigatória
- segregação por empresa via RLS
- logs mínimos de processamento
- possibilidade de reprocessamento
- armazenamento seguro dos arquivos
- nomes do banco em português
- código organizado por domínio
- uso de migrations versionadas
- ambiente executado em VPS com Docker
- Supabase mantido para banco, auth, storage e RLS

## 17. Critérios de sucesso do MVP

O MVP será considerado funcional quando permitir:

- cadastrar a empresa Daxx
- criar usuários vinculados à Daxx
- fazer login
- enviar arquivos Excel
- criar um fechamento financeiro
- processar os arquivos
- visualizar conciliados e divergências
- adicionar observação em divergências
- exportar resultado em Excel
- consultar histórico de fechamentos
- identificar exceções para revisão do financeiro

## 18. Critérios de aceite com o cliente piloto

A Daxx deve conseguir validar:

- se os arquivos reais podem ser enviados
- se as colunas principais são reconhecidas
- se a conciliação identifica os principais casos esperados
- se as divergências estão claras
- se a planilha final ajuda o time financeiro
- se o time financeiro consegue revisar apenas exceções
- se o fluxo reduz conferência manual
- se o resultado é confiável para evoluir o produto

## 19. Premissas

- O primeiro ciclo será baseado em upload manual de planilhas.
- O cliente fornecerá exemplos reais ou simulados de extratos, planilhas e fluxo de caixa.
- A integração automática com bancos não será implementada no primeiro ciclo.
- A arquitetura ficará preparada para fontes automáticas no futuro.
- A conciliação será baseada em regras determinísticas.
- A IA não terá autonomia para alterar conciliações.

## 20. Riscos

- Os arquivos reais podem ter baixa padronização.
- As colunas podem variar entre períodos.
- Pode haver divergências que dependem de julgamento humano.
- Pode haver regras específicas da Daxx ainda não documentadas.
- O time financeiro pode esperar automação maior do que o MVP entrega.
- A qualidade da conciliação depende da qualidade dos arquivos enviados.

## 21. Próximas validações com a Daxx

Validar com Alice e Cristina:

1. Quais arquivos entram na conciliação hoje?
2. Qual é a fonte considerada mais confiável?
3. Quais colunas são obrigatórias?
4. Quais divergências são mais comuns?
5. Como o time marca divergências atualmente?
6. Qual formato de planilha final é esperado?
7. O fechamento é diário, semanal ou mensal?
8. Existe tolerância de valor ou data?
9. Quais casos devem ser ignorados?
10. Quais casos precisam de alerta?
## 22. Premissa de implementação multicliente e multiconciliação

O MVP deve nascer preparado para atender mais de um cliente e mais de um tipo de conciliação.

Isso não significa criar um motor financeiro universal complexo no primeiro ciclo. Significa evitar acoplamento com um único cliente.

Regras obrigatórias:

- não criar objetos com nome de cliente no banco de dados
- não criar tabelas específicas da Daxx
- não criar regras hardcoded para uma empresa quando puderem ser configuração
- todo fechamento deve ter um tipo de conciliação
- toda empresa pode ter uma ou mais configurações de conciliação
- modelos de arquivo devem ser vinculados à empresa e ao tipo de conciliação
- regras de conciliação devem ser configuráveis por empresa
- a saída pode variar por tipo de conciliação, mas deve usar estrutura comum

Exemplos:

```text
Daxx Omnimedia:
tipo de conciliação = bancaria

Cliente 2:
tipo de conciliação = caixa_recebiveis
```
