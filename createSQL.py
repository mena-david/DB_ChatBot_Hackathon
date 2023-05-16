import openai
import pinecone
import mysql.connector
from mysql.connector import Error
import constants
import json

# Set the OpenAI API key and client
openai.organization = ""
openai.api_key = ""
openai.Engine.list()

pinecone.init(
    api_key="",
    environment="us-central1-gcp"  # find next to API key in console
)

# Define your database schema as plain text here
db_schema = constants.DB_SHCEMA

conversation_examples = {
    "examples": [
        {"user": "Give me everything on user XXX", "sql": "SELECT name, id FROM users WHERE name=XXX"},
        {"user": "Is Spencer Pearson a admin user?", "sql": "SELECT * FROM users WHERE name = 'Spencer Pearson' AND admin = 1"},
        {"user": "How many runs has Firstname Lastname run", "sql": "SELECT COUNT(*) FROM runs WHERE user_id = (SELECT id FROM users WHERE name = 'Firstname Lastname');"},
    ]
}

schema_and_examples = [db_schema] + [example["user"] for example in conversation_examples["examples"]]

MODEL = "text-embedding-ada-002"
res = openai.Embedding.create(
    input=schema_and_examples, engine=MODEL
)

embedding = res.data[0].embedding
example_embeddings = res.data[1:]
id = 'db-chat-bot'

index = pinecone.Index('db-chatbot-2')

example_vectors = [(f"example-{i}", e.embedding, {"text": schema_and_examples[i+1]}) for i, e in enumerate(res.data[1:])]
meta = {'text': db_schema, 'examples': json.dumps(conversation_examples)}

index.upsert(vectors=[(id, embedding, meta)] + example_vectors)

db_config = {
    "host": "localhost",
    "port":3307,
    "user": "wandb",
    "password": "wandb",
    "database": "wandb_qa",
}

def connect_to_db(db_config):
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None

def execute_query(query, connection):
    cursor = connection.cursor()
    result = ""

    try:
        cursor.execute(query)
    except Exception as e :
        print(e)
    else:
        result = cursor.fetchall()
    return result

def generate_gpt_response(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error in generate_gpt_response: {e}")
        return "I'm sorry, but I couldn't complete your request. Please try again later."


def process_user_input(user_input, connection):
    xq = openai.Embedding.create(input=user_input, engine=MODEL)['data'][0]['embedding']
    res = index.query([xq], top_k=3, include_metadata=True)

    context = (
        "You are a chatbot whose main purpose is to extract data from a Database "
        "Database has the following tables: users, organizations, organization_subscriptions, organization_members, runs, and plans. "
        "A self-service user is a user  "
        "Enterprise users are those part of an organization who has a subscription with plan.name Enterprise"
        "Here is the necessary schema definitions for the different tables."
    )

    conversation_examples_text = ""
    for match in res['matches']:
        #print(f"{match['score']:.2f}: {match['metadata']['text']}")

        # Retrieve schema and conversation examples
        if 'examples' in match['metadata']:
            context += match['metadata']['text']
            conversation_examples = json.loads(match['metadata']['examples'])
            conversation_examples_text = "\n".join([f"Example {i + 1}\nUser: {ex['user']}\nSQL: {ex['sql']};" for i, ex in enumerate(conversation_examples["examples"])])

    context += conversation_examples_text

    prompt = f"{context} Translate the following user input to an SQL query : {user_input}"
    sql_query = generate_gpt_response(prompt)

    # You may need to validate the generated SQL query before executing it on the database
    print(sql_query)
    if sql_query:
        # Execute the SQL query and get the results
        results = execute_query(sql_query, connection)

        if not results:
            return "Sorry there was an error in executing the generated SQL query. Try rephrasing your question or indicating specific columns to refrence."

        print(" Results from the Query/DB:")
        print(results)
        # Prepare the response to display the results
        prompt = f"Prepare a response for the following query result: '{results}'"
        response_text = generate_gpt_response(prompt)
    else:
        # If no SQL query was generated, ask GPT for a response
        response_text = generate_gpt_response(user_input)

    return response_text

def main():
    # Connect to the database
    connection = connect_to_db(db_config)
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

if __name__ == "__main__":
    main()
