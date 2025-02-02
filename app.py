from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import pandas as pd
from datetime import datetime
import schedule
import time
from datetime import datetime
import threading
from dotenv import load_dotenv
import os
from database import get_db_connection

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configurações do Twilio usando variáveis de ambiente
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_client = Client(account_sid, auth_token)
twilio_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
user_whatsapp_number = os.getenv('USER_WHATSAPP_NUMBER')

DATA_FILE = 'atividades.csv'

def enviar_lembrete():
    try:
        mensagem = "⏰ Hora de registrar sua atividade! Formato: 'Atividade, Hora Início, Hora Fim, Categoria'"
        
        twilio_client.messages.create(
            body=mensagem,
            from_=twilio_whatsapp_number,
            to=user_whatsapp_number
        )
        print("Lembrete enviado!")
    except Exception as e:
        print(f"Erro ao enviar lembrete: {e}")

def agendar_lembretes():
    schedule.every(2).hours.do(enviar_lembrete)
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=agendar_lembretes, daemon=True).start()

@app.route('/webhook', methods=['POST'])
def webhook():
    user_message = request.values.get('Body', '').strip().lower()
    user_number = request.values.get('From', '')
    response = process_message(user_message, user_number)
    twilio_response = MessagingResponse()
    twilio_response.message(response)
    return str(twilio_response)

def process_message(msg, user):
    try:
        # Formato esperado: "Atividade, Categoria"
        # Exemplo: "Estudar Python, Estudos"
        atividade, categoria = msg.split(',', 1)  # Divide apenas na primeira vírgula
        atividade = atividade.strip()
        categoria = categoria.strip()

        # Captura data/hora atual
        data_inicio = datetime.now()
        data_termino = data_inicio  # Ou ajuste conforme a lógica desejada

        # Salva no banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO atividades (data_inicio, data_termino, atividade, categoria, usuario)
            VALUES (%s, %s, %s, %s, %s)
        ''', (data_inicio, data_termino, atividade, categoria, user))
        conn.commit()
        cursor.close()
        conn.close()

        return "✅ Atividade registrada com sucesso!"

    except Exception as e:
        return f"❌ Erro: Formato inválido. Use: 'Atividade, Categoria'.\nExemplo: 'Academia, Saúde'"

if __name__ == '__main__':
    app.run(port=5000, debug=True)
