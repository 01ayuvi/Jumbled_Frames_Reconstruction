<<<<<<< HEAD
# Jumbled Frames Reconstruction Challenge

**Author:** Ayuvi Chaudhary  
**Objective:** Reconstruct the correct order of a 10-second 1080p video (30 fps, ≈ 300 frames).  
**Task:** Analyze and reorder shuffled frames to produce a smooth, original-sequence video.

---

## 📂 Files
- `main.py` – main reconstruction script  
- `requirements.txt` – dependencies  
- `time_log.txt` – execution-time record  
- Output video: `unjumbled_video.mp4`

---

## ⚙️ Running the Code
```bash
pip install -r requirements.txt
python main.py
=======
# Jumbled Frames Reconstruction Challenge

**Author:** Ayuvi Chaudhary  
**Objective:** Reconstruct the correct order of a 10-second 1080p video (30 fps, ≈ 300 frames).  
**Task:** Analyze and reorder shuffled frames to produce a smooth, original-sequence video.

---

## 📂 Files
- `main.py` – main reconstruction script  
- `requirements.txt` – dependencies  
- `time_log.txt` – execution-time record  
- Output video: `unjumbled_video.mp4`

---

## ⚙️ Running the Code
```bash
pip install -r requirements.txt
python main.py
>>>>>>> 09d3a3353011426c8d98954521543a1cc9bdc4c1

Goal:
Speed up the reconstruction process while maintaining visual accuracy.

Key Improvements:

Introduced ULTRA FAST MODE using color histograms instead of SSIM.

Added configuration parameters:

FRAME_RESIZE_SCALE = 0.5 → reduces frame size by 50% for faster comparison.

NEIGHBOR_LIMIT = 30 → limits the number of frames compared per step.

Reconstruction now runs ~10× faster than the previous version.

Added time logging for performance tracking.

Result:
The video reconstructs in seconds instead of minutes, while keeping frame order visually consistent.
Some flickering in the first few seconds may still occur — next step will target Smart Matching Refinement to reduce that.
