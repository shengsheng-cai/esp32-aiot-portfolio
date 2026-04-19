import io
import os
from pathlib import Path

import numpy as np
import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel
from torchvision import transforms
from transformers import ViTConfig, ViTForImageClassification, ViTImageProcessor, pipeline

from models import SimpleCNN, SimpleNN, ViT_MNIST
from preprocessing import preprocess


app = FastAPI(title="MNIST Multi-Model Inference API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_DIR = Path(os.environ.get("MODEL_DIR", "../models"))

loaded_models: dict = {}
vit_processor: ViTImageProcessor | None = None

to_tensor = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,)),
])


@app.on_event("startup")
async def load_models():
    global loaded_models, vit_processor

    # 自建模型（SimpleNN / SimpleCNN / ViT_MNIST）
    custom_configs = [
        ("simple_nn_mnist.pth", "SimpleNN", SimpleNN),
        ("simple_cnn_mnist.pth", "SimpleCNN", SimpleCNN),
        ("myvit_mnist.pth", "ViT_Custom", ViT_MNIST),
    ]
    for fname, name, cls in custom_configs:
        path = MODEL_DIR / fname
        if path.exists():
            model = cls().to(device)
            model.load_state_dict(torch.load(path, map_location=device))
            model.eval()
            loaded_models[name] = {"type": "mnist", "model": model}
            print(f"Loaded: {name}")

    # HF ViT fine-tuned on MNIST（我們自己訓練的）
    hf_pth_configs = [
        ("myvit_mnist_hf_4060.pth", "ViT_HF_4060"),
        ("myvit_mnist_hf_best_tuned.pth", "ViT_HF_BestTuned"),
    ]
    hf_pth_exist = [(fname, name) for fname, name in hf_pth_configs if (MODEL_DIR / fname).exists()]
    if hf_pth_exist:
        try:
            vit_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
            hf_config = ViTConfig.from_pretrained("google/vit-base-patch16-224", num_labels=10)
        except Exception as e:
            print(f"Failed loading HF config: {e}")
            hf_config = None

        for fname, name in hf_pth_exist:
            if hf_config is None:
                break
            try:
                model = ViTForImageClassification(hf_config).to(device)
                model.load_state_dict(torch.load(MODEL_DIR / fname, map_location=device))
                model.eval()
                loaded_models[name] = {"type": "hf_vit", "model": model, "processor": vit_processor}
                print(f"Loaded: {name}")
            except Exception as e:
                print(f"Failed loading {name}: {e}")

    # HF ViT pretrained on ImageNet（不認識數字，做對比用）
    try:
        pipe = pipeline(
            "image-classification",
            model="google/vit-base-patch16-224",
            device=0 if torch.cuda.is_available() else -1,
        )
        loaded_models["ViT_ImageNet"] = {"type": "pipeline", "model": pipe}
        print("Loaded: ViT_ImageNet")
    except Exception as e:
        print(f"Failed loading ViT_ImageNet: {e}")

    # HF ViT 第三方已訓練好的 MNIST 模型
    try:
        proc = ViTImageProcessor.from_pretrained("farleyknight-org-username/vit-base-mnist")
        model = ViTForImageClassification.from_pretrained(
            "farleyknight-org-username/vit-base-mnist"
        ).to(device)
        model.eval()
        loaded_models["ViT_3rd_MNIST"] = {"type": "hf_vit", "model": model, "processor": proc}
        print("Loaded: ViT_3rd_MNIST")
    except Exception as e:
        print(f"Failed loading ViT_3rd_MNIST: {e}")

    print(f"Total: {len(loaded_models)} models loaded")


class PredictionResult(BaseModel):
    prediction: int
    confidence: float
    probabilities: list[float]


class InferenceResponse(BaseModel):
    success: bool
    results: dict[str, PredictionResult]
    best_model: str
    best_prediction: int


@app.get("/")
async def root():
    return {"message": "MNIST Multi-Model Inference API", "models": list(loaded_models.keys())}


@app.get("/health")
async def health():
    return {"status": "healthy", "device": str(device), "models_count": len(loaded_models)}


@app.get("/models")
async def list_models():
    return {"models": list(loaded_models.keys())}


@app.post("/predict", response_model=InferenceResponse)
async def predict(file: UploadFile = File(...)):
    if not loaded_models:
        raise HTTPException(status_code=503, detail="No models loaded")

    try:
        pil_img = Image.open(io.BytesIO(await file.read())).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}")

    processed = preprocess(pil_img)
    t28 = to_tensor(processed).unsqueeze(0).to(device)

    results = {}
    best_conf, best_model, best_pred = 0.0, "", -1

    with torch.no_grad():
        for name, info in loaded_models.items():
            if info["type"] == "mnist":
                logits = info["model"](t28)
                probs = torch.softmax(logits, dim=1)[0].cpu().numpy()

            elif info["type"] == "pipeline":
                pipe_results = info["model"](pil_img, top_k=10)
                probs = np.zeros(10)
                for r in pipe_results:
                    label = r["label"]
                    try:
                        idx = int(label.split("_")[-1]) if "_" in label else int(label)
                        if 0 <= idx < 10:
                            probs[idx] = r["score"]
                    except ValueError:
                        pass

            else:  # hf_vit
                inputs = info["processor"](images=pil_img, return_tensors="pt")
                inputs = {k: v.to(device) for k, v in inputs.items()}
                outputs = info["model"](**inputs)
                probs = torch.softmax(outputs.logits, dim=1)[0].cpu().numpy()

            pred = int(np.argmax(probs))
            conf = float(np.max(probs))

            results[name] = PredictionResult(
                prediction=pred,
                confidence=conf,
                probabilities=probs.tolist(),
            )

            if conf > best_conf:
                best_conf, best_model, best_pred = conf, name, pred

    return InferenceResponse(
        success=True,
        results=results,
        best_model=best_model,
        best_prediction=best_pred,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
