# This code hasn't been tested and probably doesn't work - I'm just using it as a starting point to add a new feature.
import time
import board
import busio
import displayio
import terminalio
import digitalio

from adafruit_bme280 import Adafruit_BME280_I2C
from adafruit_displayio_ssd1306 import SSD1306

# ----------------------------
# 1) I2C setup
# ----------------------------
i2c = busio.I2C(board.SCL, board.SDA)

# BME280 sensor (use 0x77 instead if needed)
bme = Adafruit_BME280_I2C(i2c, address=0x76)

# SSD1306 OLED display
displayio.release_displays()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = SSD1306(display_bus, width=128, height=64)

# ----------------------------
# 2) Button setup
# ----------------------------
button = digitalio.DigitalInOut(board.D5)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP   # button connects to GND when pressed

# ----------------------------
# 3) Create text label
# ----------------------------
group = displayio.Group()
display.show(group)

label = terminalio.Label(
    terminalio.FONT,
    text="Press button",
    color=0xFFFFFF,
    scale=1,
    x=8,
    y=20
)
group.append(label)

# ----------------------------
# 4) Helper function
# ----------------------------
def update_display():
    temp = bme.temperature
    humidity = bme.humidity
    pressure = bme.pressure / 100  # convert Pa -> hPa

    label.text = (
        f"Temp: {temp:.1f} C\n"
        f"Humidity: {humidity:.1f} %\n"
        f"Pressure: {pressure:.0f} hPa"
    )
    label.y = 8

# ----------------------------
# 5) Main loop
# ----------------------------
last_button_state = False
display_on = False

while True:
    current_button_state = not button.value  # True when button pressed

    # Detect press edge (goes from False to True)
    if current_button_state and not last_button_state:
        display_on = not display_on
        if display_on:
            update_display()
        else:
            label.text = "Press button"
            label.y = 20
        time.sleep(0.2)  # debounce delay

    last_button_state = current_button_state

    # Refresh the reading while the display is on
    if display_on:
        update_display()
        time.sleep(1.0)
    else:
        time.sleep(0.05)
