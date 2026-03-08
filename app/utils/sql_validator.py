import sqlparse


def get_sql_operation(query: str):
    parsed = sqlparse.parse(query)

    if not parsed:
        return None

    statement = parsed[0]

    for token in statement.tokens:
        if token.ttype is None:
            value = token.value.upper().strip()
            if value.split(" ")[0]:
                return value.split(" ")[0]

    return None