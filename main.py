from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import os
import time
# import pprint
import sqlite3
import streamlit as st
from llama_index.core.prompts import RichPromptTemplate
load_dotenv()
def get_llm_response(x):
    llm = OpenAI(model = "gpt-4o-mini")
    res = llm.complete(x)
    return res.text

prompt=RichPromptTemplate(
    """
    You are an expert in converting English questions to SQL query!
    The SQL database has the name STUDENT and name SUBJECTthese two tabels has the following columns STUDENT - NAME, SUBJECT_CODE, 
    SECTION,MARKS\n SUBJECT - SUBJECT_CODE, SUBJECT  \n\nFor example,\nExample 1 - How many entries of records are present?, 
    the SQL command will be something like this SELECT COUNT(*) FROM STUDENT or SELECT COUNT(*) FROM SUBJECT ;
    \nExample 2 - Tell me all the students studying in Data Science class?, 
    the SQL command will have to fetch data from both the tables first need to fetch the SUBJECT related to SUBJECT_CODE \n
    be something like this 
    SELECT s.NAME, s.SECTION, s.MARKS
    FROM STUDENT s
    JOIN SUBJECT sub
    ON s.SUBJECT_CODE = sub.SUBJECT_CODE
    WHERE sub.SUBJECT = 'Data Science';
    also the sql code should not have ``` in beginning or end and sql word in output
    now based on this answer this {{ query_str }}
    """

)

prompt1 = RichPromptTemplate(
    """ you will get the out put of a SQL query \n
        SELECT s.NAME, s.SECTION, s.MARKS
        FROM STUDENT s
        JOIN SUBJECT sub
        ON s.SUBJECT_CODE = sub.SUBJECT_CODE
        WHERE sub.SUBJECT = 'Data Science';\n
        like this query answer will be like the students who are in data science are :
        after this give the answer you have to answer innatural language\n
        this is your {{sql_query}} and here is the answer {{answer}}
    """
)
# question = "give me the name of student who has enrolled in Devops"


def read_sql_query(sql,db):
    conn=sqlite3.connect(db)
    cur=conn.cursor()
    cur.execute(sql)
    rows=cur.fetchall()
    conn.commit()
    conn.close()
    for row in rows:
        print(row)
    return rows

# prompt_str = prompt.format(query_str = question)

llm = OpenAI(model = "gpt-4o-mini")
# response = llm.complete(prompt_str)

# print(response)
# response2=read_sql_query(response.text,"student_2.db")
# print(response2)

st.set_page_config(page_title="I can Retrieve Any SQL query")
st.header("txt-to-sql using llm")

question=st.text_input("Input: ",key="input")

submit=st.button("Ask the question")

prompt_str = prompt.format(query_str = question)

if submit:
    response=get_llm_response(prompt_str)
    print(response)
    response1=read_sql_query(response,"student_2.db")
    final_prompt = prompt1.format(sql_query = response, answer = response1)
    st.subheader("The REsponse is")
    answer = get_llm_response(final_prompt)

    st.code(response, language="sql")

    # results_df = read_sql_query(response, "student_2.db")
    # st.subheader("Query Results")
    # st.dataframe(results_df)  
    def stream_data():
        for word in answer.split(" "):
            yield word + " "
            time.sleep(0.02)
    # for row in response1:
    #     print(row)
    #     # st.subheader(row)
    #     row1 = str(row)
    st.write_stream(stream_data())
    




