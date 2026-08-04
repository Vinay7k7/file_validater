# SQL Validator (AI-powered, YAML rules)

Validates a SQL file against rules defined in a YAML file, using an AI
model, and prints the result to the terminal.

## Files
- `sql_validation_rules.yaml` — the dev-owned rules file. `common:` rules
  are always applied, plus a block per type: `create`, `query`, `alter`,
  `drop`, `delete`, `stored_procedure` (each with `rules:` and `prompt:`).
- `validate_sql.py` — the script.

## Usage

```bash
python validate_sql.py <sql_file> <TYPE>
```

Example:
```bash
python validate_sql.py party.sql CREATE
```

`<TYPE>` is one of `CREATE`, `QUERY`, `ALTER`, `DROP`, `DELETE`,
`STORED_PROCEDURE` (case-insensitive).

The script loads `party.sql`, pulls the `common` rules/prompt + the
`create` rules/prompt out of the YAML, sends both plus the SQL to the AI,
and prints the AI's response.

## Setup
```bash
pip install pyyaml anthropic     # or: pip install pyyaml openai
export ANTHROPIC_API_KEY=sk-ant-...   # or OPENAI_API_KEY
```

## Config (top of validate_sql.py)
```python
RULES_FILE = os.environ.get("SQL_VALIDATION_RULES_FILE", "sql_validation_rules.yaml")
PROVIDER = "anthropic"          # or "openai"
MODEL = "claude-sonnet-4-6"     # e.g. "gpt-4o" if PROVIDER = "openai"
API_KEY = os.environ.get("ANTHROPIC_API_KEY")
```
- **Rules file location**: put `sql_validation_rules.yaml` anywhere and
  either set `SQL_VALIDATION_RULES_FILE` as an env var, or just leave the
  file next to the script.
- **Switching AI provider**: change `PROVIDER`/`MODEL`/`API_KEY` at the
  top of the file — no other code changes needed.

## Editing rules (dev workflow)
Edit `sql_validation_rules.yaml` directly — add/remove items under any
`rules:` list, or edit a `prompt:` block. No code changes needed for rule
or prompt content changes.
