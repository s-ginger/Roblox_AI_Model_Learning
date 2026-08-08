import time

import mss
import torch
import torch.nn as nn
import torchvision
from PIL import Image
from torchvision import transforms
from pynput import keyboard
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController


# ============================================================
# Configuration
# ============================================================

MODEL_PATH = "model/best_model.pt"

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Model input
IMAGE_SIZE = 224

# How often the agent makes a decision
FPS = 15

# Toggle / exit keys
TOGGLE_KEY = keyboard.Key.f8
EXIT_KEY = keyboard.Key.f9


# ============================================================
# Model
# ============================================================

class Agent(nn.Module):
    def __init__(self):
        super().__init__()

        self.backbone = torchvision.models.resnet18()

        self.state = nn.Sequential(
            nn.Linear(1000, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
        )

        self.keyboard = nn.Linear(512, 7)
        self.mouse_buttons = nn.Linear(512, 2)
        self.mouse_pos = nn.Linear(512, 2)

    def forward(self, image):
        x = self.backbone(image)
        x = self.state(x)

        keys = self.keyboard(x)
        mouse_buttons = self.mouse_buttons(x)
        mouse_pos = self.mouse_pos(x)

        return mouse_pos, mouse_buttons, keys


# ============================================================
# Load model
# ============================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print(f"Device: {device}")

model = Agent().to(device)

checkpoint = torch.load(
    MODEL_PATH,
    map_location=device,
)

model.load_state_dict(checkpoint["model_state_dict"])

model.eval()

print("Model loaded")


# ============================================================
# Input processing
# ============================================================

transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
])


# ============================================================
# Controllers
# ============================================================

mouse = MouseController()
keyboard_controller = KeyboardController()

screen = mss.mss()


# ============================================================
# State
# ============================================================

running = True
agent_enabled = False

pressed_keys = set()
mouse_left_pressed = False
mouse_right_pressed = False


# ============================================================
# Keyboard control
# ============================================================

def on_press(key):
    global agent_enabled, running

    if key == TOGGLE_KEY:
        agent_enabled = not agent_enabled

        print(
            f"Agent: {'ON' if agent_enabled else 'OFF'}"
        )

        if not agent_enabled:
            release_all()

    elif key == EXIT_KEY:
        running = False

        print("Stopping agent...")

        release_all()


listener = keyboard.Listener(
    on_press=on_press
)

listener.start()


# ============================================================
# Release input
# ============================================================

def release_all():
    global pressed_keys
    global mouse_left_pressed
    global mouse_right_pressed

    for key in pressed_keys:
        try:
            keyboard_controller.release(key)
        except:
            pass

    pressed_keys.clear()

    if mouse_left_pressed:
        mouse.release(Button.left)
        mouse_left_pressed = False

    if mouse_right_pressed:
        mouse.release(Button.right)
        mouse_right_pressed = False


# ============================================================
# Screenshot
# ============================================================

def get_screen():
    screenshot = screen.grab({
        "top": 0,
        "left": 0,
        "width": SCREEN_WIDTH,
        "height": SCREEN_HEIGHT,
    })

    image = Image.frombytes(
        "RGB",
        screenshot.size,
        screenshot.rgb,
    )

    return image


# ============================================================
# Main inference
# ============================================================

KEYS = [
    keyboard.KeyCode.from_char("w"),
    keyboard.KeyCode.from_char("a"),
    keyboard.KeyCode.from_char("s"),
    keyboard.KeyCode.from_char("d"),
    keyboard.Key.space,
    keyboard.Key.shift,
    keyboard.Key.ctrl,
]

@torch.no_grad()
def predict(image):
    image = transform(image)

    image = image.unsqueeze(0).to(device)

    mouse_pos, mouse_buttons, keys = model(image)

    mouse_buttons = torch.sigmoid(mouse_buttons)
    keys = torch.sigmoid(keys)

    mouse_pos = mouse_pos[0]
    mouse_buttons = mouse_buttons[0]
    keys = keys[0]

    return (
        mouse_pos.cpu(),
        mouse_buttons.cpu(),
        keys.cpu(),
    )


# ============================================================
# Apply model output
# ============================================================

def apply_output(
    mouse_pos,
    mouse_buttons,
    keys,
):
    global pressed_keys
    global mouse_left_pressed
    global mouse_right_pressed

    # --------------------------------------------------------
    # Mouse position
    # --------------------------------------------------------

    
    target_x = mouse_pos[0].item()
    target_y = mouse_pos[1].item()

    center_x = SCREEN_WIDTH / 2
    center_y = SCREEN_HEIGHT / 2

    dx = target_x - center_x
    dy = target_y - center_y

    # Sensitivity
    SENSITIVITY = 0.01

    move_x = int(dx * SENSITIVITY)
    move_y = int(dy * SENSITIVITY)

    if move_x != 0 or move_y != 0:
        mouse.move(move_x, move_y)

    # --------------------------------------------------------
    # Mouse buttons
    # --------------------------------------------------------

    left = mouse_buttons[0].item() > 0.5
    right = mouse_buttons[1].item() > 0.5

    if left and not mouse_left_pressed:
        mouse.press(Button.left)
        mouse_left_pressed = True

    elif not left and mouse_left_pressed:
        mouse.release(Button.left)
        mouse_left_pressed = False

    if right and not mouse_right_pressed:
        mouse.press(Button.right)
        mouse_right_pressed = True

    elif not right and mouse_right_pressed:
        mouse.release(Button.right)
        mouse_right_pressed = False

    # --------------------------------------------------------
    # Keyboard
    # --------------------------------------------------------

    new_pressed_keys = set()

    for i, key_name in enumerate(KEYS):
        probability = keys[i].item()

        if probability > 0.2:
            new_pressed_keys.add(key_name)

    # Press newly activated keys
    for key in new_pressed_keys - pressed_keys:
        print("PRESS:", key)
        keyboard_controller.press(key)

    # Release keys that are no longer active
    for key in pressed_keys - new_pressed_keys:
        print("RELEASE:", key)
        keyboard_controller.release(key)

    pressed_keys = new_pressed_keys


# ============================================================
# Main loop
# ============================================================

print()
print("Controls:")
print("F8 - enable / disable agent")
print("F9 - exit")
print()
print("Agent is currently OFF.")

delay = 1.0 / FPS

try:
    while running:

        start = time.perf_counter()

        if agent_enabled:

            image = get_screen()

            mouse_pos, mouse_buttons, keys = predict(
                image
            )

            print(
               f"mouse={mouse_pos.tolist()} "
               f"buttons={mouse_buttons.tolist()} "
               f"keys={keys.tolist()}"
            )

            apply_output(
                mouse_pos,
                mouse_buttons,
                keys,
            )

        else:
            time.sleep(0.05)

        elapsed = time.perf_counter() - start

        sleep_time = delay - elapsed

        if sleep_time > 0:
            time.sleep(sleep_time)

finally:
    release_all()
    listener.stop()

    print("Agent stopped.")