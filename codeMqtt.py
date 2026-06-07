
import time
import board
import busio
import wifi
import socketpool
import ssl
import json
from adafruit_minimqtt.adafruit_minimqtt import MQTT
import adafruit_bme280
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_requests

WIFI_SSID = ""
WIFI_PASSWORD = ""

MQTT_BROKER = "192.168.1.10"  # Or use your own broker
MQTT_PORT = 1883
MQTT_USERNAME = None  # Set if your broker requires auth
MQTT_PASSWORD = None
MQTT_TOPIC_PUBLISH = "sensor/data"

# GPS/Geolocation settings
USE_WIFI_GEOLOCATION = True
MOZILLA_API_KEY = "https://location.services.mozilla.com/v1/geolocate?key=test"  # Use "test" for demo, request your own for production

# Sensor update interval (15 minutes = 900 seconds)
UPDATE_INTERVAL = 30

# ============================================================================
# GLOBAL VARIABLES
# ============================================================================
mqtt_client = None
bme280_sensor = None
last_update_time = 0
# location_data = {"latitude": None, "longitude": None, "accuracy": None}


def setup_wifi():
    """Connect to WiFi network"""
    print(f"Connecting to WiFi: {WIFI_SSID}")
    wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
    print(f"WiFi connected! IP: {wifi.radio.ipv4_address}")
    return wifi.radio.ipv4_address

def setup_mqtt(pool):
    """Initialize and connect to MQTT broker"""
    print(f"Connecting to MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
    
    mqtt = MQTT(
        broker=MQTT_BROKER,
        port=MQTT_PORT,
        socket_pool=pool,
        ssl_context=None,
        username=MQTT_USERNAME,
        password=MQTT_PASSWORD,
        client_id="CircuitPython_Sensor",
        keep_alive=60
    )
    
    # Set up callback for message receipt
    def message_callback(client, topic, message):
        print(f"Message received on {topic}: {message}")
    
    mqtt.on_message = message_callback
    mqtt.connect()
    print("MQTT connected!")
    return mqtt

def setup_bme280():
    """Initialize BME280 I2C sensor"""
    print("Initializing BME280 sensor...")
    i2c = busio.I2C(board.GP1, board.GP0)  # 
    sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
    
    # Optional: Set sea level pressure for accurate altitude calculation
    # sensor.sea_level_pressure = 1013.25
    
    print("BME280 sensor initialized!")
    return sensor

def get_bme280_data():
    """Read temperature, humidity, and pressure from BME280"""
    try:
        data = {
            "timestamp": int(time.time()),
            "device": "CircuitPython_Sensor",
            "temperature_c": round(bme280_sensor.temperature, 2),
            "humidity_percent": round(bme280_sensor.relative_humidity, 2),
            "pressure_hpa": round(bme280_sensor.pressure, 2),
            "altitude_m": round(bme280_sensor.altitude, 2)
        }
        print(f"BME280 Data: {data}")
        return data
    except Exception as e:
        print(f"Error reading BME280: {e}")
        return None


def publish_sensor_data(requests_session):
    """Collect all sensor data and publish to MQTT"""
#    global location_data
    
#    print("\n" + "="*50)
    print(f"Publishing sensor data at {time.time()}")
#    print("="*50)
    
    # Get BME280 data
    bme_data = get_bme280_data()
    if bme_data is None:
        print("Failed to read BME280 sensor")
        return False
    
    # Prepare combined payload
    payload = bme_data
    
    # Publish to MQTT
    try:
        mqtt_client.publish(MQTT_TOPIC_PUBLISH, json.dumps(payload))
        print(f"Published: {json.dumps(payload)}")
        return True
    except Exception as e:
        print(f"Error publishing to MQTT: {e}")
        return False

# ============================================================================
# MAIN PROGRAM
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
        mqtt_client = setup_mqtt(pool)
        
        # Setup BME280 sensor
        bme280_sensor = setup_bme280()
        
        print("\n✓ All systems initialized successfully!\n")
        
        # Main loop
        while True:
            try:
                # Call MQTT loop to process incoming messages
                mqtt_client.loop()
                
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

