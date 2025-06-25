import paho.mqtt.client as mqtt
import os
import ssl
from dotenv import load_dotenv

# Load environment variables from the .env file located one directory above
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class MQTTHandler:
    def __init__(self, role):
        self.role = role.upper()  # Convert to uppercase for consistency
        
        # Initialize MQTT connection details from role-specific environment variables
        self.broker = os.getenv('MQTT_BROKER')
        self.port = int(os.getenv('MQTT_PORT'))
        self.username = os.getenv(f'{self.role}_MQTT_USERNAME')
        self.password = os.getenv(f'{self.role}_MQTT_PASSWORD')
        self.topic = os.getenv(f'{self.role}_POSITION_TOPIC')
        self.use_tls = os.getenv('MQTT_USE_TLS', 'false').lower() == 'true'
        
        # Validate all required configuration is present
        if not all([self.broker, self.port, self.username, self.password, self.topic]):
            raise ValueError(f"Missing required MQTT configuration for role: {self.role}")
        
        # Initialize MQTT client and set up connection
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.username_pw_set(self.username, self.password)
        
        # Configure TLS if enabled in environment variables
        if self.use_tls:
            # Create an SSLContext that loads system CAs (which include Let's Encrypt)
            ctx = ssl.create_default_context()
            self.client.tls_set_context(ctx)
            print("TLS enabled, using system default CA certificates")
        else:
            print("TLS disabled, using non-secure connection")
        
        # Attempt to connect to MQTT broker with error handling
        try:
            print(f"Connecting to {self.broker}:{self.port} ...")
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            print("Successfully connected to MQTT broker")
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            raise
    
    # Function to publish a message to the MQTT broker
    def publish(self, payload):
        # Append the username to the payload
        payload_with_username = f"{payload}, USER: {self.username}"
        
        # Publish the modified payload to the MQTT broker
        result = self.client.publish(self.topic, payload_with_username)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Successfully published to MQTT topic: {self.topic}")
        else:
            print(f"Failed to publish to MQTT: {result.rc}")
        
        # Return the actual payload that was sent
        return payload_with_username
    
    # Function to disconnect the MQTT client
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
