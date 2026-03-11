def build_sql_prompt(schema: dict, history: str, question: str):

    return f"""
You are an expert SQL assistant.

Database schema:
{schema}

Conversation history:
{history}

User question:
{question}

Return ONLY the SQL query.
"""


def build_answer_prompt(question: str, result: list):

    return f"""
User asked:
{question}

Query result:
{result}

Explain the result clearly to the user.
"""

def build_chat_title_prompt(question: str):
    return f"""
User asked:
{question}

Based on this first question, generate a suitable title for the chat.
"""