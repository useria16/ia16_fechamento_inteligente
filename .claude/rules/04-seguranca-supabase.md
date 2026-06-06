# Segurança e Supabase

## Regras obrigatórias

- Usar Supabase Auth para autenticação.
- Usar Supabase Postgres como banco.
- Usar Supabase Storage para arquivos.
- Usar Supabase RLS para segregação por empresa.
- Não criar cadastro público no MVP.
- Usuários devem ser criados ou controlados pela iA16.
- Usuário cliente só pode acessar dados da própria empresa.
- Admin iA16 pode acessar múltiplas empresas.
- Nunca versionar chaves, tokens, senhas ou URLs sensíveis.

## Arquivos sensíveis

Não ler, exibir ou versionar:

- `.env`
- `.env.*`
- `backend/.env`
- `frontend/.env`
- arquivos em `secrets/`
- arquivos de credenciais
