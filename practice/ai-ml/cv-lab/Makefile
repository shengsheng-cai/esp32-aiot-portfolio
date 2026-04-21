.PHONY: install smoke transfer transfer-efficientnet transfer-quick vae vae-denoise style dream cartoonize cartoonize-style

install:
	pip install -r requirements.txt

# 從零開始：安裝套件 + 跑所有模組驗證
dev:
	$(MAKE) install
	$(MAKE) smoke

# ── Smoke Test ───────────────────────────────────────────────────────────────
# 一鍵驗證所有模組（cartoonize 除外，animeganv2 套件問題）
# 時間：CPU ~30 分鐘
smoke:
	$(MAKE) transfer-quick
	$(MAKE) vae-denoise
	python style/style.py dream --img sample/content.jpg --steps 50 --step-size 0.05 --max-loss 5000
	python style/style.py style --content sample/content.jpg --style sample/style.jpg --style-weight 1e4 --device cpu

# ── Transfer Learning ────────────────────────────────────────────────────────
# 資料：CIFAR-10（自動下載，約 170MB）
# 時間：CPU 全量 ~2 小時；GPU ~10 分鐘
# 產出：resnet50_cifar10.pth（repo 根目錄）
# ⚠️ 第一次建議先跑 transfer-quick 驗證程式能動
transfer:
	python transfer/train.py --model resnet50

transfer-efficientnet:
	python transfer/train.py --model efficientnet

# 快速驗證：5000 張樣本 × 2 epoch，CPU ~10 分鐘，val_acc ~80%
transfer-quick:
	python transfer/train.py --model resnet50 --subset 5000 --epochs-extract 2 --epochs-finetune 2

# ── VAE ──────────────────────────────────────────────────────────────────────
# 資料：MNIST（自動下載，約 11MB）
# 時間：CPU ~10 分鐘
# 產出：vae.pth, latent_space.png, label_clusters.png
vae:
	python vae/vae.py --mode vae --epochs 30

# 產出：denoise_ae.pth, denoise_result.png
vae-denoise:
	python vae/vae.py --mode denoise --epochs 30

# ── Style Transfer / Deep Dream ──────────────────────────────────────────────
# 需自備圖片。時間：CPU 幾分鐘。產出：result_style.png（repo 根目錄）
# 範例：make style CONTENT=photo.jpg STYLE_IMG=starry_night.jpg
style:
	@[ "$(CONTENT)" ] && [ "$(STYLE_IMG)" ] || { echo "Usage: make style CONTENT=<path> STYLE_IMG=<path>"; exit 1; }
	python style/style.py style --content $(CONTENT) --style $(STYLE_IMG) $(EXTRA)

# 需自備圖片。產出：result_dream.png
# 範例：make dream IMG=photo.jpg
dream:
	@[ "$(IMG)" ] || { echo "Usage: make dream IMG=<path>"; exit 1; }
	python style/style.py dream --img $(IMG)

# ── Cartoonize ───────────────────────────────────────────────────────────────
# ⚠️ 需額外安裝 animeganv2（PyPI 沒有，需從 GitHub 安裝，目前未驗證）
# 輸入：cartoonize/input_images/*.jpg
# 產出：cartoonize/output_images/<style>/*
cartoonize:
	python cartoonize/cartoonize.py --input-dir cartoonize/input_images --all-styles

# 範例：make cartoonize-style STYLE=Hayao
cartoonize-style:
	@[ "$(STYLE)" ] || { echo "Usage: make cartoonize-style STYLE=Hayao"; exit 1; }
	python cartoonize/cartoonize.py --input-dir cartoonize/input_images --styles $(STYLE)
