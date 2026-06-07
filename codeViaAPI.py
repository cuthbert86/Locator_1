
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

WIFI_SSID = ""
WIFI_PASSWORD = ""
# Node-RED API settings
NODE_RED_URL = "http://192.168.1.17:1880/sensor-data"  # Change IP to your Node-RED server
NODE_RED_PORT = 1880
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


def setup_wifi():
    """Connect to WiFi network"""
    print(f"Connecting to WiFi: {WIFI_SSID}")
    wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
    print(f"WiFi connected! IP: {wifi.radio.ipv4_address}")
    return wifi.radio.ipv4_address

def setup_mqtt(pool):
    """Initialize and connect to MQTT broker"""
    print(f"Connecting to MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
    
    mqtt = MMQTT(
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

def get_wifi_geolocation(requests_session):
    """Get geolocation from WiFi networks using Mozilla Location Service"""
    if not USE_WIFI_GEOLOCATION:
        return None
    
    try:
        print("Scanning WiFi networks for geolocation...")
        networks = []
        
        # Scan nearby WiFi networks
        for network in wifi.radio.start_scanning_networks():
            networks.append({
                "macAddress": "".join([f"{x:02x}" for x in network.bssid]),
                "signalStrength": network.rssi
            })
            if len(networks) >= 10:  # Limit to 10 networks to save data
                break
        
        wifi.radio.stop_scanning_networks()
        
        if not networks:
            print("No WiFi networks found for geolocation")
            return None
        
        # Request geolocation from Mozilla
        url = f"https://location.services.mozilla.com/v1/geolocate?key={MOZILLA_API_KEY}"
        body = {"wifiAccessPoints": networks}
        
        response = requests_session.post(url, json=body)
        geo_data = response.json()
        
        location = {
            "latitude": round(geo_data.get("location", {}).get("lat"), 6),
            "longitude": round(geo_data.get("location", {}).get("lng"), 6),
            "accuracy": round(geo_data.get("accuracy", 0), 2)
        }
        
        print(f"Geolocation: {location}")
        return location
    
    except Exception as e:
        print(f"Error getting geolocation: {e}")
        return None

def publish_sensor_data_via_api(requests_session):
    """Collect all sensor data and publish via REST API"""
    global location_data
    
    print("\n" + "="*50)
    print(f"Publishing sensor data at {time.time()}")
    print("="*50)
    
    # Get BME280 data
    bme_data = get_bme280_data()
    if bme_data is None:
        print("Failed to read BME280 sensor")
        return False
    
    # Get WiFi geolocation
    location = get_wifi_geolocation(requests_session)
    if location:
        location_data = location
    
    # Prepare combined payload
    payload = {
        "timestamp": int(time.time()),
        "device": "CircuitPython_Sensor",
        "location": location_data,
        "sensors": {
            "bme280": bme_data
        }
    }
    
    # Publish via REST API
    try:
        api_url = "http://localhost:1880/#"  # Change this to your API endpoint
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer YOUR_API_KEY"  # Add if needed
        }
        response = requests_session.post(api_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"Data sent successfully: {json.dumps(payload)}")
            return True
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error publishing to API: {e}")
        return False
    
def publish_sensor_data_to_nodered(requests_session):
    """Collect all sensor data and publish to Node-RED via REST API"""
    global location_data
    
    print("\n" + "="*50)
    print(f"Publishing sensor data to Node-RED at {time.time()}")
    print("="*50)
    
    # Get BME280 data
    bme_data = get_bme280_data()
    if bme_data is None:
        print("Failed to read BME280 sensor")
        return False
    
    # Get WiFi geolocation
    location = get_wifi_geolocation(requests_session)
    if location:
        location_data = location
    
    # Prepare combined payload
    payload = {
        "timestamp": int(time.time()),
        "device": "CircuitPython_Sensor",
        "location": location_data,
        "sensors": {
            "bme280": bme_data
        }
    }
    
    # Send to Node-RED
    try:
        response = requests_session.post(NODE_RED_URL, json=payload)
        
        if response.status_code == 200:
            print(f"Data sent to Node-RED: {json.dumps(payload)}")
#            blink_led(3, 0.2)  # Success blink
            return True
        else:
            print(f"Node-RED Error: {response.status_code}")
#            blink_led(2, 0.3)  # Error blink
            return False
    except Exception as e:
        print(f"Error sending to Node-RED: {e}")
 #       blink_led(5, 0.1)  # Fast error blink
        return False


# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    global bme280_sensor, last_update_time
    
    print("\n" + "="*50)
    print("CircuitPython Sensor Logger - Starting")
    print("="*50 + "\n")
    
    try:
        # Setup WiFi
        setup_wifi()
        
        # Setup networking pool for requests
        pool = socketpool.SocketPool(wifi.radio)
        requests = adafruit_requests.Session(pool, ssl.create_default_context())
        
        # Setup BME280 sensor
        bme280_sensor = setup_bme280()
        
        print("\n✓ All systems initialized successfully!\n")
        
        # Main loop
        while True:
            try:
                # Check if it's time to publish data
                current_time = time.time()
                if current_time - last_update_time >= UPDATE_INTERVAL:
                    last_update_time = current_time
                    publish_sensor_data_to_nodered(requests)
                
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

