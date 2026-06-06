# Funcionalidades de negócio, iA16 Fechamento Inteligente

## 1. Objetivo deste documento

Este documento consolida as funcionalidades de negócio do MVP do iA16 Fechamento Inteligente.

Enquanto o PRD explica a visão do produto e os FDDs detalham cada funcionalidade para desenvolvimento, este documento organiza o que o produto realmente entrega para o usuário final e para a operação da iA16.

## 2. Princípio do MVP

O MVP não será um ERP financeiro.

O produto deve resolver uma dor específica:

> Permitir que o cliente envie planilhas financeiras, processe um fechamento, identifique divergências, registre observações e gere uma saída confiável para análise e tomada de decisão.

## 2.1 Cliente piloto do MVP

Cliente piloto: Daxx Omnimedia

Primeiro caso de uso: conciliação bancária

O backlog funcional do MVP deve priorizar a capacidade de receber planilhas e extratos, processar conciliação, identificar divergências e gerar planilha final marcada para revisão do time financeiro.

## 3. Funcionalidades de negócio do MVP

### FN-01, Acesso seguro à plataforma

Permitir que usuários autorizados acessem a aplicação com login e senha.

Valor de negócio:

- proteger informações financeiras
- evitar acesso público
- controlar usuários por empresa
- permitir operação assistida pela iA16

Relacionamento técnico:

- FDD 01, Autenticação, empresas e usuários

---

### FN-02, Gestão de empresas clientes

Permitir que a iA16 cadastre e mantenha empresas clientes dentro da plataforma.

Valor de negócio:

- organizar clientes atendidos
- separar dados financeiros por empresa
- permitir atendimento multiempresa
- preparar a base para planos recorrentes

Relacionamento técnico:

- FDD 01, Autenticação, empresas e usuários

---

### FN-03, Gestão de usuários por empresa

Permitir cadastrar usuários vinculados a uma empresa, com perfil operacional ou administrativo.

Valor de negócio:

- controlar quem acessa os fechamentos
- separar operação da iA16 e operação do cliente
- reduzir risco de exposição de dados financeiros

Relacionamento técnico:

- FDD 01, Autenticação, empresas e usuários

---

### FN-04, Cadastro de fontes de dados financeiras

Permitir registrar de onde vêm os dados usados no fechamento financeiro.

Exemplos:

- Excel manual
- banco
- adquirente
- ERP
- Google Drive
- outro

No MVP, somente Excel manual será processado.

Valor de negócio:

- preparar o produto para evolução futura
- organizar origem dos arquivos
- dar rastreabilidade ao fechamento

Relacionamento técnico:

- FDD 02, Fontes de dados

---

### FN-05, Configuração de modelos de arquivo

Permitir configurar o padrão esperado das planilhas de cada cliente.

Exemplo:

- coluna de data
- coluna de valor
- coluna de documento
- coluna de descrição
- coluna de status
- coluna de forma de pagamento

Valor de negócio:

- reduzir esforço manual
- permitir que cada cliente use sua própria planilha
- evitar que cada upload vire uma análise manual do zero

Relacionamento técnico:

- FDD 03, Modelos de arquivo

---

### FN-06, Upload de planilhas financeiras

Permitir que o cliente ou a equipe iA16 envie planilhas Excel para a aplicação.

Tipos iniciais:

- extrato bancário
- relatório de vendas
- relatório de recebíveis
- planilha interna
- taxas de adquirente
- outro

Valor de negócio:

- permitir entrada manual simples
- validar o produto sem depender de APIs bancárias
- reduzir barreira de adoção

Relacionamento técnico:

- FDD 04, Upload de arquivos

---

### FN-07, Validação dos arquivos enviados

Validar se o arquivo enviado pode ser usado no fechamento.

Validações iniciais:

- extensão permitida
- tamanho permitido
- arquivo legível
- colunas obrigatórias
- modelo associado
- tipo de arquivo

Valor de negócio:

- evitar processamento com dados inválidos
- reduzir erro operacional
- gerar mensagens claras para correção

Relacionamento técnico:

- FDD 04, Upload de arquivos
- FDD 06, Motor de conciliação
- FDD 10, Logs de processamento

---

### FN-08, Criação de fechamento financeiro

Permitir criar um fechamento financeiro por período, empresa e título.

Exemplos:

- fechamento diário
- fechamento semanal
- fechamento mensal
- fechamento por unidade
- fechamento por conta bancária

Valor de negócio:

- organizar a rotina financeira
- criar histórico dos fechamentos
- permitir acompanhamento por status

Relacionamento técnico:

