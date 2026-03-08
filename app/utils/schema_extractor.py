from sqlalchemy import inspect
from sqlalchemy.engine import Engine

def extract_schema(engine: Engine):
    inspector = inspect(engine)

    schema_snapshot = {"tables": {}}

    for table_name in inspector.get_table_names(schema="public"):
        columns_info = inspector.get_columns(table_name)
        pk_info = inspector.get_pk_constraint(table_name)
        fk_info = inspector.get_foreign_keys(table_name)

        schema_snapshot["tables"][table_name] = {
            "columns": {col["name"]: str(col["type"]) for col in columns_info},
            "primary_key": pk_info.get("constrained_columns", []),
            "foreign_keys": {
                col: f"{fk['referred_table']}.{ref}"
                for fk in fk_info
                for col, ref in zip(fk["constrained_columns"], fk["referred_columns"])
            }
        }

    return schema_snapshot