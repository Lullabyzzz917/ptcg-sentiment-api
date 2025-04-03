"""
資料處理模組 - 負責CSV檔案讀取、清理與過濾
"""
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataProcessor:
    """處理PTCG Pocket評論資料"""
    
    def __init__(self, csv_path):
        """
        初始化資料處理器
        
        Args:
            csv_path (str): CSV檔案路徑
        """
        self.csv_path = csv_path
        self.raw_data = None
        self.processed_data = None
    
    def load_data(self):
        """
        讀取CSV檔案並進行基本清理
        
        Returns:
            pandas.DataFrame: 清理過的資料
        """
        logger.info(f"正在讀取CSV檔案: {self.csv_path}")
        
        try:
            # 讀取CSV檔案，處理可能的編碼問題
            try:
                # 首先嘗試正常讀取
                self.raw_data = pd.read_csv(self.csv_path, sep='\t')
            except UnicodeDecodeError:
                # 如果出現編碼問題，嘗試用不同編碼格式
                self.raw_data = pd.read_csv(self.csv_path, sep='\t', encoding='utf-16le')
                
            logger.info(f"成功讀取CSV檔案，原始資料筆數: {len(self.raw_data)}")
            
            # 清理資料
            self.processed_data = self._clean_data(self.raw_data)
            logger.info(f"資料清理完成，清理後資料筆數: {len(self.processed_data)}")
            
            return self.processed_data
            
        except Exception as e:
            logger.error(f"讀取CSV檔案時發生錯誤: {str(e)}")
            raise
    
    def _clean_data(self, df):
        """
        清理資料，處理缺失值、格式問題等
        
        Args:
            df (pandas.DataFrame): 原始資料框
            
        Returns:
            pandas.DataFrame: 清理後的資料框
        """
        # 複製資料框以避免修改原始資料
        cleaned_df = df.copy()
        
        # 移除缺少主要欄位的資料
        cleaned_df = cleaned_df.dropna(subset=['Country', 'Rating', 'Date', 'Content'])
        
        # 確保Rating是數值型態且在1-5範圍
        cleaned_df = cleaned_df[cleaned_df['Rating'].apply(lambda x: isinstance(x, (int, float)) and 1 <= x <= 5)]
        
        # 轉換日期格式，排除無效日期
        cleaned_df['Date'] = pd.to_datetime(cleaned_df['Date'], errors='coerce')
        cleaned_df = cleaned_df.dropna(subset=['Date'])
        
        # 重設索引
        cleaned_df = cleaned_df.reset_index(drop=True)
        
        return cleaned_df
    
    def filter_by_date_range(self, start_date, end_date):
        """
        根據日期範圍過濾資料
        
        Args:
            start_date (str): 開始日期 (YYYY-MM-DD)
            end_date (str): 結束日期 (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: 過濾後的資料
        """
        if self.processed_data is None:
            raise ValueError("請先呼叫load_data()方法載入資料")
        
        # 轉換日期字串為datetime物件
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # 過濾資料
        filtered_data = self.processed_data[(self.processed_data['Date'] >= start_date) & 
                                           (self.processed_data['Date'] <= end_date)]
        
        logger.info(f"根據日期範圍 {start_date.date()} 至 {end_date.date()} 過濾後，取得 {len(filtered_data)} 筆資料")
        
        return filtered_data
    
    def get_data_stats(self, df=None):
        """
        取得資料基本統計資訊
        
        Args:
            df (pandas.DataFrame, optional): 要分析的資料框，如果未提供則使用整個處理過的資料
            
        Returns:
            dict: 包含基本統計資訊的字典
        """
        if df is None:
            if self.processed_data is None:
                raise ValueError("請先呼叫load_data()方法載入資料")
            df = self.processed_data
        
        # 計算基本統計數據
        stats = {
            'total_reviews': len(df),
            'rating_distribution': df['Rating'].value_counts().to_dict(),
            'average_rating': round(df['Rating'].mean(), 2),
            'date_range': {
                'min': df['Date'].min().date().isoformat() if not df.empty else None,
                'max': df['Date'].max().date().isoformat() if not df.empty else None
            },
            'version_distribution': df['Version'].value_counts().to_dict()
        }
        
        return stats