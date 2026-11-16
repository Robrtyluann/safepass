# Banco integrado do SAFEpass — ensaio no fork

Trabalho local em `Robrtyluann/safepass`, branch `integration/banco-unificado`,
criada da `develop` em `dd175a6719ee09a4baadd00115dbb8e2dfa24d0c`.
Referências oficiais consultadas apenas para leitura:

- `feature/backend`: `1997856e01b6f0076f6fce1b07287070654ee1b0` (backend idêntico ao da base).
- `feat/squad44-historico-medico`: `30dc4b7dd393137bde495da4efef9a26506f7254`.

Foram aproveitados os módulos, models, serviços, testes e migration PostgreSQL do
Squad 44. Usuários e dependentes continuam sendo os módulos já existentes.
Frontend e Compose da raiz não foram modificados. Na etapa inicial não houve commit,
push, merge ou PR. A publicação posterior no fork é descrita no README principal.

## Banco novo e execução local

Todos os comandos abaixo partem de `backend/`. Requisitos: Python 3.12, uv,
Docker com daemon disponível e Compose. A instalação usa o lockfile existente:

```bash
uv sync --frozen
# Se o cache padrão não for gravável na nuvem:
# UV_CACHE_DIR=/workspace/.cache/uv uv sync --frozen

docker compose -p safepass-integration -f compose.integration.yaml build
docker compose -p safepass-integration -f compose.integration.yaml up -d --no-build api
curl --fail-with-body http://127.0.0.1:8001/health
```

Se o build estiver atrás de proxy HTTPS com CA privada confiável, o Dockerfile
já aceita um bundle de certificados via secret do BuildKit. Não desative TLS:

```bash
docker build --secret id=build_ca,src=/etc/ssl/certs/ca-certificates.crt \
  -t safepass-banco-unificado:local .
docker compose -p safepass-integration -f compose.integration.yaml up -d --no-build api
```

Use o bundle confiável do seu ambiente; o caminho acima foi validado nesta nuvem.
A API fica em `127.0.0.1:8001`, docs em `/docs`; banco em `127.0.0.1:55440`.
O Compose separado usa volumes `safepass-integration_integration_pgdata` e
`safepass-integration_integration_documents`, sem tocar nos volumes do Compose padrão.
O serviço `migrate` aplica apenas `alembic upgrade head`; não executa seed automático.
Os arquivos ficam em `/app/storage/documents`, gravável pelo usuário sem root.
As credenciais embutidas são exclusivamente locais. Não exponha este Compose em produção.

Alternativa sem container da API, mantendo o banco do Compose separado:

```bash
export DATABASE_URL=postgresql+psycopg://safepass:integration_local_only@127.0.0.1:55440/safepass
export DOCUMENTS_DIR=storage/documents
uv run alembic upgrade head
uv run alembic check
uv run fastapi dev app/main.py
```

Antes de cadastrar um usuário gestor na base NOVA de demonstração, inicialize os
planos (o cadastro depende do plano gratuito):

```bash
docker compose -p safepass-integration -f compose.integration.yaml exec -T api python -m scripts.seed
# API sem container: uv run python -m scripts.seed
```

Depois registre uma conta em `POST /api/v1/auth/register` e use o cookie retornado,
ou efetue login. O admin e os depoimentos de demo são opcionais, configuráveis por
variáveis de `.env.example`. Não semeie bancos antigos automaticamente.

O OCR externo Gemini é opcional, exige chave configurada de forma segura e
acesso ao serviço; não foi chamado nesta validação. O container instala Tesseract
com português. Sem chave, a aplicação usa o fallback para revisão manual.
Não envie dados médicos reais na apresentação. O OCR simulado dos testes valida
as transações e rotas, não a precisão clínica de extração.

## Atualização de banco antigo

A cadeia é linear, com um único head:

```text
d01_0001 -> 93b27d541c7e -> 66c8e1279f5c -> 1bd9c3273419
```

As três migrations anteriores foram preservadas byte a byte. A migration do
Squad 44 foi reaproveitada sem reescrita. Ela acrescenta seis tabelas:
`ocr_readings`, `documents`, `prescriptions`, `medications`, `dose_intakes`, `vaccines`.

Antes de qualquer atualização real: faça backup recuperável do banco E dos
arquivos e ensaie numa cópia. Com `DATABASE_URL` apontando para essa cópia, execute:

```bash
uv run alembic current
uv run alembic heads
uv run alembic history
# Só prossiga se a revisão e o schema corresponderem à cadeia conhecida.
uv run alembic upgrade head
uv run alembic check
```

Banco antigo em revisão conhecida recebe apenas as migrations pendentes. Banco
com tabelas mas sem histórico Alembic, revisões desconhecidas ou schema divergente
precisa de diagnóstico específico e plano de conversão; não é uma instalação nova.
Não execute `stamp`, `downgrade`, `drop`, remoção de volumes ou tentativa de recriar
as tabelas nesse banco. Não foi acessado nem atualizado nenhum banco antigo real.

## Validação reproduzível em PostgreSQL descartável

Escolha um nome de container e porta livres. Este container guarda o banco em
memória e é exclusivo de testes; não aponta para volumes existentes:

```bash
docker run -d --name safepass-integration-banco-unificado \
  -e POSTGRES_USER=safepass -e POSTGRES_PASSWORD=integration_local_only \
  -e POSTGRES_DB=safepass_test -p 127.0.0.1:55439:5432 \
  --tmpfs /var/lib/postgresql/data postgres:16-alpine
docker exec safepass-integration-banco-unificado pg_isready -U safepass
export TEST_DATABASE_URL=postgresql+psycopg://safepass:integration_local_only@127.0.0.1:55439/safepass_test
DATABASE_URL="$TEST_DATABASE_URL" uv run alembic upgrade head
DATABASE_URL="$TEST_DATABASE_URL" uv run alembic check
uv run pytest --cov=app --cov-report=term --cov-fail-under=80
uv run ruff check .
uv run ruff format --check .
uv run mypy app scripts/verify_database_upgrade.py
```

