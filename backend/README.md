# SAFEpass — backend integrado dos squads 23, 46, 47 e 44

Guia principal da branch **`integration/banco-unificado`** do fork
**Robrtyluann/safepass**. Uma aplicação FastAPI, um PostgreSQL 16, uma cadeia
Alembic e arquivos médicos em volume persistente. Entrega para revisão e
apresentação local; não é uma declaração de prontidão para produção.

O assistente de IA está **fora desta entrega**. O material final do Squad 23
continua pendente; usamos a implementação existente sem inventar seu contrato final.
O frontend foi preservado e suas jornadas médicas ainda não foram integradas/validadas.

## Escopo e arquitetura

| Squad | Responsabilidade implementada na base |
|---|---|
| 23 / Desafio 01 | Identidade única, autenticação JWT, usuários, planos, assinaturas simuladas, avaliações da plataforma, indicações e estatísticas |
| 46 / Desafio 02 | Marketplace, avaliações de prestadores, pontos, cupons, dependentes, alertas e dashboard |
| 47 / Desafio 03 | Prestadores, aprovação, catálogo, profissionais, empresas e colaboradores |
| 44 / Desafio 04 | Documentos, receitas/OCR revisado, medicamentos, doses, vacinas e lembretes |

Fluxo: **router → service → repository → PostgreSQL**. Schemas Pydantic validam
entrada/saída; services concentram regras e transações; repositories executam
queries SQLAlchemy. Todos os routers são registrados por `app/main.py` sob
`/api/v1`; `/health` consulta o banco. `core/database.py` fornece a sessão comum.
`users` e `dependents` são reutilizados, sem tabelas duplicadas por squad.

```text
backend/
├── app/core/                # configuração, sessão, JWT, dependências e registry
├── app/shared/              # tipos, paginação, transações e mixins
├── app/integrations/        # identidade, catálogo e OCR
├── app/modules/<domínio>/   # router, schemas, service, repository, models
├── alembic/versions/        # histórico versionado do banco
├── scripts/                # seed, modo local e ensaio de atualização
├── tests/{unit,integration}/
├── docs/                   # decisões, diagrama e evidências
├── compose.integration.yaml
├── Dockerfile
├── pyproject.toml
└── uv.lock
```

Principais relações: usuário → assinatura/plano; conta gestora → dependentes;
usuário → documentos/receitas/medicamentos/vacinas; receita → medicamentos → doses;
documento → comprovantes de vacinação; empresa → colaboradores; prestador →
serviços/profissionais. Veja o [diagrama físico completo](docs/DIAGRAMA_BANCO_INTEGRADO.md)
com 34 tabelas de aplicação. Referências lógicas sem FK e decisões pendentes
estão no [guia de banco](docs/BANCO_UNIFICADO.md).

## Pré-requisitos

- Git; Docker Engine/Desktop com daemon ativo e Docker Compose **2.24 ou superior**
  (o Compose usa `.env` opcional com `required: false`).
- Porta local **55440** para o banco e **8001** para a API disponíveis.
- Para desenvolver/testar fora do container: **Python 3.12** e **uv**. O
  `pyproject.toml` exige `>=3.12,<3.13`; dependências exatas estão em `uv.lock`.
- Para os exemplos: Bash, curl, Python 3 e utilitários `cmp`/`sha256sum`.
- A imagem instala Tesseract e idioma português. Na API sem container, instale
  esses pacotes no sistema se quiser OCR offline real.

A validação desta nuvem usou Python 3.12.14, uv 0.13.6, Docker 29.9.2 e Compose
2.40.3. A imagem usa Python 3.12 e uv 0.12.23. Node/pnpm não são necessários para
esta demonstração do backend. HTTPS e verificação de certificados devem permanecer ativos.

## Do clone ao banco e à API

Em um diretório novo, fora de qualquer checkout que contenha trabalho local:

```bash
git clone --branch integration/banco-unificado https://github.com/Robrtyluann/safepass.git
cd safepass/backend
```

Se já houver checkout, confirme `git branch --show-current` e `git status` antes
de trocar de branch; preserve alterações existentes. **Todos os comandos restantes
partem de `safepass/backend/`**, salvo indicação explícita.

Configuração local (sem sobrescrever `.env` existente):

