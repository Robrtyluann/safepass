# Evidência de validação para publicação no fork

Revisão local da branch `integration/banco-unificado`, baseada em `develop`
(`dd175a6719ee09a4baadd00115dbb8e2dfa24d0c`). Verificações concluídas em
15/11/2026 às 23:57:16 (America/Sao_Paulo), antes do commit e push.
Destino autorizado: **somente Robrtyluann/safepass, integration/banco-unificado**.
Publicação aqui significa código no GitHub, não deploy ou publicação de dados locais.

## Verificações executadas nesta revisão

| Verificação | Resultado real |
|---|---|
| `uv sync --frozen` | Passou; 91 dependências verificadas, lockfile preservado. |
| PostgreSQL descartável novo | Banco em container com tmpfs e porta dinâmica; nenhum volume existente utilizado. |
| `alembic upgrade head` | Cadeia completa instalada até `1bd9c3273419`. |
| `alembic check` | Sem novas operações; validado no descartável e no banco de demonstração. |
| Bloco de testes do README, executado sem mudar os comandos (cache uv em caminho gravável) | **210 passed em 36,02 s**, sem falhas ou skips. |
| Cobertura | **96,53%**, acima do limite de 80%. |
| `ruff check .` e `ruff format --check .` | Passaram. |
| `mypy app scripts/verify_database_upgrade.py` | Passou, 152 arquivos. |
| Atualização simulada, conforme README | Revisão `66c8e1279f5c` com usuário, conta/saldo 37 e dependente atualizada ao head sem perder esses registros; check passou. |
| Build Docker final | Passou com o bundle CA confiável via secret BuildKit; TLS permaneceu verificado. |
| Compose de integração | Banco saudável; migrations encerradas com código 0; API sem root em execução. |
| `.env` opcional | Carregado; conexão continua em `db:5432` e armazenamento em `/app/storage/documents`. |
| API Docker `/health` | 200, `status=ok`, `database=ok`. |
| Alternativa de API no host do README | Iniciada em 8002 com uvicorn; `/health` 200; processo de validação encerrado depois. |
| Exemplos Bash do README | Seed, cadastro, aprovação, empresa, colaborador, dependente e upload/download executados com sucesso; bytes iguais após restart. |
| PNG sintético do exemplo | Verificado pelo Pillow; 69 bytes, nenhum dado médico. |
| Demonstração com asserções independentes | **26 respostas HTTP com status esperado**, incluindo 403 para autoaprovação e 404 antes da aprovação. |
| Persistência | PostgreSQL e API reiniciados; registros, aprovação e vínculos preservados; arquivo idêntico e mesmos volumes antes/depois. |
| Banco compartilhado | 34 tabelas de aplicação + `alembic_version`; sem usuários/dependentes duplicados. |
| Frontend, Compose da raiz e três migrations anteriores | Sem diferenças em relação à base `develop`. |
| Links relativos do README e diff | Conferidos antes do commit. |

Hash SHA-256 do arquivo da execução com asserções antes e depois do restart:
`c550bd620e742232b3b805c5f30eac93d4e308d4fd60516d6fe022f3844572bc` (173 bytes, payload fictício).

O exemplo PNG do README também retornou hashes iguais:
`e878950f8091ec010cf5cc723bdea027a8539cf7147cfea199c2f666232dcd4e`.

## Ajustes necessários para execução/documentação

- Reaproveitados os módulos e a migration PostgreSQL do Squad 44 sobre a base integrada.
- Dockerfile instala Tesseract/português, prepara o diretório persistente gravável
  e usa `COPY --chown` para os arquivos funcionarem com usuário sem root, inclusive
  em checkouts cujos arquivos locais sejam 600/700.
- Compose próprio separa volumes de banco e arquivos; `.env` é opcional (Compose
  2.24+) e as URLs/diretórios internos são preservados pelas configurações explícitas.
- Armazenamento local foi excluído do Git e do contexto Docker; SQLite/dumps
  também foram excluídos do contexto de build. Nenhum dado enviado integra o commit.
- A descrição OpenAPI agora menciona D04. Nenhuma funcionalidade nova foi criada.
- README principal foi consolidado e os relatórios anteriores identificados como históricos.

## Falhas iniciais e solução

O build sem a CA privada desta nuvem falha com `UnknownIssuer`. O Dockerfile já
aceitava `build_ca`: forneceu-se o bundle confiável, sem desativar TLS ou alterar
checksums. O README traz os dois caminhos: build comum e build com CA privada.
O cache uv padrão desta máquina é somente leitura; foi usado
`UV_CACHE_DIR=/workspace/.cache/uv`, fora do checkout. Não houve alteração de
asserções ou desativação de testes para obter sucesso.

## Limites e verificações não executadas

- Frontend/build Next/jornadas no navegador não foram executados nesta entrega.
- Gemini externo e precisão clínica de OCR não foram validados nesta revisão.
  O ensaio anterior com Tesseract real está registrado separadamente.
- Assistente legado está fora do escopo; o campo de consentimento não resolve sua incompatibilidade.
- Material final do Squad 23 ainda pendente, sem regras inventadas para substituí-lo.
- Decisões do Squad 44 sobre dependentes, retenção, snapshot confirmado, normalização,
  período textual, constraints/defaults e conversão SQLite estão explícitas em
  [BANCO_UNIFICADO.md](BANCO_UNIFICADO.md), com link ao documento de referência recebido.
- Nenhum banco antigo real foi atualizado; o teste de atualização usa fixtures
  descartáveis na revisão anterior. Backup/restauração e perda de disco não foram simulados.
- Não houve deploy externo, merge, PR, alteração de frontend ou escrita no repositório oficial.

## Estado para apresentação

O Compose de demonstração permaneceu ativo, com dados e arquivos inteiramente
fictícios preservados. Os containers de testes são separados e usam tmpfs.
Senha/cookies de validação e `.env` ficam fora do versionamento. As contas criadas
em uma máquina não são distribuídas pelo GitHub: outra pessoa deve executar o seed
explícito e os exemplos do [README](../README.md).
