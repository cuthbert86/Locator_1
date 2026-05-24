from circuitPythonHelperCode import setup_wifi, setup_mqtt, setup_bme280, publish_sensor_data,  get_wifi_geolocation,  get_bme280_data
import time
import board
import busio
import wifi
import socketpool
import ssl
import json
from adafruit_minimqtt.adafruit_minimqtt import MQTT
#import adafruit_bme280
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_requests

WIFI_SSID = "BB"
WIFI_PASSWORD = "6KH1jk1mn0s"

MQTT_BROKER = "localhost"  # Or use your own broker
MQTT_PORT = 1883
MQTT_USERNAME = None  # Set if your broker requires auth
MQTT_PASSWORD = None
MQTT_TOPIC_PUBLISH = "circuitpython/sensordata"

# GPS/Geolocation settings
USE_WIFI_GEOLOCATION = True
MOZILLA_API_KEY = "https://location.services.mozilla.com/v1/geolocate?key=test"  # Use "test" for demo, request your own for production

# Sensor update interval (15 minutes = 900 seconds)
UPDATE_INTERVAL = 900

# ============================================================================
# GLOBAL VARIABLES
# ============================================================================
mqtt_client = None
bme280_sensor = None
last_update_time = 0
location_data = {"latitude": None, "longitude": None, "accuracy": None}


#  MAIN PROGRAM
# ============================================================================

def main():
    global mqtt_client, bme280_sensor, last_update_time
    
    print("\n" + "="*50)
    print("CircuitPython Sensor Logger - Starting")
    print("="*50 + "\n")
    
    try:
        # Setup WiFi
        setup_wifi()
        
        # Setup networking pool for requests
        pool = socketpool.SocketPool(wifi.radio)
        requests = adafruit_requests.Session(pool, ssl.create_default_context())
        
        # Setup MQTT
#        mqtt_client = setup_mqtt(pool)
        
        # Setup BME280 sensor
        bme280_sensor = setup_bme280()
        
        print("\n✓ All systems initialized successfully!\n")
        
        # Main loop
        while True:
            try:
                # Call MQTT loop to process incoming messages
#                mqtt_client.loop()
                
                # Check if it's time to publish data
                current_time = time.time()
                if current_time - last_update_time >= UPDATE_INTERVAL:
                    last_update_time = current_time
                    publish_sensor_data(requests)
                
                # Small delay to prevent busy waiting
                time.sleep(1)
            
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(5)
    
    except Exception as e:
        print(f"Fatal error: {e}")
        while True:
            time.sleep(10)

if __name__ == "__main__":
    main()

