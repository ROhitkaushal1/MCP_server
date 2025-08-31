from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv
import sqlite3
import os
from llama_index.core.prompts import RichPromptTemplate
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sql-mcp")
# Load env
load_dotenv()

llm = OpenAI(model="gpt-4o-mini")  # You can swap this for Anthropic later if needed



@mcp.tool()
def ask_sql(question: str) -> dict:
    prompt = RichPromptTemplate(
    """
    You are an expert in converting English questions to SQL query!
    The SQL database has the name STUDENT and SUBJECT tables. 
    STUDENT - NAME, SUBJECT_CODE, SECTION, MARKS
    SUBJECT - SUBJECT_CODE, SUBJECT  
    
    Example:
    Q: How many records are present?
    A: SELECT COUNT(*) FROM STUDENT;

    Q: Tell me all the students studying in Data Science class?
    A: SELECT s.NAME, s.SECTION, s.MARKS
       FROM STUDENT s
       JOIN SUBJECT sub
       ON s.SUBJECT_CODE = sub.SUBJECT_CODE
       WHERE sub.SUBJECT = 'Data Science';

    Return only the SQL code without ``` or sql word.
    Question: {{ query_str }}
    """
)

    def read_sql_query(sql, db_path="student_2.db"):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        col_names = [desc[0] for desc in cur.description] if cur.description else []
        conn.close()
        return [dict(zip(col_names, row)) for row in rows]

    """Ask a natural language question and get structured results from the database."""
    prompt_str = prompt.format(query_str=question)
    sql_query = llm.complete(prompt_str).text.strip()
    print(f"Generated SQL: {sql_query}")
    result = read_sql_query(sql_query)
    return {"sql": sql_query, "data": result}

if __name__ == "__main__":
    mcp.run()