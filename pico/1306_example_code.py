# Untested Code for running my Oled dispaly screens that I've just bought a 5 pack from the internet, instructions are on the link below this comment.  
# https://github.com/adafruit/Adafruit_CircuitPython_SSD1306
import board
import busio
import adafruit_ssd1306

# Create I2C interface
i2c = busio.I2C(board.SCL, board.SDA)

# Create display object (128x64, default I2C address 0x3C)
display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Clear the display
display.fill(0)
display.show()

# Write text
display.text("Hello!", 0, 0, 1)
display.show()
