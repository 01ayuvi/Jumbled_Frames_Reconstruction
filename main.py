"""
Jumbled Frames Reconstruction - ULTRA FAST MODE
Author: Ayuvi Chaudhary
Description: Uses color histograms instead of SSIM for ~10x faster reconstruction.
"""

import cv2
import numpy as np
import glob
import os
import time

# ========== CONFIGURATION ==========
INPUT_VIDEO = "jumbled_video.mp4"
OUTPUT_VIDEO = "unjumbled_video.mp4"
FPS = 30
FRAME_RESIZE_SCALE = 0.5  # reduce size for speed
NEIGHBOR_LIMIT = 30       # limit comparisons

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

# ========== STEP 2: Load and Resize Frames ==========
frame_files = sorted(glob.glob("frames/*.jpg"))
frames = []
for f in frame_files:
    img = cv2.imread(f)
    h, w = img.shape[:2]
    img_small = cv2.resize(img, (int(w * FRAME_RESIZE_SCALE), int(h * FRAME_RESIZE_SCALE)))
    frames.append(img_small)
n = len(frames)

# ========== STEP 3: Define Fast Histogram Similarity ==========
def frame_similarity(f1, f2):
    hist1 = cv2.calcHist([f1], [0, 1, 2], None, [8,8,8], [0,256,0,256,0,256])
    hist2 = cv2.calcHist([f2], [0, 1, 2], None, [8,8,8], [0,256,0,256,0,256])
    cv2.normalize(hist1, hist1)
    cv2.normalize(hist2, hist2)
    return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

# ========== STEP 4: Reconstruct Order ==========
print("[INFO] Reconstructing frame order (ULTRA FAST MODE)...")
start_time = time.time()

used = set()
order = [0]
used.add(0)

for _ in range(n - 1):
    current = order[-1]
    best_match, best_score = -1, -1

    candidates = [i for i in range(n) if i not in used]
    if len(candidates) > NEIGHBOR_LIMIT:
        candidates = np.random.choice(candidates, NEIGHBOR_LIMIT, replace=False)

    for i in candidates:
        score = frame_similarity(frames[current], frames[i])
        if score > best_score:
            best_score, best_match = score, i

    order.append(best_match)
    used.add(best_match)

end_time = time.time()
execution_time = end_time - start_time
print(f"[INFO] Reconstruction complete in {execution_time:.2f} s.\n")

with open("time_log.txt", "w") as f:
    f.write(f"Execution Time: {execution_time:.2f} seconds\n")

# ========== STEP 5: Save Output ==========
print("[INFO] Saving reconstructed video...")
first_full = cv2.imread(frame_files[0])
height, width, _ = first_full.shape
out = cv2.VideoWriter(OUTPUT_VIDEO, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (width, height))

for idx in order:
    full_frame = cv2.imread(frame_files[idx])
    out.write(full_frame)

out.release()
print(f"[DONE] Saved '{OUTPUT_VIDEO}'. Time log written to 'time_log.txt'.")
