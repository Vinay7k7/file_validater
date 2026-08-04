#!/usr/bin/env python3
"""
validate_sql.py

Usage:
    python validate_sql.py <sql_file> <TYPE>

Example:
    python validate_sql.py party.sql CREATE

TYPE must be one of: CREATE, QUERY, ALTER, DROP, DELETE, STORED_PROCEDURE
(case-insensitive)

What it does:
1. Loads the SQL file the dev/user gives it.
2. Loads sql_validation_rules.yaml (the dev-owned rules file).
3. Pulls out the COMMON rules/prompt (always applied) + the rules/prompt
   for the given TYPE.
4. Sends the combined rules + prompt + SQL file to the AI.
5. Prints the AI's validation response to the terminal.
"""

import os
import sys
import yaml

# --------------------------------------------------------------------------
# Config — edit these to change where the rules file lives or which AI to use
# --------------------------------------------------------------------------

RULES_FILE = os.environ.get("SQL_VALIDATION_RULES_FILE", "sql_validation_rules.yaml")

PROVIDER = "anthropic"          # "anthropic" or "openai"
MODEL = "claude-sonnet-4-6"     # e.g. "gpt-4o" if PROVIDER = "openai"
API_KEY = os.environ.get("ANTHROPIC_API_KEY")  # use OPENAI_API_KEY if PROVIDER = "openai"


def call_ai(system_prompt: str, user_prompt: str) -> str:
    if PROVIDER == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=API_KEY)
        resp = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")

    elif PROVIDER == "openai":
        import openai
        client = openai.OpenAI(api_key=API_KEY)
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content

    else:
        sys.exit(f"Unknown PROVIDER: {PROVIDER}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python validate_sql.py <sql_file> <TYPE>")
        print("TYPE: CREATE | QUERY | ALTER | DROP | DELETE | STORED_PROCEDURE")
        sys.exit(1)

    sql_file = sys.argv[1]
    entity_type = sys.argv[2].strip().lower()

    if not os.path.isfile(sql_file):
        sys.exit(f"SQL file not found: {sql_file}")
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    if not os.path.isfile(RULES_FILE):
        sys.exit(f"Rules file not found: {RULES_FILE}")
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        rules = yaml.safe_load(f)

    common = rules.get("common", {}) or {}
    entity = rules.get(entity_type, {}) or {}

    if not entity:
        valid_types = [k for k in rules.keys() if k != "common"]
        sys.exit(f"'{entity_type}' is not a valid TYPE. Valid types: {', '.join(valid_types)}")

    # Merge common + entity-specific prompt and rules
    system_prompt = (common.get("prompt", "") + "\n\n" + entity.get("prompt", "")).strip()

    all_rules = (common.get("rules", []) or []) + (entity.get("rules", []) or [])
    rules_text = "\n".join(f"- {r}" for r in all_rules)

    user_prompt = (
        f"Validation Rules:\n{rules_text}\n\n"
        f"SQL file to validate ({os.path.basename(sql_file)}):\n"
        f"```sql\n{sql_content}\n```"
    )

    print(f"Validating {sql_file} as {entity_type.upper()} ...\n")
    result = call_ai(system_prompt, user_prompt)
    print(result)


if __name__ == "__main__":
    main()
