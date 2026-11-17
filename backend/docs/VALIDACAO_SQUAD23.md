# Validação da entrega — Squad 23 (identidade e autenticação)

## Escopo entregue

O Desafio 01 concentra a identidade compartilhada e a autenticação. A tabela `users` é a fonte única de identidade para os demais squads. O banco deste pacote é PostgreSQL 16 e a criação do schema é controlada pelo Alembic.

A migration `d01_0001` cria as tabelas do escopo D01:

- `users`
- `refresh_tokens`
- `password_reset_tokens`
- `plans`
- `subscriptions`
- `platform_reviews`
- `referrals`

As migrations `93b27d541c7e` (D02) e `66c8e1279f5c` (D03) pertencem aos respectivos squads e devem ser integradas na cadeia compartilhada depois de `d01_0001`, sem duplicar `users`. Elas não estão neste pacote de código; a documentação e o SQL fornecidos por esses squads devem ser preservados na branch de integração do banco.

## Autenticação

Rotas sob `/api/v1`:

| Método | Endpoint | Resultado |
|---|---|---|
| POST | `/auth/register` | Cria conta e inicia sessão |
| POST | `/auth/login` | Valida credenciais e inicia sessão |
| POST | `/auth/refresh` | Rotaciona o refresh token |
| POST | `/auth/logout` | Revoga a sessão atual |
| GET | `/auth/me` | Retorna identidade e assinatura atual |
| POST | `/auth/forgot-password` | Solicita link de recuperação |
| POST | `/auth/reset-password` | Define nova senha com token de uso único |

A senha é armazenada com Argon2id. Os refresh tokens e tokens de recuperação são armazenados apenas como SHA-256. A sessão usa cookies `HttpOnly`; o backend também aceita `Authorization: Bearer` para testes e Swagger.

## Executar localmente

Na raiz do repositório:

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Mailpit: http://localhost:8025

Para aplicar somente o banco e as migrations:

```bash
docker compose up -d db
docker compose run --rm migrate
```

## Validações realizadas no pacote

- 44 testes unitários passaram com `DATABASE_URL=sqlite+pysqlite:///:memory:` no ambiente de validação.
- O módulo FastAPI foi importado e o OpenAPI foi gerado; as sete rotas de autenticação foram encontradas.
- `compileall` passou para `app`, `scripts`, `alembic` e `tests`.

## Validações ainda necessárias no ambiente da equipe

- Executar `docker compose up --build` com acesso à internet para baixar as imagens e dependências.
- Confirmar `alembic upgrade head` no PostgreSQL 16 real.
- Rodar os testes de integração com PostgreSQL.
- Integrar as migrations D02 e D03 na branch compartilhada e confirmar que `alembic heads` retorna um único head.
- Fazer o build e os testes do frontend após instalar as dependências (`pnpm install`, `pnpm typecheck`, `pnpm test`, `pnpm build`).

A suíte unitária validada com SQLite não substitui a validação de migrations e queries no PostgreSQL.
