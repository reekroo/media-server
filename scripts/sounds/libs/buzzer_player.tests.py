#!/usr/bin/env python3
import sys
sys.path.append('/home/reekroo/scripts')

from sounds.libs.buzzer_player import BuzzerPlayer
from time import sleep

print("--- Starting Buzzer Hardware Test ---")

try:
    player = BuzzerPlayer(pin=18)
    print("[OK] BuzzerPlayer initialized on pin 18.")

    print("Playing a simple note (C4 for 0.5s)...")
    player.bz.play('C4')
    sleep(0.5)
    player.bz.stop()
    print("...Note stopped.")
    
    sleep(0.5)

    print("Playing a short melody via player.play()...")
    test_melody = [('C4', 0.2), ('E4', 0.2), ('G4', 0.2)]
    player.play(test_melody)
    print("...Melody finished.")
    
    print("\n--- Test Complete ---")

except Exception as e:
    print("\n!!! AN ERROR OCCURRED !!!")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {e}")
    import traceback
    traceback.print_exc()

finally:
    if 'player' in locals() and player:
        player.close()
        print("Buzzer resources released.")