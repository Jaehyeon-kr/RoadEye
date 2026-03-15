import cv2 as cv
from controls import state, get_figsize, get_buttons, RESOLUTIONS, BAR_HEIGHT


def draw_button(img, rect, text, bg_color, text_color=(255, 255, 255)):
    cv.rectangle(img, (rect[0], rect[1]), (rect[2], rect[3]), bg_color, -1)
    cv.rectangle(img, (rect[0], rect[1]), (rect[2], rect[3]), (200, 200, 200), 1)
    text_size = cv.getTextSize(text, cv.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
    tx = rect[0] + (rect[2] - rect[0] - text_size[0]) // 2
    ty = rect[1] + (rect[3] - rect[1] + text_size[1]) // 2
    cv.putText(img, text, (tx, ty), cv.FONT_HERSHEY_SIMPLEX, 0.4, text_color, 1)


def draw_control_bar(img):
    w, h = get_figsize()
    btns = get_buttons()

    overlay = img.copy()
    cv.rectangle(overlay, (0, h - BAR_HEIGHT - 5), (w, h), (40, 40, 40), -1)
    cv.addWeighted(overlay, 0.7, img, 0.3, 0, img)

    rec_color = (0, 0, 200) if state["recording"] else (80, 80, 80)
    draw_button(img, btns["rec"], "REC", rec_color)

    pause_color = (0, 140, 200) if state["paused"] else (80, 80, 80)
    pause_text = "PLAY" if state["paused"] else "PAUSE"
    draw_button(img, btns["pause"], pause_text, pause_color)

    draw_button(img, btns["stop"], "STOP", (60, 60, 180))
    draw_button(img, btns["snap"], "SNAP", (140, 100, 20))

    sett_color = (160, 120, 0) if state["show_settings"] else (80, 80, 80)
    draw_button(img, btns["sett"], "SETTINGS", sett_color)


def draw_settings_panel(img):
    if not state["show_settings"]:
        return

    w, _ = get_figsize()
    btns = get_buttons()

    overlay = img.copy()
    px1, py1 = w - 160, 35
    px2, py2 = w - 5, 160
    cv.rectangle(overlay, (px1, py1), (px2, py2), (30, 30, 30), -1)
    cv.addWeighted(overlay, 0.8, img, 0.2, 0, img)
    cv.rectangle(img, (px1, py1), (px2, py2), (200, 200, 200), 1)

    cv.putText(img, f"Speed: {state['speed']}x", (px1 + 15, 67),
               cv.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    draw_button(img, btns["spd_dn"], "-", (80, 80, 80))
    draw_button(img, btns["spd_up"], "+", (80, 80, 80))

    res = RESOLUTIONS[state["resolution_idx"]]
    cv.putText(img, f"Res: {res[0]}x{res[1]}", (px1 + 15, 107),
               cv.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    draw_button(img, btns["res_dn"], "-", (80, 80, 80))
    draw_button(img, btns["res_up"], "+", (80, 80, 80))

    draw_button(img, btns["trail"], "TRAIL", (0, 120, 0))


def draw_status_bar(img):
    w, _ = get_figsize()

    if state["recording"]:
        cv.circle(img, (w - 20, 20), 8, (0, 0, 255), -1)
        cv.putText(img, "REC", (w - 55, 25),
                   cv.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    if state["paused"]:
        cv.putText(img, "|| PAUSED", (w // 2 - 40, 25),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)

    if state["speed"] != 1.0:
        cv.putText(img, f"{state['speed']}x", (10, 25),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 200), 1)
