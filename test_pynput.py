from pynput import keyboard
from pynput.keyboard import Key
import time

a = ""

def on_press(key):
    global a
    a = key
    if key == Key.left:
        print("left")
    if key == Key.down:
        print("stop")

listener = keyboard.Listener(
    on_press=on_press)
listener.start()

while True:

    if a == Key.down:
        break

listener.stop()
print("stopstop")
