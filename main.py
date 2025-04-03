"""
PTCG Pocket 玩家輿情比較 API - 主程式入口點
"""
import os
import sys
import logging
import argparse
import uvicorn
from src.api import app

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

def parse_args():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description='PTCG Pocket 玩家輿情比較 API - 分析玩家評論情感與趨勢'
    )
    parser.add_argument(
        '--host', 
        type=str, 
        default='0.0.0.0', 
        help='服務主機名稱或IP地址 (預設: 0.0.0.0)'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=8000, 
        help='服務連接埠 (預設: 8000)'
    )
    parser.add_argument(
        '--csv-path', 
        type=str, 
        default='data/PTCG_Pocket.csv', 
        help='CSV檔案路徑 (預設: data/PTCG_Pocket.csv)'
    )
    parser.add_argument(
        '--report-dir', 
        type=str, 
        default='reports', 
        help='報告輸出目錄 (預設: reports)'
    )
    parser.add_argument(
        '--use-transformers', 
        action='store_true', 
        help='使用transformers進行情感分析 (預設: False)'
    )
    parser.add_argument(
        '--reload', 
        action='store_true', 
        help='啟用熱重載 (預設: False)'
    )
    
    return parser.parse_args()

def main():
    """主程式入口"""
    # 解析命令列參數
    args = parse_args()
    
    # 設定環境變數
    os.environ['CSV_PATH'] = args.csv_path
    os.environ['REPORT_DIR'] = args.report_dir
    os.environ['USE_TRANSFORMERS'] = str(args.use_transformers)
    
    # 確保報告目錄存在
    os.makedirs(args.report_dir, exist_ok=True)
    
    # 確保資料目錄存在
    os.makedirs(os.path.dirname(args.csv_path), exist_ok=True)
    
    # 確保前端目錄存在
    frontend_dir = "frontend"
    os.makedirs(frontend_dir, exist_ok=True)
    
    # 初始化前端界面
    try:
        logger.info("初始化前端界面...")
        exec(open("init_frontend.py").read())
        logger.info("前端界面初始化完成")
    except Exception as e:
        logger.warning(f"初始化前端界面時發生錯誤: {str(e)}，將使用預設API文檔頁面")
    
    # 顯示啟動資訊
    logger.info(f"正在啟動 PTCG Pocket 玩家輿情比較 API 服務...")
    logger.info(f"主機: {args.host}")
    logger.info(f"連接埠: {args.port}")
    logger.info(f"CSV檔案路徑: {args.csv_path}")
    logger.info(f"報告輸出目錄: {args.report_dir}")
    logger.info(f"使用transformers進行情感分析: {args.use_transformers}")
    logger.info(f"啟用熱重載: {args.reload}")
    logger.info(f"網頁界面: http://{args.host}:{args.port}")
    logger.info(f"API文檔: http://{args.host}:{args.port}/docs")
    
    # 啟動API服務
    uvicorn.run(
        "src.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()