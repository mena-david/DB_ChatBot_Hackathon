import mysql.connector
from mysql.connector import Error
import constants

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

def setUpIndex(pinecone_name):
    # Context Set up
    contex_items = constants.contex_items
    index = pinecone.Index(pinecone_name)

    batch_num = 0
    batches = []
    for i in range(0, len(contex_items)):
        batch_text = contex_items[i]

        res = openai.Embedding.create(
            input=batch_text, engine="text-embedding-ada-002"
        )

        embedding = res.data[0].embedding
        id = 'batch' + '_' + str(batch_num)
        meta = {'text': batch_text}

        batches.append((id, embedding, meta))
        batch_num += 1

    index.upsert(vectors=batches)
    return index
