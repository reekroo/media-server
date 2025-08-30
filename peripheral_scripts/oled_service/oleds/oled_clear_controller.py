#!/usr/bin/env python3
import os

def main():
    try:
        drv = os.getenv("OLED_DRIVER", "ssd1306").strip().lower()
        if drv == "ssd1327":
            from oleds.displays.drivers.ssd1327 import SSD1327_Driver
            driver = SSD1327_Driver()
        else:
            from oleds.displays.drivers.ssd1306 import SSD1306_Driver
            driver = SSD1306_Driver()

        driver.clear()
        print("OLED screen cleared successfully.")
        
    except Exception as e:
        print(f"Failed to clear OLED screen: {e}")

if __name__ == '__main__':
    main()
