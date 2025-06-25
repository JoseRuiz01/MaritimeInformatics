import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
import json

# Load environment variables from the .env file located one directory above
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class MQTTHandler:
    def __init__(self, role):
        self.role = role.upper()
        
        # Initialize MQTT connection details from role-specific environment variables
        self.broker = os.getenv('MQTT_BROKER')
        self.port = int(os.getenv('MQTT_PORT'))
        self.username = os.getenv(f'{self.role}_MQTT_USERNAME')
        self.password = os.getenv(f'{self.role}_MQTT_PASSWORD')
        self.topic = os.getenv(f'{self.role}_POSITION_TOPIC')
        
        if not all([self.broker, self.port, self.username, self.password, self.topic]):
            raise ValueError(f"Missing required MQTT configuration for role: {self.role}")
        
        # Initialize MQTT client and set up connection
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()
    
    def publish(self, payload):
        # Add the boat identifier to the payload
        payload['boat'] = self.username
        
        # Convert the payload to a JSON string
        json_payload = json.dumps(payload)
        
        # Publish the JSON payload to the MQTT broker
        result = self.client.publish(self.topic, json_payload)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Successfully published to MQTT topic: {self.topic}")
        else:
            print(f"Failed to publish to MQTT: {result.rc}")
    
    def subscribe(self, topic_name, callback=None):
        topic = os.getenv(topic_name)
        if not topic:
            raise ValueError(f"Missing {topic_name} in environment variables")
        
        def default_callback(client, userdata, msg):
            try:
                payload = json.loads(msg.payload.decode())
                print(f"Received message on topic {msg.topic}:")
                print(f"  Latitude: {payload.get('latitude')}, Longitude: {payload.get('longitude')}")
            except json.JSONDecodeError:
                print("Received invalid JSON message")
            except KeyError:
                print("Received message doesn't contain expected data")
        
        self.client.subscribe(topic)
        self.client.message_callback_add(topic, callback or default_callback)
    
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()


