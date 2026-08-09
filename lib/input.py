import ctypes
import time
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)

ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("mi", MOUSEINPUT),
    ]


def move_mouse(dx, dy):
    inp = INPUT(
        type=INPUT_MOUSE,
        mi=MOUSEINPUT(
            dx=dx,
            dy=dy,
            mouseData=0,
            dwFlags=MOUSEEVENTF_MOVE,
            time=0,
            dwExtraInfo=0,
        ),
    )

    result = user32.SendInput(
        1,
        ctypes.byref(inp),
        ctypes.sizeof(INPUT),
    )

    if result != 1:
        raise ctypes.WinError(ctypes.get_last_error())


# print("Через 3 секунды нажму W...")
# time.sleep(3)

# # Клавиатуру пока оставляем через pynput
# from pynput.keyboard import Controller as KeyboardController

# keyboard = KeyboardController()

# keyboard.press("w")
# time.sleep(2)
# keyboard.release("w")

# print("W отпущена")

# print("Наведи Roblox на игру...")
# time.sleep(3)

# for i in range(20):
#     move_mouse(20, 0)
#     time.sleep(0.05)

# print("Готово")