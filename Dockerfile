# 使用官方Python映像作為基礎
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴和中文字體
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    fonts-noto-cjk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 複製需要的檔案
COPY requirements.txt .
COPY data/ ./data/
COPY src/ ./src/
COPY tests/ ./tests/
COPY main.py .
COPY README.md .

# 建立報告輸出目錄
RUN mkdir -p reports

# 安裝依賴項目
RUN pip install --no-cache-dir -r requirements.txt

# 預下載NLTK資源
RUN python -c "import nltk; nltk.download('vader_lexicon')"

# 設定中文字體快取
RUN python -c "import matplotlib.font_manager as fm; fm.fontManager.rebuild()"

# 設定環境變數
ENV CSV_PATH=/app/data/PTCG_Pocket.csv
ENV REPORT_DIR=/app/reports
ENV USE_TRANSFORMERS=False

# 暴露連接埠
EXPOSE 8000

# 運行指令
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8000"]