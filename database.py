import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",      # Ou "127.0.0.1"
        user="root",           # Usuário do MySQL
        password="01470439212",  # Senha definida na instalação
        database="habitos_whatsapp"
    )

from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM atividades")
result = cursor.fetchall()
print(result)  # Deve retornar uma lista vazia inicialmente