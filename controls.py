import cv2 as cv

# === 상수 ===
OUTPUT_DIR = "./"
FIGSIZE = (400, 300)

RESOLUTIONS = [
    (320, 240),
    (400, 300),
    (640, 480),
    (800, 600),
]

SPEEDS = [0.25, 0.5, 1.0, 1.5, 2.0, 4.0]

# === 버튼 정의 (x1, y1, x2, y2) ===
BTN_REC    = (10,  260, 70,  290)
BTN_PAUSE  = (80,  260, 140, 290)
BTN_STOP   = (150, 260, 210, 290)
BTN_SNAP   = (220, 260, 280, 290)
BTN_SETT   = (290, 260, 390, 290)

BTN_SPD_DN = (250, 50,  290, 75)
BTN_SPD_UP = (340, 50,  380, 75)
BTN_RES_DN = (250, 90,  290, 115)
BTN_RES_UP = (340, 90,  380, 115)

# === 상태 관리 ===
state = {
    "recording": False,
    "paused": False,
    "speed": 1.0,
    "resolution_idx": 1,
    "show_settings": False,
    "screenshot": False,
}


def point_in_rect(x, y, rect):
    return rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]


def on_mouse(event, x, y, flags, param):
    if event != cv.EVENT_LBUTTONDOWN:
        return

    if state["show_settings"]:
        if point_in_rect(x, y, BTN_SPD_DN):
            idx = SPEEDS.index(state["speed"])
            if idx > 0:
                state["speed"] = SPEEDS[idx - 1]
            return
        if point_in_rect(x, y, BTN_SPD_UP):
            idx = SPEEDS.index(state["speed"])
            if idx < len(SPEEDS) - 1:
                state["speed"] = SPEEDS[idx + 1]
            return
        if point_in_rect(x, y, BTN_RES_DN):
            if state["resolution_idx"] > 0:
                state["resolution_idx"] -= 1
            return
        if point_in_rect(x, y, BTN_RES_UP):
            if state["resolution_idx"] < len(RESOLUTIONS) - 1:
                state["resolution_idx"] += 1
            return

    if point_in_rect(x, y, BTN_REC):
        state["recording"] = not state["recording"]
    elif point_in_rect(x, y, BTN_PAUSE):
        state["paused"] = not state["paused"]
    elif point_in_rect(x, y, BTN_STOP):
        if state["recording"]:
            state["recording"] = False
    elif point_in_rect(x, y, BTN_SNAP):
        state["screenshot"] = True
    elif point_in_rect(x, y, BTN_SETT):
        state["show_settings"] = not state["show_settings"]


def handle_key(key):
    if key == ord(' '):
        state["paused"] = not state["paused"]
    elif key == ord('r'):
        state["recording"] = not state["recording"]
    elif key == ord('s'):
        state["screenshot"] = True
    elif key == ord('+') or key == ord('='):
        idx = SPEEDS.index(state["speed"])
        if idx < len(SPEEDS) - 1:
            state["speed"] = SPEEDS[idx + 1]
    elif key == ord('-'):
        idx = SPEEDS.index(state["speed"])
        if idx > 0:
            state["speed"] = SPEEDS[idx - 1]
