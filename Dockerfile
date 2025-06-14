FROM python:3.11-slim

RUN apt-get update && apt-get install -y gcc build-essential libffi-dev && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-chi-tra libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
