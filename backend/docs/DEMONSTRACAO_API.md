> Evidência histórica da demonstração anterior. Para a revisão publicada, consulte
> [VALIDACAO_PUBLICACAO.md](VALIDACAO_PUBLICACAO.md). Os IDs abaixo são locais e
> os dados correspondentes não são distribuídos com o código.

# Demonstração real da API e persistência

Executada em 15/11/2026 às 18:10:23 (America/Sao_Paulo). Execução `71f21ac9a6`.
Branch: `integration/banco-unificado`, no fork `Robrtyluann/safepass`.

Foi mantida a integração PostgreSQL existente. Nenhuma funcionalidade, regra de negócio, migration, dependência ou arquivo do frontend foi alterado nesta demonstração. Este relatório é o único arquivo adicionado ao projeto nesta etapa. Nenhum commit ou push.

## Preparação e dados

- API HTTP real do Compose `safepass-integration`, com autenticação JWT real em cookie, PostgreSQL persistente e armazenamento real no volume de documentos; sem adapters locais de identidade ou mocks.
- Um administrador fictício foi inicializado pelo seed já existente e autenticado via API. Cadastro público não foi usado para criar privilégios de administrador.
- Contas de prestador, responsável da empresa e colaborador/gestor foram cadastradas via API. Todos os nomes e emails são fictícios (`example.com`).
- CNPJ sintético foi gerado para atender aos dígitos verificadores exigidos pela API; não foi consultado cadastro externo nem alegada existência de empresa real.
- O colaborador também é o gestor do dependente nesta demonstração. Nenhuma regra de elegibilidade por vínculo empresarial foi acrescentada.
- O arquivo enviado é um payload PDF mínimo fictício, com 173 bytes e sem informações médicas reais. Não foi testado OCR nem renderização do PDF em navegador.
- Senhas aleatórias e cookies foram mantidos somente em memória durante a execução; não estão neste relatório nem no repositório. Não há credenciais persistidas para reutilizar essas sessões.

## Resultados

| Fluxo | Resultado real |
|---|---|
| Prestador | Cadastro 201, status pending; perfil público 404 antes da aprovação; autoaprovação negada 403; aprovação por administrador 200; perfil público 200. |
| Empresa e colaborador | Empresa criada 201; usuário existente vinculado 201, vínculo ativo e user_id conferido. |
| Dependente e documento | Dependente criado 201; upload multipart 201 com dependent_id correto; download 200 com bytes idênticos ao enviado. |
| Depois do restart | Saúde da API/banco 200; as quatro sessões continuaram autenticadas; prestador aprovado e reviewed_by preservados; empresa, vínculo, dependente e metadados do documento iguais aos originais; download 200. |

Foram verificadas **26 requisições HTTP** com status igual ao esperado. Os 403/404 acima são resultados negativos esperados, não falhas do ensaio. Não foi reexecutada a suíte pytest nesta etapa.

## Persistência

Foi executado somente:

```bash
cd /workspace/safepass/backend
docker compose -p safepass-integration -f compose.integration.yaml restart db api
```

Após o restart, a execução aguardou `/health` responder 200 com `database=ok` antes de consultar os registros. Não houve remoção de containers ou volumes, reset, downgrade, stamp ou exclusão de registros.

Volumes conferidos antes e depois:

- Banco: `safepass-integration_integration_pgdata` → `/var/lib/postgresql/data`.
- Arquivos: `safepass-integration_integration_documents` → `/app/storage/documents`.

SHA-256 antes: `c550bd620e742232b3b805c5f30eac93d4e308d4fd60516d6fe022f3844572bc`.

SHA-256 depois: `c550bd620e742232b3b805c5f30eac93d4e308d4fd60516d6fe022f3844572bc`.

Este ensaio demonstra persistência após restart dos serviços. Não substitui teste de restauração de backup ou perda de máquina/disco.

## Identificadores preservados

| Registro | UUID |
|---|---|
| admin_user | `cbef8bb4-dc2c-4338-a780-d7fa87bfb49e` |
| provider_user | `dce41702-5b41-4825-8079-b080df4add85` |
| company_user | `b0d6c884-b36a-46fa-bd6a-7bed1e106047` |
| user_user | `2398e62c-d954-4207-adcf-8394d2283812` |
| provider | `dbd8ad5d-eb58-4a10-a466-20cad13b64b8` |
| company | `dc4d4df4-6c38-4fcd-a71b-adc6ee34bea7` |
| employee_link | `767c6911-ce82-40a3-b95e-2622358d8b2c` |
| dependent | `aaee1602-55e8-40d6-b9ef-7c4721690660` |
| document | `8f2ef52c-2c61-4336-9725-31122546c4bd` |

## Registro das requisições, em ordem