Espere `pg_isready` indicar disponibilidade antes das migrations. Para ensaiar a
atualização, crie outro banco vazio no MESMO container descartável:

```bash
docker exec safepass-integration-banco-unificado createdb -U safepass safepass_upgrade_test
DATABASE_URL=postgresql+psycopg://safepass:integration_local_only@127.0.0.1:55439/safepass_upgrade_test \
  uv run python -m scripts.verify_database_upgrade
```

O verificador recusa banco não vazio ou sem sufixo `_upgrade_test`, aplica a
revisão anterior, insere usuário, conta com saldo e dependente, atualiza ao head,
confere os dados e executa `alembic check`. Não usa downgrade ou stamp. Para novo
ensaio, escolha outro banco descartável vazio; não tente reaplicar a preparação
sobre o anterior.

## Revisão de integridade e pendências

Veja [o diagrama físico completo](DIAGRAMA_BANCO_INTEGRADO.md), com as 34 tabelas de aplicação.

- FKs médicas apontam para `users.id` e `dependents.id` existentes. O isolamento
  entre contas e a posse do dependente são validados pelo serviço; uma FK isolada
  não garante que dependente e usuário pertençam à mesma conta.
- `ocr_reading_id` é único em documentos e receitas; a confirmação bloqueia a
  leitura com `FOR UPDATE`. `dose_intakes` tem unicidade por medicamento/dia/hora.
- CHECKs cobrem tipos de documento, estados/fontes OCR, fonte de medicamento e
  duração positiva. Há testes diretos de FK, duração e unicidade no PostgreSQL.
- Exclusão de documento deixa receita/vacina com `document_id = NULL`. Exclusão
  de receita propaga para medicamentos e doses. O código recebido apaga documentos,
  medicamentos e vacinas fisicamente. A política final de retenção/soft delete de
  saúde precisa ser acordada antes de produção; não foi inventada nesta integração.
- Referências lógicas antigas sem FK física incluem `manager_accounts.manager_user_id`,
  `manager_accounts.plan_id`, `dependents.linked_user_id` e IDs externos de catálogo.
  Não foram endurecidas retroativamente: isso exige avaliar órfãos em bases reais
  e confirmar contratos com os squads. Não foi criada identidade paralela.
- O material FINAL do Squad 23 ainda não foi fornecido. Auth/plano/assinaturas
  atuais são a implementação da base, sem assumir contrato definitivo ou alterar
  regras para preencher a ausência. Gateway de pagamentos atual é simulado.
- O assistente usa schema legado incompatível. Não foram criadas tabelas duplicadas
  ou adapters fictícios para fazê-lo funcionar. `shared_with_assistant` registra
  opção no módulo médico; não estabelece integração funcional com o assistente.
- Disco local atende a apresentação com uma instância. Bucket, backup/restauração,
  retenção e consistência entre arquivo e transação exigem validação antes de produção.
- Testes HTTP de histórico médico usam JWT real, PostgreSQL e filesystem temporário,
  mas OCR falso. Gemini real, integração final do assistente e interface do frontend
  não são resultados cobertos por esta entrega.

## Evidência desta execução

Evidência inicial em [VALIDACAO_BANCO.md](VALIDACAO_BANCO.md); resultados da revisão
para publicação em [VALIDACAO_PUBLICACAO.md](VALIDACAO_PUBLICACAO.md).

## Confronto com o documento SQLite do Squad 44

A [referência recebida](REFERENCIA_SQUAD44.md) descreve o estado em 12/11/2026,
commit informado `ce87b4b`; não é um contrato PostgreSQL final aprovado.

| Referência | Adaptação existente / decisão pendente |
|---|---|
| `usuario_id` textual | `user_id UUID` com FK para `users` nos módulos médicos. |
| `dependente` próprio do Squad 44 e parentesco obrigatório | Reutiliza `dependents` do domínio compartilhado via `manager_accounts`; `bond` opcional. Confirmar responsabilidade e obrigatoriedade. |
| Bloquear exclusão de dependente com registros | FKs bloqueiam exclusão física; API permite desativação lógica. Confirmar semântica de exclusão/retenção. |
| JSON `confirmado` na leitura OCR | Não há snapshot imutável; confirmação é persistida em receita/medicamentos normalizados. Confirmar exigência de auditoria. |
| Medicamentos da receita em JSON | Linhas UUID em `medications`, com `source` e FK `prescription_id`. Confirmar contrato e importação. |
| Campo textual `periodo` | Persistência operacional em `duration_days`; texto original não é campo próprio do medicamento confirmado. Confirmar necessidade de preservá-lo. |
| Dose com `usuario_id` e `ref` textual | FK `medication_id`, unicidade medicamento/data/hora; usuário e receita inferidos dos relacionamentos. `created_at` representa a tomada. |
| Confiança 0–1 | Validação na extração; sem CHECK SQL para `confidence`. Confirmar necessidade de constraint adicional. |
| Defaults descritos no SQLite | Vários defaults são Python, não `DEFAULT` SQL; `vaccines.dose` é obrigatório na entrada atual da API. Confirmar comportamento esperado para inserções diretas/API. |
| Compartilhar com assistente | Campo booleano preservado; assistente legado incompatível e fora da entrega. |

Nomes em inglês, UUIDs, DATE/TIMESTAMPTZ/JSONB/BOOLEAN e migrations substituem as
convenções SQLite. Nenhuma dessas adaptações implica importação validada dos dados
legados ou aprovação das decisões pendentes pelos squads.
