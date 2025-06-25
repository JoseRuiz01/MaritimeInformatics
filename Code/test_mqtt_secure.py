import ssl
import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import time

load_dotenv()

broker   = os.getenv("MQTT_BROKER")
port     = int(os.getenv("MQTT_PORT", 8883))
username = os.getenv("MQTT_USERNAME")
password = os.getenv("MQTT_PASSWORD")
use_tls  = os.getenv("MQTT_USE_TLS", "false").lower() == "true"

def on_connect(client, userdata, flags, rc):
    print("Connected" if rc==0 else f"Connect failed ({rc})")
    client.subscribe("test/lab04")

def on_message(client, userdata, msg):
    print(f"Received: {msg.topic} -> {msg.payload.decode()}")

client = mqtt.Client()
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message

if use_tls:
    # create an SSLContext that loads system CAs (which include Let's Encrypt)
    ctx = ssl.create_default_context()
    client.tls_set_context(ctx)
    print("TLS enabled, using system default CA certificates")

print(f"Connecting to {broker}:{port} ...")
client.connect(broker, port, keepalive=60)
client.loop_start()

time.sleep(2)
for i in range(3):
    msg = f"Test message {i+1}"
    client.publish("test/lab04", msg)
    print("Published:", msg)
    time.sleep(1)

time.sleep(5)
client.loop_stop()
client.disconnect()
