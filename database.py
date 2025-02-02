import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),       # Obtém o valor da variável DB_HOST
        user=os.getenv("DB_USER"),       # Obtém o valor da variável DB_USER
        password=os.getenv("DB_PASSWORD"),  # Obtém o valor da variável DB_PASSWORD
        database=os.getenv("DB_DATABASE")   # Obtém o valor da variável DB_DATABASE
    )

from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM atividades")
result = cursor.fetchall()
print(result)  # Deve retornar uma lista vazia inicialmente