import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# MQTT settings from .env
broker = os.getenv('MQTT_BROKER')
port = int(os.getenv('MQTT_PORT'))
username = os.getenv('MQTT_USERNAME')
password = os.getenv('MQTT_PASSWORD')

# Callback functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected successfully to {broker}:{port}")
        # Subscribe to test topic
        client.subscribe("test/lab04")
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    print(f"Received: {msg.topic} -> {msg.payload.decode()}")

# Create MQTT client
client = mqtt.Client()
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message

# Connect and start loop
print(f"Connecting to {broker}:{port} as {username}...")
client.connect(broker, port, 60)
client.loop_start()

# Publish test messages
time.sleep(2)  # Wait for connection
for i in range(3):
    message = f"Test message {i+1} from Lab04"
    client.publish("test/lab04", message)
    print(f"Published: {message}")
    time.sleep(1)

# Keep running for a bit to receive messages
time.sleep(5)
client.loop_stop()
client.disconnect()
