FROM python:3.11-slim

# 安裝系統套件
RUN apt-get update && \
    apt-get install -y gcc build-essential libffi-dev && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-chi-tra libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 安裝 Python 套件
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 複製專案檔案
COPY . .

# 啟動腳本權限
RUN chmod +x start.sh

# 啟動指令
CMD ["./start.sh"]
