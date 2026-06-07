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
NODE_RED_USERNAME = "Cuthbert86"
NODE_RED_PASSWORD = "Baines0809?"

UPDATE_INTERVAL = 900
last_update_time = 0

def setup_wifi():
    """Connect to WiFi network"""
    print(f"Connecting to WiFi: {WIFI_SSID}")
    wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
    print(f"WiFi connected! IP: {wifi.radio.ipv4_address}")
    return wifi.radio.ipv4_address

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


def basic_auth_header(username, password):
    """Create Basic Auth header without base64 library"""
    auth_string = f"{username}:{password}"
    
    # Manual base64 encoding (if base64 not available)
    import binascii
    auth_bytes = auth_string.encode()
    auth_b64 = binascii.b2a_base64(auth_bytes).decode().strip()
    
    return f"Basic {auth_b64}"


def publish_sensor_data_to_nodered(requests_session):
    """Collect all sensor data and publish to Node-RED via REST API"""
    
    print("\n" + "="*50)
    print(f"Publishing sensor data to Node-RED")
    print("="*50)
    
    # Get BME280 data
    bme_data = get_bme280_data()
    if bme_data is None:
        print("Failed to read BME280 sensor")
        return False
    
    # Prepare payload
    payload = {
        "timestamp": int(time.time()),
        "device": "CircuitPython_Sensor",
        "sensors": {
            "bme280": bme_data
        }
    }
    headers = {
    "Authorization": basic_auth_header("admin", "password"),
    "Content-Type": "application/json"
    }
    
    
    # Send to Node-RED with authentication
    try:
        print(f"Connecting to Node-RED at {NODE_RED_URL}")
        response = requests_session.post(NODE_RED_URL, json=payload, headers=headers, timeout=10)
        
         for attempt in range(retries):
            try:
                print(f"Attempt {attempt + 1}/{retries}: Connecting to Node-RED...")
                response = requests_session.post(
                    NODE_RED_URL, 
                    json=payload, 
                    headers=headers, 
                    timeout=10
                )
            
                if response.status_code == 200:
                    print(f"✓ Data sent successfully!")

                    return True
                else:
                    print(f"✗ HTTP Error: {response.status_code}")
                
            except Exception as e:
                print(f"✗ Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(2)  # Wait 2 seconds before retrying
                    continue
                else:
#                blink_led(5, 0.1)
                    return False

##############################################

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

