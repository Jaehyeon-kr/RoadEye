import cv2 as cv
import numpy as np
import os
import glob
from controls import OUTPUT_DIR, get_figsize


def get_latest_video():
    """records 폴더에서 가장 최근 녹화 파일 찾기"""
    pattern = os.path.join(OUTPUT_DIR, "rec_*.mp4")
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def generate_trail(video_path, out_duration=10):
    """
    영상 전체에서 차량 움직임을 추출하고,
    out_duration초짜리 영상으로 압축하여 모든 차량을 한꺼번에 보여준다.

    1단계: 전체 영상 읽으면서 배경 학습 + 전경(차량) 마스크 저장
    2단계: 전체 프레임의 차량들을 out_duration초 분량으로 재배치하여 합성
    """
    cap = cv.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Failed to open: {video_path}")
        return None

    fps = cap.get(cv.CAP_PROP_FPS)
    if fps <= 0 or fps > 120:
        fps = 30.0
    src_total = int(cap.get(cv.CAP_PROP_FRAME_COUNT))

    if src_total < 2:
        print("Not enough frames")
        cap.release()
        return None

    # === 1단계: 전체 영상 읽기 + 배경 학습 ===
    print(f"Reading {src_total} frames & learning background...")
    bg_sub = cv.createBackgroundSubtractorMOG2(
        history=500, varThreshold=50, detectShadows=True
    )
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))

    foregrounds = []  # (frame, mask) 튜플 리스트

    figsize = get_figsize()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv.resize(frame, figsize)
        fg_mask = bg_sub.apply(frame)
        # 그림자 제거
        fg_mask[fg_mask == 127] = 0
        # 노이즈 제거
        fg_mask = cv.morphologyEx(fg_mask, cv.MORPH_OPEN, kernel)
        fg_mask = cv.morphologyEx(fg_mask, cv.MORPH_CLOSE, kernel)

        # 작은 물체 무시
        contours, _ = cv.findContours(fg_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        clean_mask = np.zeros_like(fg_mask)
        for cnt in contours:
            if cv.contourArea(cnt) > 500:
                cv.drawContours(clean_mask, [cnt], -1, 255, -1)

        foregrounds.append((frame, clean_mask))

    cap.release()

    if len(foregrounds) < 2:
        print("Not enough frames")
        return None

    # 배경 이미지
    background = bg_sub.getBackgroundImage()
    if background is None:
        background = foregrounds[0][0].copy()
    background = cv.resize(background, figsize)

    w, h = figsize

    # === 2단계: out_duration초 영상으로 압축 합성 ===
    out_fps = fps
    out_total = int(out_duration * out_fps)
    src_count = len(foregrounds)

    # 원본 프레임을 출력 프레임에 매핑
    # 한 출력 프레임에 여러 원본 프레임의 차량이 겹침
    frames_per_out = max(1, src_count / out_total)

    fourcc = cv.VideoWriter_fourcc(*"mp4v")
    base = os.path.splitext(os.path.basename(video_path))[0]
    out_path = os.path.join(OUTPUT_DIR, f"trail_{base}.mp4")
    writer = cv.VideoWriter(out_path, fourcc, out_fps, (w, h))

    # 스냅샷 이미지도 생성 (전체 차량 한 장)
    all_in_one = background.copy()

    print(f"Compositing into {out_total} frames ({out_duration}s)...")
    for i in range(out_total):
        # 이 출력 프레임에 합성할 원본 프레임 범위
        src_start = int(i * frames_per_out)
        src_end = int((i + 1) * frames_per_out)
        src_end = min(src_end, src_count)

        composed = background.copy()

        for j in range(src_start, src_end):
            frame, mask = foregrounds[j]
            # 차량(전경)을 배경 위에 합성
            fg = cv.bitwise_and(frame, frame, mask=mask)
            bg_part = cv.bitwise_and(composed, composed, mask=cv.bitwise_not(mask))
            composed = cv.add(bg_part, fg)

        # 전체 합성 이미지에도 누적
        for j in range(src_start, src_end):
            frame, mask = foregrounds[j]
            fg = cv.bitwise_and(frame, frame, mask=mask)
            bg_part = cv.bitwise_and(all_in_one, all_in_one, mask=cv.bitwise_not(mask))
            all_in_one = cv.add(bg_part, fg)

        writer.write(composed)

    writer.release()
    print(f"Trail video saved: {out_path}")

    # 전체 합성 스냅샷 저장
    snap_path = os.path.join(OUTPUT_DIR, f"trail_{base}.png")
    cv.imwrite(snap_path, all_in_one)
    print(f"Trail snapshot saved: {snap_path}")

    return out_path, snap_path


def show_trail(video_path=None, out_duration=10):
    """Trail 영상 생성 후 재생"""
    if video_path is None:
        video_path = get_latest_video()
        if video_path is None:
            print("No recorded video found in records/")
            return

    print(f"Processing: {video_path}")
    result = generate_trail(video_path, out_duration)

    if result is None:
        return

    out_video, snap_path = result

    # 생성된 영상 재생
    cap = cv.VideoCapture(out_video)
    fps = cap.get(cv.CAP_PROP_FPS)

    print("Playing trail video... (press any key to close)")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            # 루프 재생
            cap.set(cv.CAP_PROP_POS_FRAMES, 0)
            continue
        cv.imshow("Vehicle Trail", frame)
        if cv.waitKey(int(1000 / fps)) != -1:
            break

    cap.release()
    cv.destroyWindow("Vehicle Trail")


if __name__ == "__main__":
    show_trail()
