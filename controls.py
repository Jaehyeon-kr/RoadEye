import cv2 as cv

# === 상수 ===
OUTPUT_DIR = "./records"

RESOLUTIONS = [
    (320, 240),
    (400, 300),
    (640, 480),
    (800, 600),
]

SPEEDS = [0.25, 0.5, 1.0, 1.5, 2.0, 4.0]

BAR_HEIGHT = 30

# === 상태 관리 ===
state = {
    "recording": False,
    "paused": False,
    "speed": 1.0,
    "resolution_idx": 1,
    "show_settings": False,
    "screenshot": False,
    "trail": False,
}


def get_figsize():
    return RESOLUTIONS[state["resolution_idx"]]


def get_buttons():
    w, h = get_figsize()
    y1 = h - BAR_HEIGHT
    y2 = h - 5
    btn_rec   = (10,      y1, 70,      y2)
    btn_pause = (80,      y1, 140,     y2)
    btn_stop  = (150,     y1, 210,     y2)
    btn_snap  = (220,     y1, 280,     y2)
    btn_sett  = (w - 110, y1, w - 10,  y2)

    # 설정 패널 버튼 (우측 상단)
    btn_spd_dn = (w - 150, 50, w - 110, 75)
    btn_spd_up = (w - 60,  50, w - 20,  75)
    btn_res_dn = (w - 150, 90, w - 110, 115)
    btn_res_up = (w - 60,  90, w - 20,  115)
    btn_trail  = (w - 150, 125, w - 20, 150)

    return {
        "rec": btn_rec, "pause": btn_pause, "stop": btn_stop,
        "snap": btn_snap, "sett": btn_sett,
        "spd_dn": btn_spd_dn, "spd_up": btn_spd_up,
        "res_dn": btn_res_dn, "res_up": btn_res_up,
        "trail": btn_trail,
    }


def point_in_rect(x, y, rect):
    return rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]


def on_mouse(event, x, y, flags, param):
    if event != cv.EVENT_LBUTTONDOWN:
        return

    btns = get_buttons()

    if state["show_settings"]:
        if point_in_rect(x, y, btns["spd_dn"]):
            idx = SPEEDS.index(state["speed"])
            if idx > 0:
                state["speed"] = SPEEDS[idx - 1]
            return
        if point_in_rect(x, y, btns["spd_up"]):
            idx = SPEEDS.index(state["speed"])
            if idx < len(SPEEDS) - 1:
                state["speed"] = SPEEDS[idx + 1]
            return
        if point_in_rect(x, y, btns["res_dn"]):
            if state["resolution_idx"] > 0:
                state["resolution_idx"] -= 1
            return
        if point_in_rect(x, y, btns["res_up"]):
            if state["resolution_idx"] < len(RESOLUTIONS) - 1:
                state["resolution_idx"] += 1
            return
        if point_in_rect(x, y, btns["trail"]):
            state["trail"] = True
            return

    if point_in_rect(x, y, btns["rec"]):
        state["recording"] = not state["recording"]
    elif point_in_rect(x, y, btns["pause"]):
        state["paused"] = not state["paused"]
    elif point_in_rect(x, y, btns["stop"]):
        if state["recording"]:
            state["recording"] = False
    elif point_in_rect(x, y, btns["snap"]):
        state["screenshot"] = True
    elif point_in_rect(x, y, btns["sett"]):
        state["show_settings"] = not state["show_settings"]


def handle_key(key):
    if key == ord(' '):
        state["recording"] = not state["recording"]
    elif key == ord('p'):
        state["paused"] = not state["paused"]
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
