from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Test core MQTT settings
print("=== CORE MQTT SETTINGS ===")
print(f"Broker: {os.getenv('MQTT_BROKER')}")
print(f"Port: {os.getenv('MQTT_PORT')}")
print(f"Using TLS: {os.getenv('MQTT_USE_TLS')}")

# Test role-based settings
print("\n=== ROLE-BASED SETTINGS ===")
print(f"Scout Username: {os.getenv('SCOUT_MQTT_USERNAME')}")
print(f"Team1 Connection: {os.getenv('TEAM1_CONNECTION_STRING')}")