```bash
if [ ! -e .env ]; then cp .env.example .env; fi
```

Edite `.env` localmente. Nunca o versione. O exemplo contém somente valores de
desenvolvimento e campos vazios para segredos. No Compose de integração:

- `DATABASE_URL` é sobrescrito para o serviço `db:5432` interno; o banco recebe
  `safepass` / `integration_local_only`, credenciais fictícias locais do Compose.
- `DOCUMENTS_DIR` é sobrescrito para `/app/storage/documents`, no volume persistente.
- `ENVIRONMENT=development` e `COOKIE_SECURE=false` são fixados para HTTP em loopback.
- Demais configurações de `.env`, como `JWT_SECRET`, são carregadas pela API e
  pelo serviço de migrations. Defina uma chave própria se compartilhar o ambiente;
  não exponha a configuração de demonstração à Internet.
- Para a API executada **no host**, ajuste `DATABASE_URL` no `.env` para
  `postgresql+psycopg://safepass:integration_local_only@127.0.0.1:55440/safepass`.
  O exemplo original usa 55432 para o Compose antigo de `backend/`; não confunda as portas.
- `GOOGLE_API_KEY` é opcional; sem ela o OCR cai no Tesseract e exige revisão manual.
  O assistente de IA permanece fora do escopo, independentemente dessa chave de OCR.

Build e inicialização:

```bash
docker compose -p safepass-integration -f compose.integration.yaml build
docker compose -p safepass-integration -f compose.integration.yaml up -d --wait db
docker compose -p safepass-integration -f compose.integration.yaml up -d --no-build api
docker compose -p safepass-integration -f compose.integration.yaml ps -a
curl --fail-with-body http://127.0.0.1:8001/health
```

Resultado esperado: banco saudável, `migrate` encerrado com código **0**, API em
execução e `/health` retornando `{"status":"ok","database":"ok"}`.
O serviço `migrate` aplica `alembic upgrade head` antes da API; não executa seed.
A aplicação não usa `create_all` nem aplica migrations no startup.

| Acesso local | Destino |
|---|---|
| API | `http://127.0.0.1:8001` |
| Swagger | `http://127.0.0.1:8001/docs` |
| OpenAPI | `http://127.0.0.1:8001/openapi.json` |
| PostgreSQL | `127.0.0.1:55440`, banco/usuário `safepass` |

Em uma nuvem, esses endereços são internos à máquina. Não são links de preview.
Para acompanhar falhas:

```bash
docker compose -p safepass-integration -f compose.integration.yaml logs --tail=80 migrate api db
```

### Proxy HTTPS com CA privada

Se o build falhar com `UnknownIssuer`, use somente o bundle confiável fornecido
pelo administrador do ambiente. Nesta nuvem, o comando validado é:

```bash
docker build --secret id=build_ca,src=/etc/ssl/certs/ca-certificates.crt \
  -t safepass-banco-unificado:local .
docker compose -p safepass-integration -f compose.integration.yaml up -d --no-build api
```

O secret é temporário no build. Não copie certificados privados/credenciais ao
repositório e não desative TLS. Em outra máquina, ajuste o caminho do bundle.

### Alternativa: API no host

Com Python 3.12, uv e o banco do Compose já ativo:

```bash
uv sync --frozen
export DATABASE_URL=postgresql+psycopg://safepass:integration_local_only@127.0.0.1:55440/safepass
uv run alembic upgrade head
uv run alembic check
uv run uvicorn app.main:app --host 127.0.0.1 --port 8002
```

Aqui a API está na porta **8002**, permitindo manter a API Docker em 8001.
Na nuvem, se o cache uv não for gravável, prefixe os comandos com
`UV_CACHE_DIR=/workspace/.cache/uv`. Não altere o lockfile para contornar instalação.

## Migrations: banco novo e banco existente

Cadeia única:

```text
d01_0001 → 93b27d541c7e → 66c8e1279f5c → 1bd9c3273419
```

Em **banco novo vazio**, `migrate` instala toda a cadeia. As três migrations
anteriores foram preservadas; a migration do Squad 44 acrescenta seis tabelas.
Em **banco já versionado**, faça backup recuperável do banco **e dos arquivos**,
ensaie em uma cópia e confirme a revisão antes de atualizar:

