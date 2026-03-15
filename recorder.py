import cv2 as cv
import datetime
import os
from controls import OUTPUT_DIR, get_figsize, state


def get_output_path():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(OUTPUT_DIR, f"rec_{ts}.mp4")


def get_snap_path():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(OUTPUT_DIR, f"snap_{ts}.png")


class Recorder:
    def __init__(self, fps):
        self.fourcc = cv.VideoWriter_fourcc(*"mp4v")
        self.fps = fps
        self.writer = None
        self.output_path = None
        self.prev_recording = False

    def update(self, frame):
        if state["recording"] and not self.prev_recording:
            self.output_path = get_output_path()
            figsize = get_figsize()
            self.writer = cv.VideoWriter(self.output_path, self.fourcc, self.fps, figsize)
            print(f"Recording started -> {self.output_path}")
        elif not state["recording"] and self.prev_recording:
            self.writer.release()
            self.writer = None
            print(f"Recording stopped, saved to {self.output_path}")
        self.prev_recording = state["recording"]

        if state["recording"] and self.writer is not None:
            self.writer.write(frame)

    def take_screenshot(self, frame):
        if state["screenshot"]:
            snap_path = get_snap_path()
            cv.imwrite(snap_path, frame)
            print(f"Screenshot saved: {snap_path}")
            state["screenshot"] = False

    def release(self):
        if self.writer is not None:
            self.writer.release()
