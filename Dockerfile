
# 多階段建置，減少映像大小
FROM python:3.11-slim AS builder
RUN apt-get update && \
    apt-get install -y gcc build-essential libffi-dev \
    tesseract-ocr tesseract-ocr-chi-tra libgl1 && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

FROM python:3.11-slim
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-chi-tra libgl1 && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8080"]
