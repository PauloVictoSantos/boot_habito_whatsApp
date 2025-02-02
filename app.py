from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import pandas as pd
from datetime import datetime
import schedule
import time
import threading
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

# Configurações Twilio
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_client = Client(account_sid, auth_token)
twilio_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
user_whatsapp_number = os.getenv('USER_WHATSAPP_NUMBER')

# Nome do arquivo CSV
DATA_FILE = 'atividades.csv'

def enviar_lembrete():
    try:
        mensagem = "⏰ Hora de registrar sua atividade! Formato: 'Atividade, Categoria'"

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

# Iniciar lembretes em outra thread para não travar o Flask
threading.Thread(target=agendar_lembretes, daemon=True).start()

def salvar_atividade_csv(atividade, categoria, user, data_inicio, data_termino):
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['data_inicio', 'data_termino', 'atividade', 'categoria', 'usuario'])
    
    nova_atividade = {
        'data_inicio': data_inicio,
        'data_termino': data_termino,
        'atividade': atividade,
        'categoria': categoria,
        'usuario': user
    }
    df = df.append(nova_atividade, ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

app = Flask(__name__)

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
        atividade, categoria = msg.split(',', 1)
        atividade, categoria = atividade.strip(), categoria.strip()
        data_inicio = datetime.now()
        data_termino = data_inicio
        salvar_atividade_csv(atividade, categoria, user, data_inicio, data_termino)
        return "✅ Atividade registrada com sucesso!"
    except Exception as e:
        return "❌ Erro: Use o formato 'Atividade, Categoria'. Exemplo: 'Academia, Saúde'"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
