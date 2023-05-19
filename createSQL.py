from completion import *
from db import * 
import openai
import pinecone
import yaml
import constants

def read_yaml_config(config_file):
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config
config_file = "config.yml"
config = read_yaml_config(config_file)

db_config = config["database"]

# Set the OpenAI API key and client
openai.organization = config["api"]["openai-org"]
openai.api_key = config["api"]["openai"]
openai.Engine.list()

pinecone.init(
    api_key=config["api"]["pinecone"],
    environment="asia-northeast1-gcp"  # find next to API key in console
)
pinecone_name = config["api"]["pinecone-name"]
index = setUpIndex(pinecone_name) #only needs to be done once
#index = pinecone.Index(pinecone_name)

embedding_model = config["api"]["embedding-model"]

def enrich_schema():
    schemas = "Here are the necessary database schema definitions for the different tables and all the available columns. Only include to columns that exist on the schemas on the SQL query.\n"
    schemas += constants.DB_SCHEMA
    return schemas

def process_user_input(user_input, connection, stream=False):
    # Enrich context for generating the sql statement
    context = (
        "You are a chatbot whose main purpose is to extract data from a Database using SQL queries. Here are some facts to keep in mind. "
        "The Database ONLY has the following tables: users, organizations, organization_subscriptions, organization_members, plans, runs, entities, projects, sweeps, and teams. "
    )
    xq = openai.Embedding.create(input=user_input, engine=embedding_model)['data'][0]['embedding']
    res = index.query([xq], top_k=10, include_metadata=True) # similarities
    for match in res['matches']:
        #print(f"{match['score']:.2f}: {match['metadata']['text']}")
        context += str(match['metadata']['text'])
    
    schemas = enrich_schema()
    sql_prompt = f"{schemas}\nThe request is as follows: {user_input}\n Only output a SQL Query:\n"    
    sql_query = generate_gpt_response(sql_prompt, context)

    # print("Final Query" + final_SQL + "\n")

    # You may need to validate the generated SQL query before executing it on the database
    print(sql_query + "\n")

    if sql_query:
        # Execute the SQL query and get the results
        [succeed, results] = execute_query(sql_query, connection)
        if not succeed:
            print("Sorry there was an error in executing the generated SQL query. Will attempt to fix and retry.")
            check_sql_validity_prompt = f"Here is a database schema definition that includes all table names and columns. {schemas}.\nI ran this SQL query {sql_query}, and got this error: {results}\n Please review the query for correctness. I am using MySQL as my database system, and I want to ensure that the query succeeds. Additionally, please check for any syntax errors or potential performance issues and check the provided schema to make sure all columns referenced actually exist on the table. There is no column runs.id. There is no sweeps.id column. Please provide the corrected query without any additional explanation or text."
            sql_query = generate_gpt_response(check_sql_validity_prompt, "You an expert on SQL scrips and queries. You correct badly formed queries. Please provide the corrected query without any additional explanation or text.")

            i = sql_query.find("SELECT")

            sql_query = sql_query[i:]

            print("\nNew SQL query:\n" + sql_query + "\n")
            [succeed, results] = execute_query(sql_query, connection)
            if not succeed:
                return "Sorry there was an error in executing the generated SQL query again. Try rephrasing your question or indicating specific columns to reference."

        print("Results from the Query/DB: " + str(results))
        # Prepare the response to display the results
        display_prompt = f"Based on this request by the user:'{user_input}' we ran db query '{sql_query}' and resulted in '{results}'. Format human readable reponse and include sql query separately"

        # display_prompt = f"Prepare a response with query '{sql_query}' and result '{results}' with new line and prompts. Provide short human response"
        # display_prompt = f"Based on this request by the user:'{user_input}' we ran this Database query '{sql_query}' which gave us the following results '{results}'. Provide a human readable response"
        if stream:
            return stream_gpt_response(display_prompt, "You are a helpful assistant")
        
        return generate_gpt_response(display_prompt, "You are a helpful assistant")

    # If no SQL query was generated, ask GPT for a response
    return generate_gpt_response(user_input, "You are a helpful assistant")

def main_for_local_dev():
    # Connect to the database
    connection = connect_to_db()
    if not connection:
        print("Cannot connect to the database")
        return

    while True:
        try:
            # Get user input
            user_input = input("User: ")
            # Handle user input
            response_text = process_user_input(user_input, connection)
            print(f"Chatbot: {response_text}")
        except Exception as e:
            print("Error: ", e)
            break

    # Close the database connection
    connection.close()
