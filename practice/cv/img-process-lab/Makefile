.PHONY: install demo basics cam cam-record face face-cam tracking filter filter-blur filter-sobel filter-canny histogram in-range cloak interpolation qr qr-cam scan measure grader landmarks blinks threshold gesture teachable

IMG ?= sample/lena.jpg

install:
	pip install -r requirements.txt

# 靜態圖全跑（不需攝影機），依序按任意鍵換下一個
demo:
	python basics/basics.py      --source sample/lena.jpg    --mode all
	python basics/threshold.py   --source sample/lena.jpg    --mode all --gray
	python basics/interpolation.py --source sample/lena.jpg  --mode all
	python basics/histogram.py   --source sample/dim.jpg     --mode all
	python filter/filter.py      --source sample/lena.jpg    --mode blur
	python filter/filter.py      --source sample/lena.jpg    --mode filter2d --kernel edge
	python filter/filter.py      --source sample/gear.png    --mode sobel
	python filter/filter.py      --source sample/lena.jpg    --mode canny
	python color/in_range.py     --source sample/T04-A.jpg   --mode mask
	python detection/face_detect.py --source sample/jp.png
	python detection/landmarks.py   --source sample/jp.png   --mode landmarks
	python detection/qr.py          --source sample/qr.png
	python application/measure.py   --source sample/tetris_blocks.png --width 1.0
	python application/grader.py    --source sample/test.png

# ── 基礎影像操作 ──────────────────────────────────────────────────────────────
basics:
	python basics/basics.py --source $(IMG) --mode all

threshold:
	python basics/threshold.py --source $(IMG) --mode all --gray

interpolation:
	python basics/interpolation.py --source $(IMG) --mode all

histogram:
	python basics/histogram.py --source $(IMG) --mode all

# ── 濾波 ─────────────────────────────────────────────────────────────────────
filter:
	python filter/filter.py --source $(IMG) --mode all

filter-blur:
	python filter/filter.py --source $(IMG) --mode blur

filter-sobel:
	python filter/filter.py --source $(IMG) --mode sobel

filter-canny:
	python filter/filter.py --source $(IMG) --mode canny

# ── 色彩 ─────────────────────────────────────────────────────────────────────
in-range:
	python color/in_range.py --source $(IMG) --mode mask

cloak:
	python color/in_range.py --mode cloak

tracking:
	python color/tracking.py --color green

# ── 偵測 / 辨識 ───────────────────────────────────────────────────────────────
# 首次執行自動下載 caffemodel (~10MB)
face:
	python detection/face_detect.py --source $(IMG)

face-cam:
	python detection/face_detect.py --source 0

landmarks:
	python detection/landmarks.py --source $(IMG) --mode landmarks

blinks:
	python detection/landmarks.py --source 0 --mode blinks

gesture:
	python detection/gesture.py

qr:
	python detection/qr.py --source sample/qr.png

qr-cam:
	python detection/qr.py --source 0

# 需先準備 keras_Model.h5 和 labels.txt
teachable:
	@[ "$(MODEL)" ] || { echo "Usage: make teachable MODEL=<path> LABELS=<path>"; exit 1; }
	python detection/teachable.py --model $(MODEL) --labels $(LABELS) --flip

# ── 應用 ─────────────────────────────────────────────────────────────────────
cam:
	python application/cam.py --mode preview

cam-record:
	python application/cam.py --mode record -o output.mp4

# 範例：make scan IMG=<doc-photo.jpg>
scan:
	python application/scan.py --source $(IMG) --mode scan

# 範例：make measure IMG=<photo.jpg> WIDTH=0.955
measure:
	@[ "$(WIDTH)" ] || { echo "Usage: make measure IMG=<path> WIDTH=<inches>"; exit 1; }
	python application/measure.py --source $(IMG) --width $(WIDTH)

grader:
	python application/grader.py --source sample/test.png
