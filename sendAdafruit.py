from sense_hat import SenseHat
# import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
from Adafruit_IO import Client
import requests
import subprocess

response = requests.get("https://ipinfo.io/json")
locatorData = response.json()

print(locatorData["city"], locatorData["region"], locatorData["country"])

sense = SenseHat()
ADAFRUIT_IO_USERNAME = "CuthbertB"
ADAFRUIT_IO_KEY = "aio_QbBX91bmeP5wJMj7ECvmnnoF3Dot"
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
webEndPoiint = "https://io.adafruit.com/CuthbertB/feeds/locator-data"
json_string = '{"temp": "36.2", "Humidity": "37.3", "Date": "2024-03-22 00:13:27.122036"}'
data1 = json.loads(json_string)


def truncate_float(value, digits_after_point=1):
    pow_10 = 1 ** digits_after_point
    return (float(int(value * pow_10))) / pow_10


def get_wifi_ssid():
    """Get the name of the connected WiFi network"""
    try:
        result = subprocess.run(['iwgetid', '-r'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                timeout=5)
        ssid = result.stdout.decode('utf-8').strip()
        return ssid if ssid else "Not Connected"
    except Exception as e:
        return "Error getting SSID"


temp_feed = aio.feeds('temperature')
humidity_feed = aio.feeds('humidity')
pressure_feed = aio.feeds('pressure')

start_time = time.time()
duration = 90000


# sense.show_message("Hello World!", text_colour=[255, 0, 0])


while (time.time() - start_time) < duration:
    temp = truncate_float(sense.get_temperature())
    humidity = truncate_float(sense.get_humidity())
    pressure = truncate_float(sense.get_pressure())
    timestamp = datetime.now().isoformat()
    wifi_network = get_wifi_ssid()
    print(locatorData["city"], locatorData["region"], locatorData["country"])

# Send to Adafruit IO
    aio.send(temp_feed.key, temp)
    aio.send(humidity_feed.key, humidity)
    aio.send(pressure_feed.key, pressure)
    strTemp = str(temp)
    sense.show_message(strTemp, text_colour=[255, 0, 0])
    strHumidity = str(humidity)
    sense.show_message(strHumidity, text_colour=[255, 0, 0])
    time.sleep(5)
    strPressure = str(pressure)
    sense.show_message(strPressure, text_colour=[255, 0, 0])
    dateTimestamp = str(timestamp)
# Print confirmation
    print(f"Sent - Temp: {temp:.2f}°C | Humidity: {humidity:.2f}% | Pressure: {pressure:.2f}hPa | Datetimestamp: {dateTimestamp}")
    print(f"WiFi Network: {wifi_network}")
# Wait 60 seconds before sending next batch
    time.sleep(10)

#    live_data = {
#        "temp": str(temp),
#        "Humidity": str(humidity),
#        "Date": str(timestamp),
#        }
#    data1 = json.loads(live_data)

else:
    pass
