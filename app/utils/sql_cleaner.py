import re


def clean_sql_response(llm_output: str) -> str:
    cleaned = re.sub(r"```sql|```", "", llm_output, flags=re.IGNORECASE)

    cleaned = " ".join(cleaned.split())

    return cleaned