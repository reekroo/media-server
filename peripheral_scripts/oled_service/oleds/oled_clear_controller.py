#!/usr/bin/env python3

from .displays.drivers.ssd1306 import SSD1306_Driver

def main():
    try:
        driver = SSD1306_Driver()        
        driver.clear()
        
        print("OLED screen cleared successfully.")
    except Exception as e:
        print(f"Failed to clear OLED screen: {e}")

if __name__ == '__main__':
    main()