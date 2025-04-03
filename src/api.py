"""
API 模組 - 定義 API 端點與處理邏輯
"""
from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os
import logging
from datetime import datetime, timedelta
import uvicorn

from src.data_processor import DataProcessor
from src.sentiment_analyzer import SentimentAnalyzer
from src.data_analyzer import DataAnalyzer
from src.report_generator import ReportGenerator

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 建立 FastAPI 應用程式
app = FastAPI(
    title="PTCG Pocket 玩家輿情比較 API",
    description="透過指定的日期區間，對 PTCG Pocket 遊戲玩家評論進行情感與趨勢分析",
    version="1.0.0"
)

# 確保前端和報告目錄存在
os.makedirs("frontend", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# 掛載靜態檔案
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

# 主頁路由 - 提供前端界面
@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    # 讀取前端 HTML 檔案
    frontend_path = os.path.join("frontend", "index.html")
    
    # 如果檔案不存在，則創建一個
    if not os.path.exists(frontend_path):
        with open(frontend_path, "w", encoding="utf-8") as f:
            with open(os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html"), "r", encoding="utf-8") as template:
                f.write(template.read())
    
    # 返回 HTML 文件
    return FileResponse(frontend_path)

# 定義請求模型
class ComparisonRequest(BaseModel):
    period1_start: str = Field(..., description="第一個時間段的開始日期 (YYYY-MM-DD)")
    period1_end: str = Field(..., description="第一個時間段的結束日期 (YYYY-MM-DD)")
    period2_start: str = Field(..., description="第二個時間段的開始日期 (YYYY-MM-DD)")
    period2_end: str = Field(..., description="第二個時間段的結束日期 (YYYY-MM-DD)")
    period1_name: Optional[str] = Field("時間段1", description="第一個時間段的名稱")
    period2_name: Optional[str] = Field("時間段2", description="第二個時間段的名稱")
    output_format: Optional[str] = Field("json", description="輸出格式 (json, html, text)")

# 定義回應模型
class ComparisonResponse(BaseModel):
    status: str
    message: str
    period1_info: Dict[str, Any]
    period2_info: Dict[str, Any]
    comparison_result: Dict[str, Any]
    report_path: Optional[str] = None

# 依賴項目 - 建立資料處理器
def get_data_processor():
    csv_path = os.getenv("CSV_PATH", "data/PTCG_Pocket.csv")
    return DataProcessor(csv_path)

# 依賴項目 - 建立情感分析器
def get_sentiment_analyzer():
    use_transformers = os.getenv("USE_TRANSFORMERS", "False").lower() == "true"
    return SentimentAnalyzer(use_transformers=use_transformers)

# 依賴項目 - 建立資料分析器
def get_data_analyzer():
    return DataAnalyzer()

# 依賴項目 - 建立報告生成器
def get_report_generator():
    output_dir = os.getenv("REPORT_DIR", "reports")
    return ReportGenerator(output_dir=output_dir)

# 資料載入端點
@app.get("/api/data/status", response_model=Dict[str, Any])
async def get_data_status(data_processor: DataProcessor = Depends(get_data_processor)):
    """取得資料狀態"""
    try:
        # 載入資料
        df = data_processor.load_data()
        
        # 取得基本統計資訊
        stats = data_processor.get_data_stats(df)
        
        return {
            "status": "success",
            "message": "資料載入成功",
            "data_stats": stats
        }
    except Exception as e:
        logger.error(f"取得資料狀態時發生錯誤：{str(e)}")
        raise HTTPException(status_code=500, detail=f"處理資料時發生錯誤：{str(e)}")

# 主要比較端點
@app.post("/api/comparison", response_model=ComparisonResponse)
async def compare_periods(
    request: ComparisonRequest,
    data_processor: DataProcessor = Depends(get_data_processor),
    sentiment_analyzer: SentimentAnalyzer = Depends(get_sentiment_analyzer),
    data_analyzer: DataAnalyzer = Depends(get_data_analyzer),
    report_generator: ReportGenerator = Depends(get_report_generator)
):
    """
    比較兩個時間段的玩家評論情感與趨勢
    """
    try:
        # 1. 載入資料
        logger.info("開始比較兩個時間段的資料")
        df = data_processor.load_data()
        
        # 2. 過濾兩個時間段的資料
        df_period1 = data_processor.filter_by_date_range(request.period1_start, request.period1_end)
        df_period2 = data_processor.filter_by_date_range(request.period2_start, request.period2_end)
        
        # 檢查資料是否足夠
        if len(df_period1) < 10 or len(df_period2) < 10:
            return {
                "status": "warning",
                "message": "一個或兩個時間段的資料量過少，分析結果可能不夠準確",
                "period1_info": {"review_count": len(df_period1)},
                "period2_info": {"review_count": len(df_period2)},
                "comparison_result": {"warning": "資料量不足"}
            }
        
        # 3. 情感分析
        logger.info(f"正在對第一個時間段的 {len(df_period1)} 則評論進行情感分析")
        df_period1_with_sentiment = sentiment_analyzer.analyze_dataframe(df_period1)
        
        logger.info(f"正在對第二個時間段的 {len(df_period2)} 則評論進行情感分析")
        df_period2_with_sentiment = sentiment_analyzer.analyze_dataframe(df_period2)
        
        # 4. 資料分析
        # 4.1 基本統計資訊
        period1_stats = data_processor.get_data_stats(df_period1_with_sentiment)
        period2_stats = data_processor.get_data_stats(df_period2_with_sentiment)
        
        # 4.2 評論數量分析
        period1_volume = data_analyzer.analyze_review_volume(df_period1_with_sentiment)
        period2_volume = data_analyzer.analyze_review_volume(df_period2_with_sentiment)
        
        # 4.3 情感分佈分析
        period1_sentiment = data_analyzer.analyze_sentiment_distribution(df_period1_with_sentiment)
        period2_sentiment = data_analyzer.analyze_sentiment_distribution(df_period2_with_sentiment)
        
        # 4.4 情感趨勢分析
        period1_trend = data_analyzer.analyze_sentiment_trend(df_period1_with_sentiment)
        period2_trend = data_analyzer.analyze_sentiment_trend(df_period2_with_sentiment)
        
        # 4.5 話題分析
        period1_topics = data_analyzer.analyze_topics(df_period1_with_sentiment)
        period2_topics = data_analyzer.analyze_topics(df_period2_with_sentiment)
        
        # 5. 比較兩個時間段
        comparison_result = data_analyzer.compare_time_periods(
            df_period1_with_sentiment, 
            df_period2_with_sentiment,
            request.period1_name,
            request.period2_name
        )
        
        # 6. 生成報告
        report_path = None
        if request.output_format.lower() == "json":
            report_path = report_generator.generate_json_report(
                comparison_result,
                request.period1_name,
                request.period2_name
            )
        elif request.output_format.lower() == "text":
            report_path = report_generator.generate_text_report(
                comparison_result,
                request.period1_name,
                request.period2_name
            )
        elif request.output_format.lower() == "html":
            report_path = report_generator.generate_html_report(
                comparison_result,
                df_period1_with_sentiment,
                df_period2_with_sentiment,
                request.period1_name,
                request.period2_name
            )
        
        # 7. 返回結果
        return {
            "status": "success",
            "message": "比較分析完成",
            "period1_info": {
                "name": request.period1_name,
                "start_date": request.period1_start,
                "end_date": request.period1_end,
                "review_count": len(df_period1),
                "stats": period1_stats,
                "volume": period1_volume,
                "sentiment": period1_sentiment,
                "trend": period1_trend,
                "topics": period1_topics
            },
            "period2_info": {
                "name": request.period2_name,
                "start_date": request.period2_start,
                "end_date": request.period2_end,
                "review_count": len(df_period2),
                "stats": period2_stats,
                "volume": period2_volume,
                "sentiment": period2_sentiment,
                "trend": period2_trend,
                "topics": period2_topics
            },
            "comparison_result": comparison_result,
            "report_path": report_path
        }
    
    except ValueError as e:
        logger.error(f"請求參數錯誤：{str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"比較時間段時發生錯誤：{str(e)}")
        raise HTTPException(status_code=500, detail=f"處理請求時發生錯誤：{str(e)}")

# 簡單分析單一時間段端點
@app.get("/api/period-analysis", response_model=Dict[str, Any])
async def analyze_single_period(
    start_date: str = Query(..., description="開始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="結束日期 (YYYY-MM-DD)"),
    period_name: str = Query("分析時段", description="時間段名稱"),
    data_processor: DataProcessor = Depends(get_data_processor),
    sentiment_analyzer: SentimentAnalyzer = Depends(get_sentiment_analyzer),
    data_analyzer: DataAnalyzer = Depends(get_data_analyzer)
):
    """
    分析單一時間段的玩家評論情感與趨勢
    """
    try:
        # 1. 載入資料
        df = data_processor.load_data()
        
        # 2. 過濾時間段的資料
        df_period = data_processor.filter_by_date_range(start_date, end_date)
        
        # 檢查資料是否足夠
        if len(df_period) < 10:
            return {
                "status": "warning",
                "message": "時間段的資料量過少，分析結果可能不夠準確",
                "period_info": {"review_count": len(df_period)},
                "analysis_result": {"warning": "資料量不足"}
            }
        
        # 3. 情感分析
        logger.info(f"正在對時間段的 {len(df_period)} 則評論進行情感分析")
        df_period_with_sentiment = sentiment_analyzer.analyze_dataframe(df_period)
        
        # 4. 資料分析
        # 4.1 基本統計資訊
        period_stats = data_processor.get_data_stats(df_period_with_sentiment)
        
        # 4.2 評論數量分析
        period_volume = data_analyzer.analyze_review_volume(df_period_with_sentiment)
        
        # 4.3 情感分佈分析
        period_sentiment = data_analyzer.analyze_sentiment_distribution(df_period_with_sentiment)
        
        # 4.4 情感趨勢分析
        period_trend = data_analyzer.analyze_sentiment_trend(df_period_with_sentiment)
        
        # 4.5 話題分析
        period_topics = data_analyzer.analyze_topics(df_period_with_sentiment)
        
        # 5. 返回結果
        return {
            "status": "success",
            "message": "分析完成",
            "period_info": {
                "name": period_name,
                "start_date": start_date,
                "end_date": end_date,
                "review_count": len(df_period),
                "stats": period_stats,
                "volume": period_volume,
                "sentiment": period_sentiment,
                "trend": period_trend,
                "topics": period_topics
            }
        }
    
    except ValueError as e:
        logger.error(f"請求參數錯誤：{str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"分析時間段時發生錯誤：{str(e)}")
        raise HTTPException(status_code=500, detail=f"處理請求時發生錯誤：{str(e)}")

# 取得可用資料日期範圍
@app.get("/api/data/date-range", response_model=Dict[str, Any])
async def get_date_range(data_processor: DataProcessor = Depends(get_data_processor)):
    """取得資料的日期範圍"""
    try:
        # 載入資料
        df = data_processor.load_data()
        
        # 取得日期範圍
        min_date = df['Date'].min().strftime('%Y-%m-%d') if not df.empty else None
        max_date = df['Date'].max().strftime('%Y-%m-%d') if not df.empty else None
        
        return {
            "status": "success",
            "message": "日期範圍獲取成功",
            "min_date": min_date,
            "max_date": max_date
        }
    except Exception as e:
        logger.error(f"取得日期範圍時發生錯誤：{str(e)}")
        raise HTTPException(status_code=500, detail=f"處理請求時發生錯誤：{str(e)}")