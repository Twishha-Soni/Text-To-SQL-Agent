import sqlglot

BLOCKED_KEYWORDS = {
    'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE', 'CREATE', 'GRANT', 'REVOKE'
}

def validate_sql(sql: str) -> tuple[bool, str | None]:
    # 1. syntax check
    try:
        parsed = sqlglot.parse_one(sql, dialect='postgres')
    except Exception as e:
        return False, f"SQL syntax error: {e}"
    
    # 2. must be a select
    if parsed.key.upper() != 'SELECT':
        return False, f"Only SELECT statements are allowed, got: {parsed.key.upper()}"
    
    # 3. blocklist check
    sql_upper = sql.upper()
    for keyword in BLOCKED_KEYWORDS:
        if keyword in sql_upper.split():
            return False, f"Blocked keyword detected: {keyword}"

    return True, None 