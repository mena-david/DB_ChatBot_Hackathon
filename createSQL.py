from db import *
import openai
import pinecone
import constants
import json
from flask import Flask, request, jsonify
import yaml

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
    environment="us-central1-gcp"  # find next to API key in console
)

# Define your database schema as plain text here
db_schema = constants.DB_SHCEMA

conversation_examples = {
    "examples": [
        {"user": "Give me everything on user XXX", "sql": "SELECT name, id FROM users WHERE name=XXX"},
        {"user": "Is Spencer Pearson a admin user?", "sql": "SELECT * FROM users WHERE name = 'Spencer Pearson' AND admin = 1"},
        {"user": "How many runs has Firstname Lastname run", "sql": "SELECT COUNT(*) FROM runs WHERE user_id = (SELECT id FROM users WHERE name = 'Firstname Lastname');"},
        {"user": "Get all me unique users that logged runs in the past 2 weeks?", "sql": "SELECT DISTINCT u.username FROM users u INNER JOIN runs r ON u.id = r.user_id WHERE r.created_at > DATE_SUB(NOW(), INTERVAL 2 WEEK);"},
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

index = pinecone.Index('db-chatbot')

example_vectors = [(f"example-{i}", e.embedding, {"text": schema_and_examples[i+1]}) for i, e in enumerate(res.data[1:])]
meta = {'text': db_schema, 'examples': json.dumps(conversation_examples)}

index.upsert(vectors=[(id, embedding, meta)] + example_vectors)

def stream_gpt_response(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=160,
            n=1,
            stop=None,
            temperature=0.5,
            stream=True
        )
        for line in response: 
            if 'text' in line['choices'][0]:
                yield line['choices'][0]['text']
    except Exception as e:
        print(f"Error in generate_gpt_response: {e}")
        return "I'm sorry, but I couldn't complete your request. Please try again later."

def generate_gpt_response(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=160,
            n=1,
            stop=None,
            temperature=0.5,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error in generate_gpt_response: {e}")
        return "I'm sorry, but I couldn't complete your request. Please try again later."

def generate_embedding(user_input):
    xq = openai.Embedding.create(input=user_input, engine=MODEL)['data'][0]['embedding']
    res = index.query([xq], top_k=9, include_metadata=True)

def enrich_context(res):
    context = (
        "You are a chatbot whose main purpose is to extract data from a Database. Here are some facts to keep in mind"
        "Database only has the following tables: users, organizations, organization_subscriptions, organization_members, runs, and plans"
        "Enterprise users are those part of an organization who has a subscription with plan.name Enterprise"
        "In order to determine what user belong to what organizations we need to look at the organization_members table"
        "Users have an associated stripe_customer_id and if they are the billing user for an oganization that stripe_customer_id also belongs to that organization"
        "Organizations can have multiple subscriptions and of those subscriptions of type Stripe, each has a stripe_subscription_id"
        "stripe_subscription_ids are ONLY found on the organization_subscriptions table"
        "admin users have a value of 1 on the admin column on the users table"
        "Type of subscription is found on the organization_subscription table under the subscription_type column"
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
    return context

def generate_sql_prompt(user_input):
    res = generate_embedding(user_input=user_input)
    context = enrich_context(res=res)
    prompt = f"{context}\nQuestion: {user_input}\nAnswer in the form of an SQL query:\n"
    return prompt

    # You may need to validate the generated SQL query before executing it on the database
    print(sql_query + "\n")
    if sql_query:
        # Execute the SQL query and get the results
        results = execute_query(sql_query, connection)

        if not results:
            return "Sorry there was an error in executing the generated SQL query. Try rephrasing your question or indicating specific columns to refrence."

        print("Results from the Query/DB: " + str(results))
        # Prepare the response to display the results
        prompt = f"Based on this request by the user:'{user_input}' we ran this Database query '{sql_query}' which gave us the following results '{results}'. Format the results to be readable for the user"
        response_text = generate_gpt_response(prompt, "You are a helpful assistant")
    else:
        # If no SQL query was generated, ask GPT for a response
        response_text = generate_gpt_response(user_input, "You are a helpful assistant")

    return [response_text, sql_query]

def main_for_local_dev():
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
            [response_text, query] = process_user_input(user_input, connection)
            print(f"Chatbot: {response_text}")
        except Exception as e:
            print("Error: ", e)
            break

    # Close the database connection
    connection.close()

if __name__ == '__main__':
    main()
