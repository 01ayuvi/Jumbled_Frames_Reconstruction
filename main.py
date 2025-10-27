"""
Jumbled Frames Reconstruction - Final Code
Author: Ayuvi Chaudhary
Challenge: TECDIA Internship Task
Description: Reconstructs the original sequence of a 10-sec, 30 fps jumbled video (≈300 frames).
"""

import cv2
import numpy as np
import glob
import os
import time

# ========== CONFIGURATION ==========
INPUT_VIDEO = "jumbled_video.mp4"
OUTPUT_VIDEO = "unjumbled_video.mp4"
FPS = 30  # updated spec

# ========== STEP 1: Extract Frames ==========
os.makedirs("frames", exist_ok=True)
cap = cv2.VideoCapture(INPUT_VIDEO)
frame_count = 0

print("[INFO] Extracting frames...")
while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imwrite(f"frames/frame_{frame_count:03d}.jpg", frame)
    frame_count += 1

cap.release()
print(f"[INFO] Extracted {frame_count} frames.\n")

# ========== STEP 2: Define Frame Similarity ==========
def frame_similarity(frame1, frame2):
    """Compare two frames using color histogram correlation."""
    hist1 = cv2.calcHist([frame1], [0, 1, 2], None, [8,8,8], [0,256,0,256,0,256])
    hist2 = cv2.calcHist([frame2], [0, 1, 2], None, [8,8,8], [0,256,0,256,0,256])
    cv2.normalize(hist1, hist1)
    cv2.normalize(hist2, hist2)
    return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

# ========== STEP 3: Reconstruct Order ==========
print("[INFO] Reconstructing frame order...")
start_time = time.time()

frame_files = sorted(glob.glob("frames/*.jpg"))
frames = [cv2.imread(f) for f in frame_files]
n = len(frames)
used, order = set(), []

current = 0  # starting frame
order.append(current)
used.add(current)

for _ in range(n - 1):
    best_match, best_score = -1, -1
    for i in range(n):
        if i in used:
            continue
        score = frame_similarity(frames[current], frames[i])
        if score > best_score:
            best_score, best_match = score, i
    order.append(best_match)
    used.add(best_match)
    current = best_match

end_time = time.time()
execution_time = end_time - start_time
print(f"[INFO] Reconstruction complete in {execution_time:.2f} s.\n")

with open("time_log.txt", "w") as f:
    f.write(f"Execution Time: {execution_time:.2f} seconds\n")

# ========== STEP 4: Export Reconstructed Video ==========
print("[INFO] Saving reconstructed video...")
height, width, _ = frames[0].shape
out = cv2.VideoWriter(OUTPUT_VIDEO, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (width, height))

for idx in order:
    out.write(frames[idx])

out.release()
print(f"[DONE] Saved '{OUTPUT_VIDEO}'. Time log written to 'time_log.txt'.")
