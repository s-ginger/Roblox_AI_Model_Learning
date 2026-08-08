import time
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button

keyboard = KeyboardController()
mouse = MouseController()

print("Через 3 секунды нажму W...")
time.sleep(3)

keyboard.press("w")
time.sleep(2)
keyboard.release("w")

print("W отпущена")

print("Через 2 секунды зажму левую кнопку мыши...")
time.sleep(2)

mouse.press(Button.left)
time.sleep(2)
mouse.release(Button.left)


print("Наведи Roblox на игру...")
time.sleep(3)

for i in range(20):
    mouse.move(20, 0)
    time.sleep(0.05)



print("Готово")