import streamlit as st
import pyodbc
import pandas as pd
import urllib
from sqlalchemy import create_engine
import openai
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI



class DatabaseAgent:
    def __init__(self, server, database, username, password, driver):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.driver = driver
        self.engine = None
        self.db = None
        self.llm = None
        self.toolkit = None
        self.agent_executor = None
        self.connect_database()

    def connect_database(self):
        params = urllib.parse.quote_plus(
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"  
        )

        connection_string = f"mssql+pyodbc:///?odbc_connect={params}"
        self.engine = create_engine(connection_string)
        self.db = SQLDatabase(self.engine)

    def initialize_agent(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.agent_executor = create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            agent_type='openai-tools',
            verbose=False
        )

    def run_query_from_text(self, text):
        if self.agent_executor is None:
            self.initialize_agent()
        return self.agent_executor.run(text)


# Example usage
if __name__ == "__main__":
    # Database connection details
    server = '45.122.120.92,1433'
    database = 'AIDatabase'
    username = 'vsa'
    password = '!nd!@123'
    driver = 'ODBC Driver 17 for SQL Server'

    database_agent = DatabaseAgent(server, database, username, password, driver)
    #query_text = "list name of persons along with their policy id and coverage amount"
    #data = database_agent.run_query_from_text(query_text)
    #print(data)

        # Streamlit app layout
    st.title('Natural Language to SQL Query Converter')

    # Input for natural language query
    user_query = st.text_input("Enter your query in natural language:")

    # Button to run the query
    if st.button('Generate SQL Query'):
        # Use the database_agent to process the natural language query
        sql_query = database_agent.run_query_from_text(user_query)
        
        # Display the generated SQL query
        st.text_area("Generated Data:", value=sql_query, height=100)


 