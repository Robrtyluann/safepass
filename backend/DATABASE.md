# Banco de dados SAFEpass (PostgreSQL 16)

O banco é compartilhado. O módulo de identidade do Desafio 01 é a fonte única da tabela `users`; os demais squads devem referenciar `users.id`, sem criar outra tabela de usuários.

## Estrutura do Desafio 01

A migration `alembic/versions/20261028_0001_d01_initial.py` (revision `d01_0001`) cria:

- `users`: identidade central, e-mail único, hash Argon2 da senha, nome, papel e estado ativo.
- `refresh_tokens`: hashes dos tokens de renovação, expiração e revogação.
- `password_reset_tokens`: hashes de tokens de recuperação de uso único.
- `plans` e `subscriptions`: planos e vínculo de assinatura.
- `platform_reviews`: avaliações da plataforma (não são avaliações de prestadores).
- `referrals`: indicações de profissionais.

IDs são UUIDs gerados no PostgreSQL e as tabelas de negócio usam `created_at`/`updated_at`.

## Subir o banco e aplicar migrations

Na raiz do monorepo, com Docker Desktop aberto:

```bash
docker compose up --build
```

O serviço `db` sobe PostgreSQL 16. O serviço `migrate` executa `alembic upgrade head` e depois o seed. A API fica em `http://localhost:8000`; a documentação interativa fica em `http://localhost:8000/docs`. O frontend fica em `http://localhost:3000`.

Para executar apenas banco + migration:

```bash
docker compose up -d db
docker compose run --rm migrate
```

Para apagar o banco local e recriar tudo (ATENÇÃO: apaga os dados do volume):

```bash
docker compose down -v
docker compose up --build
```

## Configuração sem Docker

Crie `backend/.env` copiando `backend/.env.example` e ajuste `DATABASE_URL`. Instale as dependências com `uv sync --group dev`, depois execute dentro de `backend/`:

```bash
uv run alembic upgrade head
uv run python -m scripts.seed
uv run fastapi dev app/main.py
```

Não versione `.env`, senhas reais nem `JWT_SECRET` de produção.

## Contrato de autenticação

Todas as rotas ficam sob `/api/v1`:

| Método | Rota | Função |
|---|---|---|
| POST | `/auth/register` | Cadastro e abertura de sessão |
| POST | `/auth/login` | Login |
| POST | `/auth/refresh` | Renovação rotativa da sessão |
| POST | `/auth/logout` | Revoga o refresh token e limpa cookies |
| GET | `/auth/me` | Retorna usuário e assinatura atual |
| POST | `/auth/forgot-password` | Solicita recuperação por e-mail |
| POST | `/auth/reset-password` | Define nova senha com token de uso único |

A autenticação usa cookies `HttpOnly` (`access_token` e `refresh_token`). A senha nunca é armazenada em texto puro: é protegida com Argon2id. Os tokens de refresh e recuperação são armazenados somente como SHA-256. Em desenvolvimento, os e-mails de recuperação podem ser visualizados no Mailpit (`http://localhost:8025`).

## Integração com migrations dos outros squads

O arquivo ZIP recebido contém apenas a migration D01 (`d01_0001`). Os códigos de migration D02 (`93b27d541c7e`) e D03 (`66c8e1279f5c`) enviados separadamente precisam estar em `alembic/versions/` no repositório compartilhado, com a cadeia:

`d01_0001` → `93b27d541c7e` → `66c8e1279f5c`

Não crie uma segunda migration inicial nem outro `users`. Antes de aplicar o banco compartilhado, confirme que essas migrations foram incluídas e que `alembic heads` retorna apenas um head. O ZIP atual não contém as tabelas dos módulos D02/D03, então o banco local gerado somente por este pacote ainda representa o escopo D01.
