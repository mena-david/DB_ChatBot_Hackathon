import mysql.connector
from mysql.connector import Error

def connect_to_db():
    db_config = {
        "host": "localhost",
        "port": 3307,
        "user": "wandb",
        "password": "wandb",
        "database": "wandb_qa",
    }

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
    except Exception as e:
        print(e)
    else:
        result = cursor.fetchall()
    return result
