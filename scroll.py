import pyautogui
import time
import keyboard

try:
    while True:
        if keyboard.is_pressed('ctrl+q'):  # if key 'ctrl + q' is pressed 
            print('Exiting...')
            break  # finish the loop
        time.sleep(0.1) # wait for 5 seconds
        pyautogui.scroll(2500) # negative values scroll down, positive values scroll up
except KeyboardInterrupt:
    print("\nDone.")