```bash
# API no host, DATABASE_URL apontando para a cópia autorizada:
uv run alembic current
uv run alembic heads
uv run alembic history
uv run alembic upgrade head
uv run alembic check
```

Não use esses comandos contra produção por engano. Banco com tabelas sem
histórico Alembic, revisão desconhecida ou schema divergente precisa de plano
específico. Não execute `stamp`, `downgrade`, remoção de tabelas ou volumes.
Não existe conversor validado dos registros do SQLite legado do Squad 44.
O ensaio de atualização disponível cobre a revisão PostgreSQL anterior, não uma
importação de SQLite. Detalhes em [BANCO_UNIFICADO.md](docs/BANCO_UNIFICADO.md).

## Preservar dados, arquivos e reiniciar

O projeto Compose separa dois volumes:

- `safepass-integration_integration_pgdata`: dados PostgreSQL.
- `safepass-integration_integration_documents`: arquivos enviados.

Para reiniciar sem apagá-los:

```bash
docker compose -p safepass-integration -f compose.integration.yaml restart db api
# Aguarde a saúde do banco e a API responder /health antes de usá-la.
curl --fail-with-body http://127.0.0.1:8001/health
```

Para parar: `docker compose -p safepass-integration -f compose.integration.yaml stop`.
Para voltar: use os comandos `up` acima. Não remova volumes. Após alterar `.env`,
`restart` não recarrega configuração: execute `up -d --no-build api` para recriar
os serviços necessários preservando volumes. Reinício não substitui backup.

## Autenticação e dados fictícios de demonstração

A API normal usa autenticação **real**: senha Argon2id, JWT em cookie httpOnly
ou Bearer, refresh token e autorização por papel. A aprovação exige administrador;
cadastro público não cria admin. O modo local `uv run python -m scripts.dev`
substitui identidade dos módulos D02/D03 por tokens fictícios (`local-manager`,
`local-owner`, `local-admin` etc.). Ele não é o servidor do Compose e não foi usado
para provar estes fluxos reais; não o exponha publicamente. O pagamento atual é
simulado e não realiza cobranças.

Inicialize somente os planos e um admin **fictício de demonstração**, usando o
seed existente. Os valores abaixo são exemplos exclusivamente locais; substitua
as senhas antes de qualquer compartilhamento:

```bash
docker compose -p safepass-integration -f compose.integration.yaml exec -T \
  -e ADMIN_EMAIL=admin-demo@example.com -e ADMIN_PASSWORD=DemoAdmin12345 \
  -e SEED_DEMO_DATA=false api python -m scripts.seed
```

O seed é idempotente, não substitui senha de admin já existente e não sobrescreve
planos alterados. Não o aplique automaticamente a bancos antigos. Nenhuma conta
fictícia ou arquivo enviado vai para o GitHub: apenas código, migrations e configuração.

### Exemplos pela API real

Execute em uma sessão Bash em `backend/`, após iniciar os serviços e o seed acima.
Os cookies ficam em diretório temporário privado; nunca os versione. Use dados
fictícios, não documentos reais de pacientes.