| # | Método | Caminho | HTTP real/esperado |
|---|---|---|---|
| 1 | POST | `/api/v1/auth/login` | 200/200 |
| 2 | POST | `/api/v1/auth/register` | 201/201 |
| 3 | POST | `/api/v1/auth/register` | 201/201 |
| 4 | POST | `/api/v1/auth/register` | 201/201 |
| 5 | POST | `/api/v1/providers` | 201/201 |
| 6 | GET | `/api/v1/providers/dbd8ad5d-eb58-4a10-a466-20cad13b64b8` | 404/404 |
| 7 | POST | `/api/v1/providers/dbd8ad5d-eb58-4a10-a466-20cad13b64b8/approval-decisions` | 403/403 |
| 8 | POST | `/api/v1/providers/dbd8ad5d-eb58-4a10-a466-20cad13b64b8/approval-decisions` | 200/200 |
| 9 | GET | `/api/v1/providers/dbd8ad5d-eb58-4a10-a466-20cad13b64b8` | 200/200 |
| 10 | POST | `/api/v1/companies` | 201/201 |
| 11 | POST | `/api/v1/companies/dc4d4df4-6c38-4fcd-a71b-adc6ee34bea7/employees` | 201/201 |
| 12 | POST | `/api/v1/dependentes` | 201/201 |
| 13 | POST | `/api/v1/documents` | 201/201 |
| 14 | GET | `/api/v1/documents/8f2ef52c-2c61-4336-9725-31122546c4bd/file` | 200/200 |
| 15 | GET | `/health` | 200/200 |
| 16 | GET | `/api/v1/auth/me` | 200/200 |
| 17 | GET | `/api/v1/auth/me` | 200/200 |
| 18 | GET | `/api/v1/auth/me` | 200/200 |
| 19 | GET | `/api/v1/auth/me` | 200/200 |
| 20 | GET | `/api/v1/providers/dbd8ad5d-eb58-4a10-a466-20cad13b64b8/profile` | 200/200 |
| 21 | GET | `/api/v1/providers/dbd8ad5d-eb58-4a10-a466-20cad13b64b8` | 200/200 |
| 22 | GET | `/api/v1/companies/dc4d4df4-6c38-4fcd-a71b-adc6ee34bea7` | 200/200 |
| 23 | GET | `/api/v1/companies/dc4d4df4-6c38-4fcd-a71b-adc6ee34bea7/employees` | 200/200 |
| 24 | GET | `/api/v1/dependentes` | 200/200 |
| 25 | GET | `/api/v1/documents/8f2ef52c-2c61-4336-9725-31122546c4bd` | 200/200 |
| 26 | GET | `/api/v1/documents/8f2ef52c-2c61-4336-9725-31122546c4bd/file` | 200/200 |

## Decisões do documento do Squad 44 que precisam de confirmação

A referência é `banco-de-dados.md`, estado SQLite de 12/11/2026, commit `ce87b4b`. Ela descreve o legado; não foi tratada como instrução para reverter a adaptação PostgreSQL.

1. **Responsabilidade por dependentes:** o documento diz que pertencem ao Squad 44 e apontam diretamente ao usuário. A integração reutiliza `dependents` e `manager_accounts`. Confirmar responsabilidade compartilhada, vínculo via conta e se `bond`/parentesco deve ser obrigatório.
2. **Exclusão e retenção:** a referência bloqueia apagar dependente com documentos, medicamentos ou vacinas. As FKs bloqueiam remoção física, mas a API atual permite desativação lógica. Confirmar comportamento desejado e retenção/soft delete dos registros médicos, hoje removíveis fisicamente.
3. **Auditoria da confirmação OCR:** o documento prevê JSON `confirmado`. A adaptação não guarda snapshot imutável desse JSON; mantém receita e medicamentos normalizados. Confirmar necessidade de conservar exatamente o que o usuário confirmou.
4. **Receitas e identificação das doses:** o legado usa medicamentos em JSON e referências `r{id}-{indice}`/`m{id}`. A integração usa linhas UUID e FK `medication_id`. Confirmar esse contrato e o mapeamento necessário para clientes e importação do legado.
5. **Período textual:** confirmar se `duration_days` é suficiente ou se o período original da receita precisa ser preservado como campo próprio, além dos dados extraídos do OCR.
6. **Garantias no banco:** confirmar se confiança 0–1 e formato de horário exigem CHECK SQL, além da validação da aplicação, e se defaults precisam existir também para inserções SQL diretas.
7. **Assistente e consentimento:** manter `shared_with_assistant` não resolve o schema legado incompatível. Confirmar contrato de acesso e auditoria de consentimento; não foram criadas tabelas duplicadas nem demonstrado o assistente.
8. **Importação do SQLite:** instalação PostgreSQL e atualização Alembic estão disponíveis, mas não existe conversor validado dos dados/IDs/arquivos do SQLite para a estrutura integrada. Confirmar se a apresentação exige dados legados ou somente dados fictícios novos.

O material final do Squad 23 continua pendente. O ensaio utiliza as regras atuais da base e não estabelece regras definitivas de plano, elegibilidade empresarial ou autenticação para substituir esse material.

## Limites e estado final

- API e PostgreSQL permaneceram em execução ao final; registros e arquivo fictícios foram mantidos para inspeção.
- A demonstração foi pela API, sem validar telas, proxy do frontend ou jornadas no navegador.
- Não houve acesso ao Gemini nem transmissão de dados médicos reais.
- Não foram alterados bancos externos ou o repositório oficial.
