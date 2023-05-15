import openai
import mysql.connector
from mysql.connector import Error

# Set the OpenAI API key and client
openai.api_key = "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"

# MySQL DB configuration
db_config = {
    "host": "localhost",
    "port":3307,
    "user": "wandb",
    "password": "wandb",
    "database": "wandb_qa",
}

conversation_history = [
       {"role": "system", "content": "You are a chatbot that interacts with the Movies database, which contains information about movies, actors, directors, and genres."},
       {"role": "user", "content": "Get the top 5 highest-grossing movies."},
   ]

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
    cursor.execute(query)
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
    # Generate an SQL query using GPT
    # prompt = f"Create a SQL script for the wandb_qa Database that correctly utilizes the context given about the relation between the tables in order to asnwer this request: '{user_input}'"


    context = (
        "You are a chatbot whose main purpose is to extract data from a Database "
        "Database has the following tables: users, organizations, organization_subscriptions, organization_members, runs, teams, entities, and plans. "
        "users has the following columns and type: created_at(date), updated_at(date), id(int), email(string), auth_id(string), name(string), username(string), photo_url(string), admin(bool), stripe_customer_id(string) . "
        "organizations has the following columns and type: id(int), name(string), created_at(date), updated_at(date), org_type(string). "
        "organization_subscriptions has the following columns and type: id(int), organization_id(int), plan_id(int), privileges(string), stripe_subscription_id(string), seats(int), subscription_type(string), status(string). "
        "organization_members has the following columns and type: user_id(int), organization_id(int), role(string), is_billing_user(bool). "
        "teams has the following columns and type: user_id(int), enity_id(int), type(string) "
        "plans has the following columns and type: id(int), name(string), stripe_plan_id(string), plan_type(string). "
        "Translate the following text to an SQL query "
    )
    prompt = f"{context} User asks: {user_input}"
    sql_query = generate_gpt_response(prompt)

    # You may need to validate the generated SQL query before executing it on the database
    print(" Generated SQL Script: ")
    print(sql_query)
    if sql_query:
        # Execute the SQL query and get the results
        results = execute_query(sql_query, connection)

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
