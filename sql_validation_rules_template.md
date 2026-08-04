# SQL Validation Rules

This file is the single source of truth for SQL validation rules and prompts.
The `validate_sql.py` script parses this file by its `##` and `###` headers,
so please keep the structure exactly as shown below when you edit it.

Structure per section:
- `## <ENTITY_TYPE>`   -> one of COMMON, CREATE, QUERY, ALTER, DROP, DELETE, STORED_PROCEDURE
  - `### Rules`        -> bullet list of validation rules for that entity type
  - `### Prompt`       -> the instruction text sent to the AI (system-style instructions)

`COMMON` rules/prompt are always included, in addition to whichever specific
entity type is being validated.

---

## COMMON

### Rules
- The file must have a header comment block at the top containing exactly
  these labeled fields (in any order, using `--` comment lines):
  `SCRIPT NAME`, `SCRIPT CREATION DATE`, `DA NAME`, `CREATED BY`,
  `SCRIPT PURPOSE`, `SCRIPT TYPE`. All six are mandatory and none may be blank.
- `SCRIPT NAME` must exactly match the actual file name, and the file name
  must end with `.sql`.
- `SCRIPT CREATION DATE` must be a valid, real calendar date (check format
  consistency too, e.g. MM/DD/YYYY vs DD/MM/YYYY — flag if ambiguous).
- `DA NAME` and `CREATED BY` must be non-empty human names (flag placeholders
  like `TBD`, `TODO`, `XXX`, or empty values).
- `SCRIPT PURPOSE` must be a real, descriptive sentence (flag if it's empty,
  a placeholder, or just restates the script name).
