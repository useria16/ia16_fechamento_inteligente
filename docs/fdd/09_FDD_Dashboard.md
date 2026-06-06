# FDD 09, Dashboard

## 1. Objetivo

Oferecer uma visão simples e executiva do fechamento financeiro.

## 2. Escopo

Dashboard com indicadores principais, últimos fechamentos e status das divergências.

## 3. Indicadores

- total processado
- total conciliado
- total divergente
- percentual conciliado
- quantidade de divergências abertas
- quantidade de fechamentos no período
- últimos fechamentos
- fechamentos com erro

## 4. Regras de negócio

- Usuário cliente visualiza apenas dados da própria empresa.
- Admin iA16 pode selecionar empresa.
- Dados devem ser calculados a partir de fechamentos processados.
- Dashboard deve carregar rápido.
- No MVP, gráficos simples são suficientes.

## 5. Telas

- `/dashboard`

## 6. APIs

### GET `/api/dashboard/resumo`

Retorna indicadores agregados.

### GET `/api/dashboard/ultimos-fechamentos`

Retorna últimos fechamentos.

## 7. Critérios de aceite

- Dashboard mostra indicadores.
- Dashboard respeita empresa do usuário.
- Dashboard mostra últimos fechamentos.
- Dashboard mostra divergências abertas.
- Interface funciona bem em desktop.

## 8. Tarefas para Claude Code

- Criar endpoint de resumo.
- Criar endpoint de últimos fechamentos.
- Criar tela dashboard.
- Criar cards de indicadores.
- Criar gráfico simples com Chart.js.
