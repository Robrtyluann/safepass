# SAFEpass — Backend Squad 46

Implementação dos módulos do Desafio 02 na branch `feature/squad-46`: `marketplace`,
`reviews`, `points`, `coupons`, `dependents`, `alerts` e `dashboard`. Python 3.12,
FastAPI, PostgreSQL 16, SQLAlchemy 2 síncrono, psycopg 3, Pydantic 2 e Alembic.
Segue o mesmo padrão de arquitetura e scaffold da branch `feature/squad-47`
(Desafio 03). IA está fora do escopo desta entrega.

## Instalação e banco local

Execute em `backend/`, com Python 3.12, uv e Docker/Compose disponíveis:

```bash
uv sync
docker compose -p safepass46 up -d --wait db
uv run alembic upgrade head
uv run alembic check
```

A conexão padrão aponta para o banco local do Compose, na porta 55432. As
credenciais do Compose são exclusivamente de desenvolvimento. Para outra
instância, defina `DATABASE_URL` por ambiente ou `.env` (veja `.env.example`).
Migrations são um passo explícito; a aplicação não executa `create_all` nem
migrations durante o startup.

## Executar e experimentar a API

Sem integração de identidade, a aplicação normal recusa operações protegidas:

```bash
uv run fastapi dev app/main.py
```

Para experimentar com identidades e catálogo de prestadores **fictícios locais**,
use explicitamente:

```bash
uv run python -m scripts.dev
```

Este comando liga somente em `127.0.0.1:8000`. Nunca o use em produção ou com
exposição pública. O aplicativo normal `app.main:app` não ativa esses adapters.
Não há login, senha, emissão de JWT, tabela de usuários ou de prestadores
concorrente aos Desafios 1 e 3.

Identidades do adapter local:

| Bearer fictício | Papel | Observação |
|---|---|---|
| `local-manager` | `user` (gestor) | Tem `plan_id` definido; cupons gated por plano aparecem desbloqueados para ele |
| `local-other-manager` | `user` (gestor) | Sem plano; útil para testar cupons bloqueados |
| `local-dependent` | `dependent` | Só atua se houver um `Dependent.linked_user_id` apontando para ele |

Verificação HTTP e primeiro fluxo:

```bash
curl --fail-with-body http://127.0.0.1:8000/health
curl --fail-with-body http://127.0.0.1:8000/api/v1/prestadores \
  -H 'Authorization: Bearer local-manager'
curl --fail-with-body http://127.0.0.1:8000/api/v1/dashboard \
  -H 'Authorization: Bearer local-manager'
```

A lista de prestadores vem de um catálogo fixo em memória (`LocalProviderCatalog`)
que substitui o módulo `providers` do Desafio 03 enquanto ele não está mergeado.
Não há `POST /cupons`: o catálogo de cupons ainda não tem dono definido, então os
cupons usados nos testes são semeados diretamente no banco. O contrato vivo está
em `/docs` e `/openapi.json`.

## Endpoints principais

Todos abaixo usam prefixo `/api/v1`; listagens aceitam `page` e `size` (máximo
100).

| Recurso | Operações |
|---|---|
| `/dashboard` | GET: visão consolidada (plano, pontos, dependentes, alertas, agenda de 7 dias, cupons ativos) |
| `/prestadores` | GET com filtros `q`, `categoria`, `preco`, `tags` |
| `/prestadores/{id}` | GET perfil |
| `/prestadores/{id}/avaliacoes` | GET (lista + média) e POST (cria avaliação, credita pontos ao gestor) |
| `/favoritos` | GET lista; `/favoritos/{providerId}` PUT favorita, DELETE remove |
| `/pontos/saldo`, `/pontos/extrato` | GET saldo e extrato (ledger append-only) |
| `/cupons` | GET catálogo, com `locked: true` para cupons fora do plano |
| `/cupons/{id}/resgates` | POST resgata (aceita header opcional `Idempotency-Key`) |
| `/resgates` | GET histórico, filtros `status`, `de`, `ate` |
| `/resgates/{token}/utilizacao` | POST marca o token como utilizado |
| `/dependentes` | GET lista; POST cria; `/dependentes/{id}` PATCH edita/libera resgate, DELETE remove (lógico) |
| `/alertas` | GET lista; POST cria alerta manual |

Exemplo de resgate:

```bash
curl --fail-with-body -X POST http://127.0.0.1:8000/api/v1/cupons/<coupon-id>/resgates \
  -H 'Authorization: Bearer local-manager' -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: 11111111-1111-1111-1111-111111111111' \
  --data '{}'
```

## Testes e checks

Crie um banco separado (somente na primeira execução):

```bash
docker compose -p safepass46 exec -T db createdb -U safepass safepass_test
export TEST_DATABASE_URL=postgresql+psycopg://safepass:safepass_local@127.0.0.1:55432/safepass_test
uv run pytest --cov=app --cov-report=term-missing --cov-fail-under=80
uv run ruff check . && uv run ruff format --check .
uv run mypy app
```

A suíte aplica migrations no banco terminado em `_test`; cada teste de integração
usa transação externa/savepoints, com rollback ao final, inclusive quando o
service executa commit. Ausência de `TEST_DATABASE_URL` falha explicitamente. Os
unitários rodam sem banco: `uv run pytest tests/unit`.

## Container da API

```bash
docker build -t safepass46-backend:local .
```

Imagem multi-stage, dependências congeladas e usuário sem root. As migrations
precisam rodar separadamente antes da API. Configure `DATABASE_URL` para um host
alcançável pelo container (por exemplo `host.docker.internal` ao testar local no
macOS/Windows), não seu loopback.

## Limites e decisões

Veja [decisões e integração](docs/decisions.md) para o que foi assumido, o que
ainda depende dos Desafios 1 e 3, e por que `alerts` também guarda a agenda de 7
dias. Veja [validação](docs/validation.md) para o que foi de fato executado e
conferido nesta entrega. IA (E8/US15/US16) está fora do escopo por instrução
explícita.
