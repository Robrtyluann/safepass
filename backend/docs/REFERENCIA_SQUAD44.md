> Documento de referência fornecido pelo usuário. Conteúdo histórico SQLite;
> consulte [BANCO_UNIFICADO.md](BANCO_UNIFICADO.md) para adaptações e divergências.

# SAFEpass (Squad 44) — banco de dados atual

Estado em 12/11/2026, commit `ce87b4b` da main. Fonte: `agente/agents/repositories/database.py`.

## Avisos para a unificação

1. **O banco hoje é SQLite, não PostgreSQL.** Os tipos abaixo são os do SQLite (`TEXT`, `INTEGER`, `REAL`). Na migração para o banco unificado, datas viram `DATE`/`TIMESTAMP`, campos JSON viram `JSONB` e `INTEGER` 0/1 vira `BOOLEAN`.
2. **Não temos tabela de usuário.** Cada registro guarda só `usuario_id` (texto) para saber de quem é. Esse campo deve passar a ser o id do usuário da tabela do login unificado (FK para ela).
3. **Dependentes são nossos.** A tabela `dependente` fica com a gente e também aponta para o usuário pelo `usuario_id`.

## Detalhes técnicos

- Banco: SQLite, um arquivo (`SAFEPASS_DB`, padrão `safepass.db`). As tabelas são criadas pela própria API ao abrir a conexão.
- Chaves estrangeiras ligadas (`PRAGMA foreign_keys = ON`).
- Datas gravadas como texto ISO 8601 (`2026-11-12` ou `2026-11-12T13:00:00+00:00`). Horários como `HH:MM`.
- Booleanos como `INTEGER` 0/1.
- Arquivos (fotos e PDFs) ficam em disco (`SAFEPASS_ARQUIVOS`); o banco guarda só o nome.

## Tabelas

### dependente

Pessoas que o usuário gerencia (filho, pai etc.).

| Coluna | Tipo | Regra |
|---|---|---|
| id | INTEGER | PK |
| usuario_id | TEXT | NOT NULL |
| nome | TEXT | NOT NULL |
| parentesco | TEXT | NOT NULL |
| data_nascimento | TEXT | |

Não pode ser apagado enquanto tiver documento, medicamento ou vacina ligados.

### documento_ocr

Uma leitura de receita por foto. Fluxo do `status`: `processando` → `revisao` → `confirmado`.

| Coluna | Tipo | Regra |
|---|---|---|
| id | INTEGER | PK |
| usuario_id | TEXT | |
| status | TEXT | NOT NULL, `processando`, `revisao` ou `confirmado` |
| origem | TEXT | `gemini`, `tesseract` ou `manual` |
| confianca | REAL | 0 a 1, uso interno |
| campos_revisar | TEXT | JSON (lista de campos), padrão `[]` |
| extraido | TEXT | JSON do que a IA leu |
| confirmado | TEXT | JSON do que o usuário confirmou: `{medico, data_receita, medicamentos}` |
| arquivo | TEXT | nome do arquivo da foto |
| mime_type | TEXT | |
| tamanho | INTEGER | bytes |
| criado_em | TEXT | NOT NULL |
| confirmado_em | TEXT | |

### receitas

Receita confirmada. Os medicamentos ficam em JSON dentro da própria linha.

| Coluna | Tipo | Regra |
|---|---|---|
| id | INTEGER | PK |
| usuario_id | TEXT | |
| medico | TEXT | |
| data_receita | TEXT | |
| medicamentos | TEXT | NOT NULL, JSON (abaixo) |
| documento_ocr_id | INTEGER | FK → documento_ocr.id |
| criado_em | TEXT | NOT NULL |

Cada item de `medicamentos`:

```json
{
  "medicamento": "Amoxicilina",
  "dose": "500 mg",
  "posologia": "8 em 8 horas",
  "periodo": "7 dias",
  "inicio": "2026-11-12",
  "primeira_dose": "08:00",
  "encerrado_em": null
}
```

### documento

Repositório de documentos do usuário ou de um dependente.

| Coluna | Tipo | Regra |
|---|---|---|
| id | INTEGER | PK |
| usuario_id | TEXT | NOT NULL |
| dependente_id | INTEGER | FK → dependente.id; nulo = do próprio usuário |
| tipo | TEXT | NOT NULL, `receita`, `exame`, `consulta`, `vacina` ou `atestado` |
| titulo | TEXT | NOT NULL |
| data_documento | TEXT | |
| arquivo | TEXT | nome do arquivo |
| mime_type | TEXT | |
| tamanho | INTEGER | bytes |
| documento_ocr_id | INTEGER | FK → documento_ocr.id (quando veio de leitura de receita) |
| compartilhado_assistente | INTEGER | NOT NULL, padrão 0; 1 = usuário autorizou o assistente de IA a ver |
| criado_em | TEXT | NOT NULL |

### medicamento

Medicamento cadastrado à mão (sem receita).

| Coluna | Tipo | Regra |
|---|---|---|
| id | INTEGER | PK |
| usuario_id | TEXT | NOT NULL |
| dependente_id | INTEGER | FK → dependente.id |
| medicamento | TEXT | NOT NULL |
| dose | TEXT | NOT NULL, padrão `''` |
| posologia | TEXT | NOT NULL, padrão `''` |
| inicio | TEXT | NOT NULL |
| duracao_dias | INTEGER | nulo = uso contínuo |
| primeira_dose | TEXT | `HH:MM` |
| encerrado_em | TEXT | preenchido = tratamento encerrado |
| criado_em | TEXT | NOT NULL |

### vacina

| Coluna | Tipo | Regra |
|---|---|---|
| id | INTEGER | PK |
| usuario_id | TEXT | NOT NULL |
| dependente_id | INTEGER | FK → dependente.id |
| nome | TEXT | NOT NULL |
| dose | TEXT | NOT NULL, padrão `''` (ex.: `2ª dose`, `reforço`) |
| data_aplicacao | TEXT | NOT NULL |
| proxima_dose | TEXT | data do lembrete |
| documento_id | INTEGER | FK → documento.id, `ON DELETE SET NULL` (comprovante) |
| compartilhado_assistente | INTEGER | NOT NULL, padrão 0 |
| criado_em | TEXT | NOT NULL |

### dose_tomada

Registro do botão "Tomei".

| Coluna | Tipo | Regra |
|---|---|---|
| id | INTEGER | PK |
| usuario_id | TEXT | NOT NULL |
| ref | TEXT | NOT NULL; `r{receita_id}-{indice}` (item de receita) ou `m{medicamento_id}` (manual) |
| data | TEXT | NOT NULL |
| horario | TEXT | NOT NULL, `HH:MM` |
| tomada_em | TEXT | NOT NULL |

`UNIQUE (usuario_id, ref, data, horario)`.

## Relações

```
dependente 1─N documento, medicamento, vacina
documento_ocr 1─1 receitas
documento_ocr 1─1 documento (tipo receita)
documento 1─N vacina (comprovante)
receitas / medicamento 1─N dose_tomada (pelo campo ref, sem FK)
```
