import sqlparse
from sqlparse.tokens import DML


def get_sql_operation(query: str):
    parsed = sqlparse.parse(query)

    if not parsed:
        return None

    statement = parsed[0]

    for token in statement.tokens:
        if token.ttype == DML:
            return token.value.upper()

    return None