- FDD 05, Fechamentos financeiros

---

### FN-09, Associação de arquivos ao fechamento

Permitir vincular os arquivos enviados a um fechamento específico.

Valor de negócio:

- garantir rastreabilidade
- saber quais arquivos foram usados em cada processamento
- permitir reprocessamento

Relacionamento técnico:

- FDD 04, Upload de arquivos
- FDD 05, Fechamentos financeiros

---

### FN-10, Processamento do fechamento financeiro

Permitir que o usuário inicie o processamento dos arquivos associados ao fechamento.

O processamento deve:

- ler as planilhas
- normalizar os dados
- aplicar regras de conciliação
- gerar registros conciliados
- gerar divergências
- atualizar indicadores do fechamento

Valor de negócio:

- reduzir conferência manual
- acelerar a rotina financeira
- padronizar análise
- melhorar confiabilidade do fechamento

Relacionamento técnico:

- FDD 06, Motor de conciliação

---

### FN-11, Normalização dos dados financeiros

Transformar dados de diferentes planilhas em um formato único para análise.

Exemplo:

- diferentes nomes de coluna passam para um padrão interno
- datas são padronizadas
- valores são convertidos
- descrições são tratadas
- documentos são normalizados

Valor de negócio:

- permitir comparar dados de fontes diferentes
- reduzir dependência de layout fixo
- preparar a base para integrações futuras

Relacionamento técnico:

- FDD 03, Modelos de arquivo
- FDD 06, Motor de conciliação

---

### FN-12, Conciliação financeira

Comparar registros financeiros de diferentes fontes para identificar correspondências.

Critérios iniciais:

- documento igual e valor igual
- data próxima e valor igual
- descrição similar e valor igual
- valor próximo dentro de tolerância
- ausência de registro correspondente

Valor de negócio:

- encontrar o que bate e o que não bate
- reduzir trabalho manual
- dar segurança para o fechamento

Relacionamento técnico:

- FDD 06, Motor de conciliação

---

### FN-13, Identificação de divergências

Gerar divergências automaticamente quando os registros não baterem.

Tipos iniciais:

- valor diferente
- data diferente
- registro não encontrado
- registro duplicado
- taxa divergente
- recebimento pendente
- categoria inconsistente
- outro

Valor de negócio:

- mostrar onde o financeiro precisa atuar
- priorizar problemas
- evitar que divergências passem despercebidas

Relacionamento técnico:

- FDD 07, Divergências e observações

---

### FN-14, Revisão operacional de divergências

Permitir que o usuário visualize, filtre e analise divergências.

Filtros iniciais:

- status
- tipo
- severidade
- valor
- data
- fechamento

Valor de negócio:

- facilitar a análise do time financeiro
- reduzir tempo de investigação
- melhorar controle operacional

Relacionamento técnico:

- FDD 07, Divergências e observações

---

### FN-15, Registro de observações

Permitir que o usuário registre observações nas divergências.

Exemplos:

- "valor diferença por taxa da adquirente"
- "lançamento será compensado no próximo dia"
- "cliente pagou com atraso"
- "registro duplicado no relatório de vendas"

Valor de negócio:

- criar histórico da análise
- evitar perda de contexto
- facilitar acompanhamento pela iA16 e pelo cliente

Relacionamento técnico:

- FDD 07, Divergências e observações

---

### FN-16, Resolução de divergências

Permitir alterar o status de uma divergência para resolvida, ignorada ou em análise.

Valor de negócio:

- controlar pendências
- separar problema real de exceção conhecida
- permitir acompanhamento do fechamento até conclusão

Relacionamento técnico:

- FDD 07, Divergências e observações

---

### FN-17, Resumo executivo do fechamento

Gerar uma visão resumida do fechamento.

Deve incluir:

- total processado
- total conciliado
- total divergente
- percentual de conciliação
- principais divergências
- pontos de atenção
- ações recomendadas

Valor de negócio:

- traduzir o fechamento para visão de gestão
- facilitar tomada de decisão
- entregar valor além da planilha

Relacionamento técnico:

- FDD 08, Relatórios e exportação
- FDD 11, Resumo executivo com IA opcional

---

### FN-18, Dashboard financeiro simples

Exibir uma visão consolidada dos fechamentos.

Indicadores iniciais:

- total processado
- total conciliado
- total divergente
- percentual conciliado
- divergências abertas
- últimos fechamentos
- fechamentos com erro

Valor de negócio:

- dar visão rápida ao gestor
- mostrar evolução dos fechamentos
- apoiar acompanhamento recorrente

Relacionamento técnico:

- FDD 09, Dashboard