```bash
API=http://127.0.0.1:8001
DEMO_RUN=$(date +%s)
DEMO_DIR=$(mktemp -d)
chmod 700 "$DEMO_DIR"
json_id() { python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])'; }

# Administrador real, criado pelo seed: login retorna 200.
curl --fail-with-body -sS -c "$DEMO_DIR/admin.cookies" \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin-demo@example.com","password":"DemoAdmin12345"}' \
  "$API/api/v1/auth/login"

# Usuário/gestor que também será colaborador: cadastro retorna 201.
USER_ID=$(curl --fail-with-body -sS -c "$DEMO_DIR/user.cookies" \
  -H 'Content-Type: application/json' \
  -d "{\"full_name\":\"Gestor Ficticio Demo\",\"email\":\"gestor-$DEMO_RUN@example.com\",\"password\":\"DemoUsuario12345\",\"account_type\":\"user\"}" \
  "$API/api/v1/auth/register" | python3 -c 'import json,sys; print(json.load(sys.stdin)["user"]["id"])')

# Identidade de prestador e perfil pendente: ambos retornam 201.
curl --fail-with-body -sS -c "$DEMO_DIR/provider.cookies" \
  -H 'Content-Type: application/json' \
  -d "{\"full_name\":\"Prestador Ficticio Demo\",\"email\":\"prestador-$DEMO_RUN@example.com\",\"password\":\"DemoPrestador12345\",\"account_type\":\"provider\"}" \
  "$API/api/v1/auth/register"
PROVIDER_ID=$(curl --fail-with-body -sS -b "$DEMO_DIR/provider.cookies" \
  -H 'Content-Type: application/json' \
  -d "{\"display_name\":\"Clinica Ficticia $DEMO_RUN\"}" \
  "$API/api/v1/providers" | json_id)

# Aprovação pelo admin: 200, status approved; o próprio prestador receberia 403.
curl --fail-with-body -sS -b "$DEMO_DIR/admin.cookies" \
  -H 'Content-Type: application/json' \
  -d '{"decision":"approved","reason":"Demonstracao ficticia local"}' \
  "$API/api/v1/providers/$PROVIDER_ID/approval-decisions"
curl --fail-with-body -sS "$API/api/v1/providers/$PROVIDER_ID"

# Identidade de empresa: 201.
curl --fail-with-body -sS -c "$DEMO_DIR/company.cookies" \
  -H 'Content-Type: application/json' \
  -d "{\"full_name\":\"Responsavel Ficticio Demo\",\"email\":\"empresa-$DEMO_RUN@example.com\",\"password\":\"DemoEmpresa12345\",\"account_type\":\"company\"}" \
  "$API/api/v1/auth/register"

# CNPJ sintético com dígitos verificadores, sem consulta a cadastro real.
DEMO_CNPJ=$(python3 - <<'PY'
import secrets
s = ''.join(str(secrets.randbelow(10)) for _ in range(12))
for weights in ([5,4,3,2,9,8,7,6,5,4,3,2], [6,5,4,3,2,9,8,7,6,5,4,3,2]):
    remainder = sum(int(d)*w for d,w in zip(s, weights)) % 11
    s += str(0 if remainder < 2 else 11-remainder)
print(s)
PY
)
COMPANY_ID=$(curl --fail-with-body -sS -b "$DEMO_DIR/company.cookies" \
  -H 'Content-Type: application/json' \
  -d "{\"legal_name\":\"Empresa Ficticia $DEMO_RUN\",\"trade_name\":\"Demo sem operacao real\",\"cnpj\":\"$DEMO_CNPJ\"}" \
  "$API/api/v1/companies" | json_id)
curl --fail-with-body -sS -b "$DEMO_DIR/company.cookies" \
  -H 'Content-Type: application/json' \
  -d "{\"user_id\":\"$USER_ID\",\"employee_number\":\"DEMO-$DEMO_RUN\",\"department\":\"Demonstracao\",\"role\":\"employee\"}" \
  "$API/api/v1/companies/$COMPANY_ID/employees"

# Dependente e documento vinculado: 201 em cada criação.
DEPENDENT_ID=$(curl --fail-with-body -sS -b "$DEMO_DIR/user.cookies" \
  -H 'Content-Type: application/json' \
  -d '{"type":"person","name":"Dependente Ficticio Demo","bond":"filho ficticio"}' \
  "$API/api/v1/dependentes" | json_id)
# PNG sintético válido de 1x1; sem informação médica.
python3 - "$DEMO_DIR/arquivo.png" <<'PY'
import base64,sys
from pathlib import Path
Path(sys.argv[1]).write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4//8/AAX+Av4N70a4AAAAAElFTkSuQmCC'))
PY
DOCUMENT_ID=$(curl --fail-with-body -sS -b "$DEMO_DIR/user.cookies" \
  -F type=exam -F title='Imagem ficticia de demonstracao' \
  -F "dependent_id=$DEPENDENT_ID" -F "file=@$DEMO_DIR/arquivo.png;type=image/png" \
  "$API/api/v1/documents" | json_id)
curl --fail-with-body -sS -b "$DEMO_DIR/user.cookies" \
  "$API/api/v1/documents/$DOCUMENT_ID/file" -o "$DEMO_DIR/antes.png"
cmp "$DEMO_DIR/arquivo.png" "$DEMO_DIR/antes.png"

# Reinicia PostgreSQL E API, mantendo os volumes e as variáveis desta sessão.
docker compose -p safepass-integration -f compose.integration.yaml restart db api
# Até 60 tentativas; interrompe se a API/banco não recuperarem a saúde.
READY=0
for attempt in $(seq 1 60); do
  if curl --fail -sS "$API/health" > /dev/null 2>&1; then READY=1; break; fi
  sleep 1
done
test "$READY" = 1 || { echo 'API indisponível após restart'; exit 1; }

curl --fail-with-body -sS "$API/api/v1/providers/$PROVIDER_ID"
curl --fail-with-body -sS -b "$DEMO_DIR/company.cookies" "$API/api/v1/companies/$COMPANY_ID"
curl --fail-with-body -sS -b "$DEMO_DIR/company.cookies" "$API/api/v1/companies/$COMPANY_ID/employees"
curl --fail-with-body -sS -b "$DEMO_DIR/user.cookies" "$API/api/v1/dependentes"
curl --fail-with-body -sS -b "$DEMO_DIR/user.cookies" "$API/api/v1/documents/$DOCUMENT_ID"
curl --fail-with-body -sS -b "$DEMO_DIR/user.cookies" \
  "$API/api/v1/documents/$DOCUMENT_ID/file" -o "$DEMO_DIR/depois.png"
cmp "$DEMO_DIR/antes.png" "$DEMO_DIR/depois.png"
sha256sum "$DEMO_DIR/antes.png" "$DEMO_DIR/depois.png"
```