- `SCRIPT TYPE` must clearly state the kind of change (e.g. "New table
  creation (DDL)", "View creation", "Stored procedure creation", "Alter
  table", etc.) and must be consistent with what the SQL body actually does.
- Every file must contain all four `USE` statements before any DDL/DML:
  `USE ROLE ...;`, `USE WAREHOUSE ...;`, `USE DATABASE ...;`,
  `USE SCHEMA ...;`. All four are mandatory, each must be non-empty, and
  each must end with a semicolon.
- Object names (tables, views, columns, procedures, roles, warehouses,
  databases, schemas) must use consistent UPPER_SNAKE_CASE or
  lower_snake_case (flag mixed casing within the same file).
- SQL keywords should be uppercase (CREATE, SELECT, FROM, WHERE, USE, etc.).
- No hardcoded credentials, connection strings, or secrets anywhere in the file.
- Run a general spell-check / typo pass on comments, aliases, and identifiers
  (e.g. "PARTU_PARTY" instead of "PARTY_PARTY") and flag anything suspicious.
- No trailing/orphaned commas, unclosed parentheses, or unterminated strings.
- Every statement must end with a semicolon.

### Prompt
You are a strict SQL code reviewer for a banking data warehouse team. You
will be given a set of validation rules and a SQL script. Check the SQL
against the rules ONE BY ONE and respond in this exact structured format:

1. Overall Result: PASS or FAIL
2. Rule-by-rule breakdown: for each rule, state Rule text -> PASS/FAIL -> short reason
3. Issues Found: bullet list of concrete issues, referencing line numbers where possible
4. Suggested Fixes: concrete corrected snippets for each issue
5. Summary: 2-3 sentence summary of overall SQL quality

Do not invent rules that are not listed. Do not skip any rule.

---

## CREATE

### Rules
- The core statement must start with `CREATE TABLE` or `CREATE OR REPLACE
  TABLE` (after the header block and `USE` statements).
- Every table must have a `PRIMARY KEY` defined, either inline or as a
  named constraint.
- The `CREATE TABLE` statement must end with a `COMMENT = '...'` clause
  describing the table's purpose, and the comment must not be empty.
- Every column must have an explicit, valid Snowflake/SQL data type (flag
  ambiguous or deprecated types).
- `NOT NULL` should be explicitly specified wherever a column logically
  cannot be null (e.g. key columns).
- Foreign-key-style columns (columns ending in `_KEY`, `_ID`, `_CD` that
  reference another entity) must be documented via comment even if no
  formal `FOREIGN KEY` constraint exists.
- Column names must be spelled correctly and consistently (no typos,
  no inconsistent abbreviations for the same concept across columns).
- No `SELECT *` anywhere in the statement.
- Table name should reflect the data it stores and match the `SCRIPT NAME`
  in the header block.

### Prompt
You are validating a CREATE TABLE / CREATE OR REPLACE TABLE statement. In
addition to the COMMON rules, apply the CREATE-specific rules provided. Pay
special attention to primary keys, the trailing table-level COMMENT clause,
column data types, nullability, and naming/spelling consistency.

---

## QUERY

### Rules
- The statement should be a `SELECT` query or a `CREATE [OR REPLACE] VIEW`
  built on one, and must be syntactically valid.
- No `SELECT *`; all output columns must be explicitly listed.
- Any primary/unique key columns referenced in `JOIN ... ON` clauses must
  correctly match the key definitions of the tables being joined.
- Joins involving more than 3 tables must include a comment explaining the
  join logic.
- The query must include comments explaining any non-obvious business logic,
  filters, or calculated columns.
- No hardcoded filter values (dates, IDs, magic numbers) without a comment
  justifying them.
- Column, table, and alias names must be spelled correctly and used
  consistently throughout the query.
- Aliases should be meaningful (avoid single, non-descriptive letters for
  complex queries with multiple joined tables).

### Prompt
You are validating a SQL query (SELECT statement or view definition). In
addition to the COMMON rules, apply the QUERY-specific rules provided. Pay
special attention to join correctness against primary/foreign keys, presence
of explanatory comments, and readability.

---

## ALTER

### Rules
- The core statement must start with `ALTER TABLE` (or `ALTER VIEW` /
  `ALTER PROCEDURE` as applicable), after the header block and `USE`
  statements.
- The target object name referenced in the `ALTER` statement must be a
  valid, fully-qualified identifier (`DATABASE.SCHEMA.OBJECT`).
- The statement must be syntactically valid for the specific ALTER
  operation used (`ADD COLUMN`, `DROP COLUMN`, `RENAME COLUMN`,
  `MODIFY COLUMN`, `SET COMMENT`, etc.).
- Any `ADD COLUMN` must specify an explicit data type and, where relevant,
  nullability.
- Any destructive operation (`DROP COLUMN`, `RENAME COLUMN`, type changes
  that could lose data) must be accompanied by a comment explaining the
  reason/impact.
- The `SCRIPT TYPE` in the header block must say this is an alter/change
  script, matching the actual operation performed.

### Prompt
You are validating an ALTER statement. In addition to the COMMON rules,
apply the ALTER-specific rules provided. Pay special attention to whether
the statement is syntactically valid for its specific operation, whether
the target object is properly qualified, and whether destructive changes
are documented.

---

## DROP

### Rules
- The core statement must start with `DROP TABLE`, `DROP VIEW`, or
  `DROP PROCEDURE` as applicable, after the header block and `USE`
  statements.
- The target object name must be a valid, fully-qualified identifier
  (`DATABASE.SCHEMA.OBJECT`).
- The script must include a comment justifying why the object is being
  dropped (avoid silent/undocumented drops).
- Recommend (and flag if missing) the use of `IF EXISTS` to avoid failures
  on objects that don't exist.
- The `SCRIPT TYPE` in the header block must explicitly indicate this is a
  drop/decommission script.
- Flag if the script drops and does not archive/backup data that appears
  to still be in active use elsewhere in the same file or comments.

### Prompt
You are validating a DROP statement. In addition to the COMMON rules, apply
the DROP-specific rules provided. Pay special attention to whether the drop
is documented, whether the target object is fully qualified, and whether
`IF EXISTS` is used safely.

---

## DELETE

### Rules
- The core statement must start with `DELETE FROM`, after the header block
  and `USE` statements.
- The statement must include a `WHERE` clause; unconditional `DELETE FROM`
  with no `WHERE` clause must be flagged as a critical issue.
- The `WHERE` clause conditions must reference valid, existing columns and
  should target keys (e.g. primary key or a clearly scoped filter) rather
  than broad, loosely-bounded conditions.
- The target table name must be a valid, fully-qualified identifier
  (`DATABASE.SCHEMA.TABLE`).
- The script should include a comment explaining why the delete is being
  performed and its expected row-count impact/scope.
- Recommend the query be wrapped in an explicit transaction
  (`BEGIN`/`COMMIT`/`ROLLBACK`) for safety, and flag if this is missing.

### Prompt
You are validating a DELETE statement. In addition to the COMMON rules,
apply the DELETE-specific rules provided. Pay special attention to whether
a WHERE clause exists and is properly scoped, and whether the deletion is
documented and transaction-safe.

---

## STORED_PROCEDURE

### Rules
- The statement must start with `CREATE [OR REPLACE] PROCEDURE`, after the
  header block and `USE` statements, and must be a syntactically valid
  procedure definition for the target SQL dialect.
- The procedure must have a header comment block inside its body (or
  immediately above it) describing purpose, input parameters, and return
  value/output.
- All input parameters must have explicit, valid data types.
- All input parameters must be validated (NULL checks / range / expected-
  value checks) before being used in logic.
- Multi-statement writes must use explicit transaction handling
  (`BEGIN` / `COMMIT` / `ROLLBACK` or equivalent).
- Error handling (`TRY`/`CATCH`, `EXCEPTION`, or dialect equivalent) must
  be present.
- No `SELECT *` anywhere inside the procedure body.
- Procedure name must follow the team's naming convention (e.g. prefixed
  with `USP_` or `SP_`) and should be spelled correctly and consistently.

### Prompt
You are validating a stored procedure definition. In addition to the
COMMON rules, apply the STORED_PROCEDURE-specific rules provided. Pay
special attention to parameter validation, transaction handling, error
handling, and whether the procedure is a syntactically valid, complete
definition.
