---
name: ia16-git
description: Configura e valida o fluxo Git do projeto iA16 Fechamento Inteligente, usando repositório existente ou criando um novo repositório no GitHub
---

# ia16-git

Você é responsável por ajudar a configurar e validar o fluxo Git do projeto iA16 Fechamento Inteligente.

## Objetivo

Configurar o Git do projeto com segurança, usando o fluxo:

```text
origin/main
  |
  v
develop
  |
  v
feature/*
```

A branch `main` deve ficar protegida no GitHub e não deve ser usada como branch local de trabalho.

## Pergunta inicial obrigatória

Antes de executar qualquer configuração, pergunte ao usuário:

```text
O repositório no GitHub já existe?

1. Sim, já existe
2. Não, ainda precisa criar
```

## Cenário A, repositório já existe

Se o repositório já existe, peça a URL SSH do repositório.

Exemplo esperado:

```text
git@github.com:useria16/ia16_fechamento_inteligente.git
```

Para este projeto, o repositório padrão é:

```text
git@github.com:useria16/ia16_fechamento_inteligente.git
```

### Passos

Validar acesso SSH:

```bash
ssh -T git@github.com
```

Se o projeto ainda não estiver clonado:

```bash
git clone git@github.com:useria16/ia16_fechamento_inteligente.git
cd ia16_fechamento_inteligente
```

Verificar remoto:

```bash
git remote -v
```

Se o remoto estiver em HTTPS, trocar para SSH:

```bash
git remote set-url origin git@github.com:useria16/ia16_fechamento_inteligente.git
```

Criar branch `develop` se ainda não existir:

```bash
git checkout main
git pull origin main
git checkout -b develop
git push -u origin develop
```

Remover branch `main` local, mantendo apenas a referência remota:

```bash
git checkout develop
git branch -d main
```

Validar:

```bash
git branch
git branch -r
git status
```

Resultado esperado:

```text
branch local ativa: develop
branches remotas: origin/main e origin/develop
```

## Cenário B, repositório ainda não existe

Se o repositório ainda não existe, primeiro valide se o acesso ao GitHub está configurado.

Validar GitHub CLI:

```bash
gh auth status
```

Se não estiver autenticado, orientar o usuário a executar:

```bash
gh auth login
```

Não inserir token manualmente no projeto.

Não salvar token em `.env`, `.claude/`, `settings.json` ou qualquer arquivo versionado.

Depois que `gh auth status` funcionar, criar o repositório:

```bash
gh repo create useria16/ia16_fechamento_inteligente --private --source=. --remote=origin
```

Se o usuário pedir repositório público, confirmar antes e usar:

```bash
gh repo create useria16/ia16_fechamento_inteligente --public --source=. --remote=origin
```

Se a pasta ainda não for um repositório Git:

```bash
git init
```

Criar README inicial, se ainda não existir:

```bash
echo "# iA16 Fechamento Inteligente" > README.md
```

Criar `.gitignore` básico se ainda não existir:

```bash
cat > .gitignore <<'EOF'
# Ambiente
.env
.env.*
!.env.example

# Python
__pycache__/
*.pyc
.venv/
venv/
.pytest_cache/

# Node/Nuxt
node_modules/
.nuxt/
.output/
dist/

# Logs
*.log

# Sistema
.DS_Store

# Credenciais
secrets/
credentials.json
EOF
```

Criar commit inicial:

```bash
git add .
git commit -m "chore: estrutura inicial do projeto"
```

Enviar para `main`:

```bash
git branch -M main
git push -u origin main
```

Criar branch `develop`:

```bash
git checkout -b develop
git push -u origin develop
```

Remover `main` local:

```bash
git checkout develop
git branch -d main
```

## Configuração de SSH, se necessário

Se `ssh -T git@github.com` falhar, verificar se existe chave SSH:

```bash
ls -la ~/.ssh
```

Se não existir `id_ed25519.pub`, criar:

```bash
ssh-keygen -t ed25519 -C "elieziomesquita@gmail.com"
```

Exibir chave pública:

```bash
cat ~/.ssh/id_ed25519.pub
```

Orientar o usuário a adicionar no GitHub:

```text
GitHub > Settings > SSH and GPG keys > New SSH key
```

Testar novamente:

```bash
ssh -T git@github.com
```

Somente continuar quando a autenticação funcionar.

## Política de branches

Nunca trabalhar diretamente na `main`.

A `main` deve existir no GitHub e ser protegida.

Branch local principal:

```text
develop
```

Branches de trabalho:

```text
feature/*
```

## Criar branch de feature

Antes de criar uma feature:

```bash
git checkout develop
git pull origin develop
```

Criar branch:

```bash
git checkout -b feature/nome-da-funcionalidade
```

Exemplos:

```bash
git checkout -b feature/configuracao-claude
git checkout -b feature/base-projeto
git checkout -b feature/tipos-conciliacao
git checkout -b feature/upload-arquivos
```

## Commit e push

Antes do commit:

```bash
git status
git diff
```

Adicionar arquivos:

```bash
git add .
```

Criar commit:

```bash
git commit -m "tipo: descricao objetiva"
```

Exemplos:

```bash
git commit -m "chore: adiciona configuracao do claude code"
git commit -m "feat: adiciona tipos de conciliacao"
git commit -m "docs: atualiza prd multicliente"
```

Enviar branch:

```bash
git push -u origin feature/nome-da-funcionalidade
```

## Pull Request

Depois do push, orientar o usuário a abrir PR:

```text
feature/nome-da-funcionalidade -> develop
```

Quando a `develop` estiver validada:

```text
develop -> main
```

O merge para `main` deve ser feito pelo GitHub, não localmente.

## Branch protection

Orientar o usuário a proteger a branch `main` no GitHub:

```text
Repository
Settings
Branches
Branch protection rules
Add branch ruleset
```

Configurações recomendadas para `main`:

* bloquear push direto
* exigir Pull Request
* bloquear force push
* bloquear deleção da branch
* exigir aprovação antes do merge, quando houver mais pessoas no projeto
* exigir checks, quando testes estiverem configurados

## Comandos proibidos sem autorização explícita

Não executar sem autorização clara do usuário:

```bash
git reset --hard
git clean -fd
git push --force
git branch -D
```

## Arquivos sensíveis

Nunca versionar:

```text
.env
.env.*
tokens
chaves SSH
credenciais
service_role keys
arquivos em secrets/
credentials.json
```

## Validação final

Ao final, executar:

```bash
git status
git branch
git branch -r
git remote -v
```

Resultado esperado:

```text
branch local ativa: develop ou feature/*
remotos: origin/main e origin/develop
remote usando SSH
nenhum arquivo sensível versionado
```

## Saída obrigatória

Sempre responder com:

1. Cenário identificado: repo existente ou repo novo.
2. Estado atual do Git.
3. Branch local ativa.
4. Remoto configurado.
5. Branches remotas disponíveis.
6. Próximo comando recomendado.
7. Alertas de segurança, se existirem.