Os dois hashes devem ser iguais. Os registros ficam no banco para inspeção;
`DEMO_DIR` contém apenas arquivos e cookies temporários, fora do checkout.
As sessões expiram; se necessário, faça login novamente com as contas fictícias.

## Consultar tabelas na apresentação

```bash
docker compose -p safepass-integration -f compose.integration.yaml exec -T db \
  psql -U safepass -d safepass -c '\dt' -c 'SELECT version_num FROM alembic_version;'
docker compose -p safepass-integration -f compose.integration.yaml exec db \
  psql -U safepass -d safepass
```

No console `psql`:

```sql
\d documents
\d medications
\d company_employees
SELECT id, display_name, status FROM providers LIMIT 10;
SELECT id, legal_name FROM companies LIMIT 10;
SELECT company_id, user_id, active FROM company_employees LIMIT 10;
SELECT id, name, account_id FROM dependents LIMIT 10;
SELECT id, dependent_id, title, shared_with_assistant FROM documents LIMIT 10;
\q
```

Evite selecionar hashes de senha ou tokens para exibição. Os dados e arquivos
locais não fazem parte da publicação no GitHub.

## Testes reproduzíveis sem tocar no banco de demonstração

Execute em `backend/`, com Python 3.12/uv. O container abaixo é exclusivo de testes,
com dados em tmpfs e porta livre atribuída pelo Docker; não usa volumes existentes.

```bash
uv sync --frozen
TEST_CONTAINER=safepass-validation-$(date +%s)
docker run -d --name "$TEST_CONTAINER" \
  -e POSTGRES_USER=safepass -e POSTGRES_PASSWORD=test_local_only \
  -e POSTGRES_DB=safepass_test -p 127.0.0.1::5432 \
  --tmpfs /var/lib/postgresql/data postgres:16-alpine
TEST_PORT=$(docker port "$TEST_CONTAINER" 5432/tcp | awk -F: '{print $NF}')
READY=0
for attempt in $(seq 1 60); do
  if docker exec "$TEST_CONTAINER" pg_isready -U safepass -d safepass_test > /dev/null 2>&1; then READY=1; break; fi
  sleep 1
done
test "$READY" = 1 || { echo 'PostgreSQL de testes indisponível'; exit 1; }
export TEST_DATABASE_URL="postgresql+psycopg://safepass:test_local_only@127.0.0.1:$TEST_PORT/safepass_test"
DATABASE_URL="$TEST_DATABASE_URL" uv run alembic upgrade head
DATABASE_URL="$TEST_DATABASE_URL" uv run alembic check
uv run pytest --cov=app --cov-report=term-missing --cov-fail-under=80
uv run ruff check .
uv run ruff format --check .
uv run mypy app scripts/verify_database_upgrade.py

# Atualização simulada em OUTRO banco vazio, terminado em _upgrade_test:
docker exec "$TEST_CONTAINER" createdb -U safepass safepass_upgrade_test
DATABASE_URL="postgresql+psycopg://safepass:test_local_only@127.0.0.1:$TEST_PORT/safepass_upgrade_test" \
  uv run python -m scripts.verify_database_upgrade
```

