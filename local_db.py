import sqlite3
import paho.mqtt.client as mqtt
from datetime import datetime
from pathlib import Path

# Configurações
MQTT_BROKER = "localhost"
MQTT_PORT = 8883  # Porta segura
MQTT_TOPIC = "esp32/rain_sensor"  # Altere para o tópico desejado
DB_FILE = "dados_mqtt.db"

# Caminhos dos certificados gerados pelo script config_mosquitto.py (~ = diretório home do usuário)
_CERT_DIR = Path.home() / "mqtt_secure/clients/local_db"
CLIENT_CERT = str(_CERT_DIR / "local_db.crt")
CLIENT_KEY = str(_CERT_DIR / "local_db.key")
CA_CERT = str(_CERT_DIR / "ca.crt")

MQTT_USERNAME = "local_db"
MQTT_PASSWORD = "1234"

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

# Configura autenticação
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Configura TLS/mTLS
client.tls_set(ca_certs=CA_CERT, certfile=CLIENT_CERT, keyfile=CLIENT_KEY)

client.connect(MQTT_BROKER, MQTT_PORT, 60)
print(f"Escutando tópico '{MQTT_TOPIC}' no broker {MQTT_BROKER}:{MQTT_PORT}...")

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Encerrando...")
finally:
    conn.close()