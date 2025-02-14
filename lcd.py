from rpi_lcd import LCD
from signal import pause

lcd = LCD()

try:
    lcd.text("Hello World!",1)
    pause()
    
except KeyboardInterrupt:
    pass

finally:
    lcd.clear()
    