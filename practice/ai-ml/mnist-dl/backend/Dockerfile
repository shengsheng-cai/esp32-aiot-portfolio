FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "\
from transformers import ViTImageProcessor, ViTForImageClassification; \
ViTImageProcessor.from_pretrained('google/vit-base-patch16-224'); \
ViTForImageClassification.from_pretrained('google/vit-base-patch16-224', num_labels=10, ignore_mismatched_sizes=True); \
ViTImageProcessor.from_pretrained('farleyknight-org-username/vit-base-mnist'); \
ViTForImageClassification.from_pretrained('farleyknight-org-username/vit-base-mnist'); \
print('HuggingFace models cached.')"

COPY app.py models.py preprocessing.py .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
