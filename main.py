import cv2 as cv
from controls import state, FIGSIZE, RESOLUTIONS, SPEEDS, on_mouse, handle_key
from ui import draw_status_bar, draw_control_bar, draw_settings_panel
from recorder import Recorder

VIDEO_URL = "rtsp://210.99.70.120:1935/live/cctv001.stream"


def main():
    video = cv.VideoCapture(VIDEO_URL)

    if not video.isOpened():
        print("Failed to open video source")
        return

    fps = video.get(cv.CAP_PROP_FPS)
    if fps <= 0 or fps > 120:
        fps = 30.0

    recorder = Recorder(fps)

    cv.namedWindow("Video Player")
    cv.setMouseCallback("Video Player", on_mouse)

    while True:
        # 일시정지 처리
        if state["paused"]:
            key = cv.waitKey(30)
            if key == 27:
                break
            handle_key(key)
            continue

        # 빨리감기: 속도에 따라 프레임 스킵
        skip = max(1, int(state["speed"])) - 1
        for _ in range(skip):
            video.read()

        valid, img = video.read()
        if not valid:
            break

        # 해상도 적용
        cur_res = RESOLUTIONS[state["resolution_idx"]]
        img = cv.resize(img, cur_res)
        img = cv.resize(img, FIGSIZE)

        # 녹화 & 스크린샷 (UI 그리기 전)
        recorder.update(img)
        recorder.take_screenshot(img)

        # UI 그리기
        draw_status_bar(img)
        draw_control_bar(img)
        draw_settings_panel(img)

        cv.imshow("Video Player", img)

        # 속도에 따른 대기 시간
        wait = max(1, int((1 / fps * 1000) / state["speed"]))
        key = cv.waitKey(wait)

        if key == 27:
            break
        handle_key(key)

    recorder.release()
    video.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