---

### FN-19, Exportação da planilha conciliada

Permitir baixar a planilha final do fechamento.

A planilha deve conter:

- registros conciliados
- registros divergentes
- observações
- status
- valores
- datas
- origem dos dados

Valor de negócio:

- manter compatibilidade com a rotina atual do cliente
- facilitar validação
- permitir uso externo do resultado

Relacionamento técnico:

- FDD 08, Relatórios e exportação

---

### FN-20, Exportação do relatório de divergências

Permitir exportar apenas as divergências do fechamento.

Valor de negócio:

- facilitar análise do time financeiro
- permitir envio para responsáveis
- apoiar revisão operacional

Relacionamento técnico:

- FDD 08, Relatórios e exportação

---

### FN-21, Histórico de fechamentos

Permitir consultar fechamentos anteriores.

Valor de negócio:

- criar memória operacional
- permitir comparação entre períodos
- reduzir dependência de arquivos soltos

Relacionamento técnico:

- FDD 05, Fechamentos financeiros
- FDD 09, Dashboard

---

### FN-22, Logs e rastreabilidade do processamento

Registrar eventos relevantes do processamento.

Exemplos:

- processamento iniciado
- arquivo lido
- arquivo inválido
- coluna obrigatória ausente
- conciliação concluída
- relatório gerado
- processamento com erro

Valor de negócio:

- facilitar suporte
- reduzir tempo para diagnóstico
- melhorar confiabilidade operacional

Relacionamento técnico:

- FDD 10, Logs de processamento

---

## 4. Funcionalidades fora do MVP

As funcionalidades abaixo não entram na primeira versão:

- integração Open Finance
- API bancária
- integração direta com adquirentes
- integração com ERP
- conciliação automática via Google Drive
- workflow avançado de aprovação
- contas a pagar completo
- contas a receber completo
- emissão de boletos
- gestão fiscal
- aplicativo mobile
- chat financeiro completo
- BI avançado

## 5. Mapa entre funcionalidade de negócio e FDD

| Funcionalidade de negócio | Documento FDD relacionado |
|---|---|
| Acesso seguro à plataforma | FDD 01 |
| Gestão de empresas clientes | FDD 01 |
| Gestão de usuários por empresa | FDD 01 |
| Cadastro de fontes de dados | FDD 02 |
| Configuração de modelos de arquivo | FDD 03 |
| Upload de planilhas financeiras | FDD 04 |
| Validação dos arquivos enviados | FDD 04, FDD 06, FDD 10 |
| Criação de fechamento financeiro | FDD 05 |
| Associação de arquivos ao fechamento | FDD 04, FDD 05 |
| Processamento do fechamento | FDD 06 |
| Normalização dos dados financeiros | FDD 03, FDD 06 |
| Conciliação financeira | FDD 06 |
| Identificação de divergências | FDD 07 |
| Revisão operacional de divergências | FDD 07 |
| Registro de observações | FDD 07 |
| Resolução de divergências | FDD 07 |
| Resumo executivo do fechamento | FDD 08, FDD 11 |
| Dashboard financeiro simples | FDD 09 |
| Exportação da planilha conciliada | FDD 08 |
| Exportação do relatório de divergências | FDD 08 |
| Histórico de fechamentos | FDD 05, FDD 09 |
| Logs e rastreabilidade | FDD 10 |

## 6. Backlog funcional do MVP

### Prioridade 1, operação mínima

- Acesso seguro
- Empresa
- Usuários
- Upload de arquivos
- Criação de fechamento
- Processamento básico
- Visualização de divergências
- Exportação Excel

### Prioridade 2, controle e gestão

- Modelos de arquivo
- Fontes de dados
- Observações
- Resolução de divergências
- Histórico de fechamentos
- Logs de processamento

### Prioridade 3, visão executiva

- Dashboard
- Resumo executivo
- Exportação de relatório de divergências
- Resumo com IA opcional

## 7. Frase guia

O produto deve permitir que o cliente envie os arquivos, processe o fechamento, veja o que conciliou, entenda o que divergiu, registre observações e baixe uma saída confiável.
## Funcionalidades estruturais para multiconciliação

Para atender a Daxx e outro cliente com conciliação de caixa e recebíveis, o MVP deve incluir:

- cadastro de tipos de conciliação
- configuração de conciliação por empresa
- regras de conciliação por configuração
- seleção do tipo de conciliação no fechamento
- modelos de arquivo vinculados ao tipo de conciliação
- motor de conciliação que aplica regras configuradas

Essa estrutura permite atender múltiplos clientes com o mesmo núcleo de produto.
