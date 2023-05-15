import openai
import mysql.connector
from mysql.connector import Error

# Set the OpenAI API key and client
openai.api_key = ""

# MySQL DB configuration
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
    cursor.execute(query)
    result = cursor.fetchall()
    return result

def generate_gpt_response(prompt):
    try:
        response = openai.Completion.create(
            engine="GPT-3.5-turbo",
            prompt=prompt,
            max_tokens=50,
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
    prompt = f"Translate the following text to an SQL query: '{user_input}'"
    sql_query = generate_gpt_response(prompt)

    # You may need to validate the generated SQL query before executing it on the database
    print(sql_query)
    if sql_query:
        # Execute the SQL query and get the results
        results = execute_query(sql_query, connection)

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
