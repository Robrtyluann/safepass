> Evidência histórica da validação inicial. O estado atual para publicação está em
> [VALIDACAO_PUBLICACAO.md](VALIDACAO_PUBLICACAO.md). Afirmações de ausência de admin
> ou de commit abaixo descrevem somente aquela etapa.

# Validação local — 15/11/2026

Branch local: `integration/banco-unificado`, base `develop` (`dd175a6`).
Nenhum commit criado. Consulte [o guia](BANCO_UNIFICADO.md) para os comandos.

| Verificação executada | Resultado observado |
|---|---|
| `uv sync --frozen` com cache gravável em `/workspace/.cache/uv` | 91 pacotes instalados, lockfile do Squad 44 preservado |
| PostgreSQL 16 em container exclusivo, dados em tmpfs | Disponível; nenhum volume/banco preexistente acessado |
| Banco novo: `alembic upgrade head` | 4 revisões aplicadas até `1bd9c3273419` |
| `alembic check` em PostgreSQL descartável | Sem operações pendentes |
| Atualização: revisão `66c8e1279f5c` com dados -> head | Usuário, conta com saldo 37 e dependente preservados; check passou |
| Suíte completa final `pytest --cov=app --cov-report=term --cov-fail-under=80` | **210 passed**, nenhum teste falhou/pulado; 39,53 s |
| Cobertura de aplicação | **96,53%** (4231 statements, 147 não cobertos); limite de 80% atendido |
| `ruff check .` | Passou |
| `ruff format --check .` | 213 arquivos formatados |
| `mypy app scripts/verify_database_upgrade.py` | Passou, 152 arquivos |
| Build da imagem Docker | Passou com secret `build_ca` contendo bundle confiável do ambiente |
| Compose isolado: db + migrate + api | Banco saudável, migration concluída e API executando sem root |
| HTTP `GET /health` | 200, `status=ok`, `database=ok` |
| Fluxo HTTP real no Compose | Cadastro, autenticação por cookie JWT, upload PDF fictício e download passaram |
| Persistência | Download retornou os mesmos bytes após reiniciar a API, usando volume de documentos |
| Seed de planos executado duas vezes na base nova | Ambas execuções concluídas; admin não criado por ausência de configuração |
| OCR offline real | Tesseract com idioma `por` extraiu texto sintético e exigiu revisão manual |
| `alembic check` no banco do Compose | Sem diferenças entre models e schema |
| Migrations anteriores e frontend | Sem diferenças em relação à `develop` |

## Falhas investigadas e corrigidas

1. O cache uv padrão era somente leitura. A instalação passou usando
   `UV_CACHE_DIR=/workspace/.cache/uv`, sem alterar dependências.
2. Build Docker inicial falhou por `UnknownIssuer` no proxy HTTPS. O Dockerfile
   já suportava CA via secret; o build passou fornecendo o bundle confiável,
   sem desativar TLS nem alterar checksums.
3. A imagem inicial não conseguia ler arquivos do checkout (modos locais 600/700)
   com o usuário sem root; Alembic reportava ausência de `script_location` e a
   importação da aplicação falhava com `PermissionError`. `COPY --chown` corrigiu
   a propriedade dos arquivos na imagem. Build, migrations, startup e fluxo real
   foram reexecutados com sucesso.

## Limites e estado deixado

O Compose `safepass-integration` fica executando para demonstração em loopback,
com um usuário e um documento inteiramente fictícios do smoke test. Não há admin
criado. O container `safepass-integration-banco-unificado` contém somente os bancos
descartáveis de validação; nenhum volume foi removido.

Não houve validação de atualização de banco antigo real: somente ensaio de dados
na revisão anterior. O teste de preservação verifica os registros de exemplo,
não substitui backup e ensaio com cópia representativa de uma base real.

Gemini externo não foi chamado. Precisão de OCR em receitas reais, integração do
assistente legado, material final do Squad 23, retenção/soft delete e frontend
não estão validados. Não foi feita publicação/deploy externo nem qualquer escrita
no repositório oficial. Nenhum commit, push, merge ou Pull Request foi realizado.

Para apresentar: seguir o guia, entrar com uma conta de demonstração, mostrar
as rotas `/documents`, `/prescriptions`, `/medications`, `/vaccines`, `/reminders`
e o diagrama. A apresentação via interface web ainda precisa de verificação
separada, pois esta entrega preservou o frontend e validou o backend pela API.