A suíte exige `TEST_DATABASE_URL` PostgreSQL com nome terminado em `_test`; sem
ela os testes de integração falham explicitamente. O verificador de atualização
recusa banco preenchido, aplica a revisão anterior, cria fixtures e confere a
preservação de usuário, saldo e dependente após upgrade. Nunca usa stamp/downgrade.
Os unitários isolados podem ser executados com `uv run pytest tests/unit`.

## Problemas comuns

| Sintoma | Ação |
|---|---|
| `UnknownIssuer` no build | Use o bundle CA confiável com `--secret id=build_ca`, como acima; preserve TLS. |
| Cache uv somente leitura | Use `UV_CACHE_DIR` em diretório gravável fora do checkout. |
| Porta ocupada | Confira os serviços existentes; não apague volumes para liberar portas. Escolha uma configuração local alternativa e ajuste seus URLs. |
| `migrate` falha | Leia os logs; confirme URL/revisão e permissões. Não force com stamp. |
| `Plano gratuito não configurado` no cadastro | Rode o seed explícito na base nova de demonstração. |
| Login do admin falha | O seed não troca senhas de admins existentes; use a senha definida anteriormente ou outro email fictício. |
| 401 / 403 | Verifique cookie/sessão e papel; somente admin aprova prestador. Não substitua autenticação real por adapter para apresentar sucesso. |
| Upload sem permissão | A imagem usa usuário sem root; mantenha o volume em `/app/storage/documents` e a propriedade definida no Dockerfile. |
| Mudou `.env`, mas API manteve valor | Recrie serviços com `up`; `restart` preserva o ambiente antigo do container. |
| OCR Gemini indisponível | Sem chave/rede/quota, usa Tesseract para revisão; precisão clínica não foi validada. |
| Site não mostra os módulos médicos | O frontend foi preservado; a API nova não cria telas. Veja limitações abaixo. |

## Limitações e documentos de apoio

- **Frontend:** telas/clientes médicos e jornada no navegador não foram validados.
  O frontend principal usa painel parcial; seu proxy aponta por padrão à porta
  8000, enquanto este Compose usa 8001. Uma demonstração pela API não prova a interface.
- **Squad 23:** o documento final está pendente; elegibilidade, contratos e gateway
  de pagamento definitivos não foram presumidos. O gateway atual é simulado.
- **Squad 44:** o SQLite de referência virou PostgreSQL/UUID e nomes em inglês;
  receitas e doses foram normalizadas, reutilizando dependentes. Ainda precisam de
  confirmação: responsabilidade por dependentes, parentesco opcional, desativação
  lógica/retenção, snapshot de confirmação OCR, período textual da receita,
  constraints/defaults SQL e conversão dos dados legados. A confiança 0–1 é
  validada na extração, mas não possui CHECK no banco. Veja o relatório detalhado.
- **Assistente:** legado incompatível, fora da entrega. `shared_with_assistant`
  não constitui integração funcional; nenhuma tabela duplicada foi criada.
- **Produção:** disco local atende uma instância de demonstração; backup/restauração,
  retenção, armazenamento compartilhado, segredos e deploy precisam de trabalho próprio.

Documentos (relativos a este README):

- [Banco unificado: decisões, atualização segura e referência Squad 44](docs/BANCO_UNIFICADO.md).
- [Diagrama físico](docs/DIAGRAMA_BANCO_INTEGRADO.md).
- [Validação para publicação desta revisão](docs/VALIDACAO_PUBLICACAO.md).
- [Validação inicial, histórica](docs/VALIDACAO_BANCO.md).
- [Demonstração real anterior com IDs e hashes](docs/DEMONSTRACAO_API.md).
- [Contratos D01 e decisões prévias](docs/INTEGRACAO.md).
- [Integração original D01/D02/D03, histórica](docs/INTEGRACAO_BACKENDS.md).

O histórico documenta o que foi executado em cada etapa; use a validação para
publicação para os resultados atuais. Dados de apresentação, `.env`, cookies,
SQLite, dumps, arquivos médicos, volumes, caches e ambientes virtuais não são versionados.
