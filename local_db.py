import sqlite3
import time
import paho.mqtt.client as mqtt
from datetime import datetime

# Configurações
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "seu/topico/aqui"  # Altere para o tópico desejado
DB_FILE = "dados_mqtt.db"

# Cria o banco e tabela se não existir
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS mensagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    payload TEXT NOT NULL
)
""")
conn.commit()

def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker com código:", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    ts = datetime.now().isoformat()
    print(f"Recebido em {ts}: {payload}")
    cursor.execute("INSERT INTO mensagens (timestamp, payload) VALUES (?, ?)", (ts, payload))
    conn.commit()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
print(f"Escutando tópico '{MQTT_TOPIC}' no broker {MQTT_BROKER}:{MQTT_PORT}...")

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Encerrando...")
finally:
    conn.close()