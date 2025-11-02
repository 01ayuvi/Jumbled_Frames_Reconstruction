"""
Jumbled Frames Reconstruction - SMOOTH MOTION BLENDED MODE (Final Version)
Author: Ayuvi Chaudhary
Description:
Reconstructs a jumbled 10-second, 30 fps video using hybrid similarity (SSIM + Histogram)
and motion-aware ordering. Adds temporal blending to reduce flicker and maintain smooth motion.
"""

import cv2
import numpy as np
import os
import time
from skimage.metrics import structural_similarity as ssim

cv2.setNumThreads(8)

# ========== SETTINGS ==========
INPUT_VIDEO = "jumbled_video.mp4"
OUTPUT_VIDEO = "unjumbled_video.mp4"
FRAME_RESIZE_SCALE = 0.3     # Downscale for faster similarity computation
NEIGHBOR_LIMIT = 25          # Limit number of frames compared per iteration
MOTION_WINDOW = 5            # How many past motions to smooth
BLEND_ALPHA = 0.6            # Strength of temporal blending (0–1)
FPS = 30                     # Required frame rate
DURATION = 10                # Target duration in seconds (≈300 frames)

# ========== STEP 1: Extract Frames ==========
os.makedirs("frames", exist_ok=True)
cap = cv2.VideoCapture(INPUT_VIDEO)
input_fps = int(cap.get(cv2.CAP_PROP_FPS)) or FPS
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
size = (width, height)

frames_full = []
frame_count = 0
print("[INFO] Extracting frames...")
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frames_full.append(frame)
    cv2.imwrite(f"frames/frame_{frame_count:03d}.jpg", frame)
    frame_count += 1
cap.release()
print(f"[INFO] Extracted {frame_count} frames.\n")

# ========== STEP 2: Prepare Resized Frames ==========
frames_small = []
for img in frames_full:
    h, w = img.shape[:2]
    img_small = cv2.resize(img, (int(w * FRAME_RESIZE_SCALE), int(h * FRAME_RESIZE_SCALE)))
    frames_small.append(img_small)
n = len(frames_small)

# ========== STEP 3: Similarity & Motion Functions ==========
def frame_similarity(f1, f2):
    """Hybrid similarity between two frames: histogram + SSIM."""
    gray1 = cv2.cvtColor(f1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY)
    try:
        ssim_score, _ = ssim(gray1, gray2, full=True)
    except Exception:
        ssim_score = 0

    hist1 = cv2.calcHist([f1], [0, 1, 2], None, [8, 8, 8], [0,256,0,256,0,256])
    hist2 = cv2.calcHist([f2], [0, 1, 2], None, [8, 8, 8], [0,256,0,256,0,256])
    cv2.normalize(hist1, hist1)
    cv2.normalize(hist2, hist2)
    hist_score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

    return 0.7 * hist_score + 0.3 * ssim_score


def motion_direction(prev, nextf):
    """Estimate average horizontal motion using optical flow."""
    p = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    n = cv2.cvtColor(nextf, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(p, n, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    return np.mean(flow[..., 0])  # positive = right, negative = left


# ========== STEP 4: Detect Best Start Frame ==========
print("[INFO] Detecting stable start frame...")
best_start, best_avg = 0, -1
for i in range(0, min(80, n), 5):
    total = 0
    for j in range(i + 1, min(i + 6, n)):
        total += frame_similarity(frames_small[i], frames_small[j])
    avg = total / 5
    if avg > best_avg:
        best_avg, best_start = avg, i
print(f"[INFO] Starting reconstruction from frame #{best_start}\n")

# ========== STEP 5: Reconstruct Frame Order ==========
print("[INFO] Reconstructing order (Hybrid + Motion + Blending Mode)...")
start_time = time.time()
used = {best_start}
order = [best_start]
motion_window = []
similarity_log = []

for _ in range(n - 1):
    cur = order[-1]
    best_match, best_score = -1, -1
    candidates = [i for i in range(n) if i not in used]
    if len(candidates) > NEIGHBOR_LIMIT:
        candidates = np.random.choice(candidates, NEIGHBOR_LIMIT, replace=False)
    for i in candidates:
        score = frame_similarity(frames_small[cur], frames_small[i])
        motion = motion_direction(frames_small[cur], frames_small[i])
        motion_window.append(motion)
        if len(motion_window) > MOTION_WINDOW:
            motion_window.pop(0)
        # Penalize direction reversals
        if len(motion_window) >= 3 and np.sign(np.sum(motion_window)) < 0:
            score *= 0.8
        if score > best_score:
            best_score, best_match = score, i
    similarity_log.append(best_score)
    order.append(best_match)
    used.add(best_match)
    if len(order) % 50 == 0:
        print(f"[DEBUG] {len(order)} / {n} frames processed")

execution_time = time.time() - start_time
avg_similarity = np.mean(similarity_log)
print(f"[INFO] Reconstruction complete in {execution_time:.2f}s")
print(f"[INFO] Average Similarity Score: {avg_similarity*100:.2f}%\n")

# ========== STEP 6: Temporal Blending & Save ==========
print("[INFO] Saving blended smooth video...")
out = cv2.VideoWriter(OUTPUT_VIDEO, cv2.VideoWriter_fourcc(*'mp4v'), FPS, size)

previous_frame = None
for idx in order:
    current_frame = frames_full[idx]

    # Blend with previous frame slightly for motion smoothness
    if previous_frame is not None:
        current_frame = cv2.addWeighted(previous_frame, BLEND_ALPHA, current_frame, 1 - BLEND_ALPHA, 0)

    out.write(current_frame)
    previous_frame = current_frame

out.release()


# ========== STEP 7: Logs ==========
with open("time_log.txt", "w") as f:
    f.write(f"Execution Time: {execution_time:.2f}s\n")
    f.write(f"Average Similarity: {avg_similarity*100:.2f}%\n")

print("\n===== SUMMARY =====")
print(f"Frames: {len(order)} | FPS: {FPS}")
print(f"Output Duration: {len(order)/FPS:.2f}s")
print(f"Execution Time: {execution_time:.2f}s")
print(f"Average Similarity: {avg_similarity*100:.2f}%")
print("[DONE] Saved 'unjumbled_video.mp4' successfully.\n")
