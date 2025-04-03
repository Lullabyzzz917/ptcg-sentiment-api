# PTCG Pocket 玩家輿情比較 API

這是一個用於分析 PTCG (Pokémon Trading Card Game) Pocket 遊戲玩家評論的 API 服務，可透過輸入兩組指定的日期區間，對玩家評論進行情感與趨勢分析，最終輸出一份綜合性的輿情比較報告。

## 功能特點

- **評論資料處理**：讀取、清理和過濾 CSV 格式的評論資料
- **情感分析**：使用 NLTK 或 Transformers 進行評論情感分析
- **趨勢分析**：分析評論數量、頻率、情感分佈和趨勢變化
- **時間段比較**：比較不同時間段的玩家評論情感和趨勢
- **報告生成**：生成 JSON、文字或 HTML 格式的輿情比較報告
- **視覺化圖表**：產生評分分佈、情感分佈和評論趨勢圖

## 安裝與設定

### 前置需求

- Python 3.8 或更高版本
- pip (Python 套件管理工具)
- 或 Docker 與 Docker Compose (選用)

### 安裝方法

#### 1. 使用 Python 直接安裝

1. 複製專案程式碼
   ```bash
   git clone https://github.com/Lullabyzzz917/ptcg-sentiment-api.git
   cd ptcg-sentiment-api
   ```

2. 安裝相依套件
   ```bash
   pip install -r requirements.txt
   ```

3. 準備資料檔案
   ```bash
   # 將 PTCG_Pocket.csv 檔案放入 data 目錄
   mkdir -p data
   cp /path/to/your/PTCG_Pocket.csv data/
   ```

#### 2. 使用 Docker 安裝

1. 複製專案程式碼
   ```bash
   git clone https://github.com/Lullabyzzz917/ptcg-sentiment-api.git
   cd ptcg-sentiment-api
   ```

2. 準備資料檔案
   ```bash
   # 將 PTCG_Pocket.csv 檔案放入 data 目錄
   mkdir -p data
   cp /path/to/your/PTCG_Pocket.csv data/
   ```

3. 使用 Docker Compose 建立和啟動容器
   ```bash
   docker-compose up -d
   ```

## 啟動服務

### 使用 Python 直接啟動

```bash
# 基本啟動
python main.py

# 指定參數啟動
python main.py --host 0.0.0.0 --port 8080 --csv-path data/PTCG_Pocket.csv --report-dir reports
```

### 使用 Docker 啟動

```bash
# 如果已經使用 docker-compose up -d 啟動，則無需此步驟
docker start ptcg-sentiment-api
```

## 使用說明

服務啟動後有兩種使用方式：通過網頁界面或直接調用 API。

### 方法一：使用網頁界面（推薦）

啟動服務後，在瀏覽器中打開 `http://localhost:8000` 即可進入玩家輿情分析儀表板。

儀表板功能：
1. **選擇比較時間段**：設定兩個時間段的開始和結束日期
2. **查看資料概要**：獲取基本資料統計和評分分佈
3. **生成分析報告**：選擇輸出格式（HTML、JSON 或文字），生成完整報告
4. **可視化展示**：報告中包含評分分佈、情感分析和趨勢圖表

### 方法二：直接調用 API

如果需要程式化操作，可直接調用 API 端點。API 文件可在 `http://localhost:8000/docs` 查看。

主要端點：

1. **GET /api/data/status** - 取得資料狀態和基本統計資訊
2. **GET /api/data/date-range** - 取得資料中的日期範圍
3. **GET /api/period-analysis** - 分析單一時間段的評論資料
4. **POST /api/comparison** - 比較兩個時間段的評論資料並生成報告

使用範例：

```bash
curl -X POST http://localhost:8000/api/comparison \
  -H "Content-Type: application/json" \
  -d '{
    "period1_start": "2025-01-01",
    "period1_end": "2025-01-15",
    "period2_start": "2025-02-01",
    "period2_end": "2025-02-15",
    "period1_name": "一月上旬",
    "period2_name": "二月上旬",
    "output_format": "html"
  }'
```

### 主要端點

1. **GET /api/data/status** - 取得資料狀態和基本統計資訊
2. **GET /api/data/date-range** - 取得資料中的日期範圍
3. **GET /api/period-analysis** - 分析單一時間段的評論資料
4. **POST /api/comparison** - 比較兩個時間段的評論資料並生成報告

### 使用範例

#### 比較兩個時間段的評論

```bash
curl -X POST http://localhost:8000/api/comparison \
  -H "Content-Type: application/json" \
  -d '{
    "period1_start": "2025-01-01",
    "period1_end": "2025-01-15",
    "period2_start": "2025-02-01",
    "period2_end": "2025-02-15",
    "period1_name": "一月上旬",
    "period2_name": "二月上旬",
    "output_format": "html"
  }'
```

## 測試

執行單元測試：

```bash
# 執行所有測試
pytest tests/

# 執行特定模組的測試
pytest tests/test_data_processor.py
```

## 專案結構

```
ptcg_sentiment_api/
├── data/
│   └── PTCG_Pocket.csv         # 評論資料 CSV 檔案
├── frontend/                   # 前端界面目錄
│   └── index.html              # 前端界面 HTML 檔案
├── src/
│   ├── __init__.py
│   ├── data_processor.py       # 資料處理模組
│   ├── sentiment_analyzer.py   # 情感分析模組
│   ├── data_analyzer.py        # 資料分析模組
│   ├── report_generator.py     # 報告生成模組
│   └── api.py                  # API 端點定義
├── tests/
│   ├── __init__.py
│   ├── test_data_processor.py
│   ├── test_sentiment_analyzer.py
│   ├── test_data_analyzer.py
│   └── test_api.py
├── reports/                    # 生成的報告儲存目錄
├── main.py                     # 主程式入口
├── init_frontend.py            # 前端初始化指令碼
├── requirements.txt            # 套件相依性
├── Dockerfile                  # Docker 配置
├── docker-compose.yml          # Docker Compose 配置
└── README.md                   # 說明文件
```

## 環境變數

- `CSV_PATH`：CSV 檔案路徑 (預設: `data/PTCG_Pocket.csv`)
- `REPORT_DIR`：報告輸出目錄 (預設: `reports`)
- `USE_TRANSFORMERS`：是否使用 Transformers 進行情感分析 (預設: `False`)

## 授權

MIT License