.PHONY: install demo basics cam cam-record face face-cam tracking filter filter-blur filter-sobel filter-canny histogram in-range cloak interpolation qr qr-cam scan measure grader landmarks blinks threshold gesture teachable

PYTHON ?= python3
IMG    ?= sample/lena.jpg

install:
	pip install -r requirements.txt

# 靜態圖全跑（不需攝影機），依序按任意鍵換下一個
demo:
	$(PYTHON) basics/basics.py      --source sample/lena.jpg    --mode all
	$(PYTHON) basics/threshold.py   --source sample/lena.jpg    --mode all --gray
	$(PYTHON) basics/interpolation.py --source sample/lena.jpg  --mode all
	$(PYTHON) basics/histogram.py   --source sample/dim.jpg     --mode all
	$(PYTHON) filter/filter.py      --source sample/lena.jpg    --mode blur
	$(PYTHON) filter/filter.py      --source sample/lena.jpg    --mode filter2d --kernel edge
	$(PYTHON) filter/filter.py      --source sample/gear.png    --mode sobel
	$(PYTHON) filter/filter.py      --source sample/lena.jpg    --mode canny
	$(PYTHON) color/in_range.py     --source sample/T04-A.jpg   --mode mask
	$(PYTHON) detection/face_detect.py --source sample/jp.png
	$(PYTHON) detection/landmarks.py   --source sample/jp.png   --mode landmarks
	$(PYTHON) detection/qr.py          --source sample/qr.png
	$(PYTHON) application/measure.py   --source sample/tetris_blocks.png --width 1.0
	$(PYTHON) application/grader.py    --source sample/test.png

# ── 基礎影像操作 ──────────────────────────────────────────────────────────────
basics:
	$(PYTHON) basics/basics.py --source $(IMG) --mode all

threshold:
	$(PYTHON) basics/threshold.py --source $(IMG) --mode all --gray

interpolation:
	$(PYTHON) basics/interpolation.py --source $(IMG) --mode all

histogram:
	$(PYTHON) basics/histogram.py --source $(IMG) --mode all

# ── 濾波 ─────────────────────────────────────────────────────────────────────
filter:
	$(PYTHON) filter/filter.py --source $(IMG) --mode all

filter-blur:
	$(PYTHON) filter/filter.py --source $(IMG) --mode blur

filter-sobel:
	$(PYTHON) filter/filter.py --source $(IMG) --mode sobel

filter-canny:
	$(PYTHON) filter/filter.py --source $(IMG) --mode canny

# ── 色彩 ─────────────────────────────────────────────────────────────────────
in-range:
	$(PYTHON) color/in_range.py --source $(IMG) --mode mask

cloak:
	$(PYTHON) color/in_range.py --mode cloak

tracking:
	$(PYTHON) color/tracking.py --color green

# ── 偵測 / 辨識 ───────────────────────────────────────────────────────────────
# 首次執行自動下載 caffemodel (~10MB)
face:
	$(PYTHON) detection/face_detect.py --source $(IMG)

face-cam:
	$(PYTHON) detection/face_detect.py --source 0

landmarks:
	$(PYTHON) detection/landmarks.py --source $(IMG) --mode landmarks

blinks:
	$(PYTHON) detection/landmarks.py --source 0 --mode blinks

gesture:
	$(PYTHON) detection/gesture.py

qr:
	$(PYTHON) detection/qr.py --source sample/qr.png

qr-cam:
	$(PYTHON) detection/qr.py --source 0

# 需先準備 keras_Model.h5 和 labels.txt
teachable:
	@[ "$(MODEL)" ] || { echo "Usage: make teachable MODEL=<path> LABELS=<path>"; exit 1; }
	$(PYTHON) detection/teachable.py --model $(MODEL) --labels $(LABELS) --flip

# ── 應用 ─────────────────────────────────────────────────────────────────────
cam:
	$(PYTHON) application/cam.py --mode preview

cam-record:
	$(PYTHON) application/cam.py --mode record -o output.mp4

# 範例：make scan IMG=<doc-photo.jpg>
scan:
	$(PYTHON) application/scan.py --source $(IMG) --mode scan

# 範例：make measure IMG=<photo.jpg> WIDTH=0.955
measure:
	@[ "$(WIDTH)" ] || { echo "Usage: make measure IMG=<path> WIDTH=<inches>"; exit 1; }
	$(PYTHON) application/measure.py --source $(IMG) --width $(WIDTH)

grader:
	$(PYTHON) application/grader.py --source sample/test.png
