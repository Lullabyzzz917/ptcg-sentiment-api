"""
情感分析模組 - 負責對評論文字進行情感分析
"""
import pandas as pd
import numpy as np
from transformers import pipeline
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """對評論文字進行情感分析"""
    
    def __init__(self, use_transformers=False, neutral_threshold=0.15):
        """
        初始化情感分析器
        
        Args:
            use_transformers (bool): 是否使用transformers模型，預設為False使用NLTK的VADER
            neutral_threshold (float): 中性情感的閾值範圍，預設為0.15
        """
        self.use_transformers = use_transformers
        self.neutral_threshold = neutral_threshold
        
        # 初始化情感分析器
        try:
            if use_transformers:
                logger.info("正在初始化Hugging Face Transformers情感分析模型...")
                self.analyzer = pipeline("sentiment-analysis")
            else:
                logger.info("正在初始化NLTK VADER情感分析器...")
                try:
                    nltk.data.find('sentiment/vader_lexicon.zip')
                except LookupError:
                    logger.info("下載NLTK VADER詞典...")
                    nltk.download('vader_lexicon')
                self.analyzer = SentimentIntensityAnalyzer()
        except Exception as e:
            logger.error(f"初始化情感分析器時發生錯誤: {str(e)}")
            raise
    
    def analyze_text(self, text):
        """
        分析單一文本的情感
        
        Args:
            text (str): 要分析的文字
            
        Returns:
            dict: 包含情感分數和標籤的字典
        """
        if not text or not isinstance(text, str):
            return {"label": "neutral", "score": 0.5}
        
        try:
            if self.use_transformers:
                # 使用transformers模型
                result = self.analyzer(text[:512])[0]
                
                # 轉換標籤格式
                return {
                    "label": result["label"].lower(),
                    "score": result["score"]
                }
            else:
                # 使用NLTK VADER
                scores = self.analyzer.polarity_scores(text)
                
                if scores['compound'] >= self.neutral_threshold:
                    label = "positive"
                elif scores['compound'] <= -self.neutral_threshold:
                    label = "negative"
                else:
                    label = "neutral"
                
                return {
                    "label": label,
                    "score": scores['compound']
                }
        except Exception as e:
            logger.error(f"分析文字時發生錯誤: {str(e)}")
            return {"label": "neutral", "score": 0.5}
    
    def analyze_dataframe(self, df, text_column='Content', title_column='Title', batch_size=100):
        """
        對資料框中的評論進行批次情感分析
        
        Args:
            df (pandas.DataFrame): 包含評論的資料框
            text_column (str): 包含評論文字的欄位名稱
            title_column (str): 包含評論標題的欄位名稱
            batch_size (int): 批次處理的大小
            
        Returns:
            pandas.DataFrame: 帶有情感分析結果的資料框
        """
        if df.empty:
            logger.warning("傳入的資料框為空，無法進行情感分析")
            return df
        
        logger.info(f"開始對 {len(df)} 筆評論進行情感分析...")
        
        # 建立結果資料框的副本
        result_df = df.copy()
        
        # 對文字內容和標題組合進行分析
        def analyze_row(row):
            # 合併標題和內容進行分析
            combined_text = ""
            if title_column in row and pd.notna(row[title_column]):
                combined_text += str(row[title_column]) + ". "
            
            if text_column in row and pd.notna(row[text_column]):
                combined_text += str(row[text_column])
            
            # 如果沒有文字，返回中性判斷
            if not combined_text.strip():
                return {"label": "neutral", "score": 0.5}
                
            return self.analyze_text(combined_text)
        
        # 準備批次處理
        total_rows = len(df)
        results = []
        
        # 使用多線程處理
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            # 提交所有任務
            future_to_index = {executor.submit(analyze_row, row): i for i, row in df.iterrows()}
            
            # 處理結果
            for i, future in enumerate(as_completed(future_to_index)):
                index = future_to_index[future]
                try:
                    result = future.result()
                    results.append((index, result))
                    
                    # 顯示進度
                    if (i + 1) % 100 == 0 or (i + 1) == total_rows:
                        logger.info(f"情感分析進度: {i + 1}/{total_rows} ({((i + 1) / total_rows * 100):.1f}%)")
                except Exception as e:
                    logger.error(f"處理索引 {index} 時發生錯誤: {str(e)}")
                    results.append((index, {"label": "neutral", "score": 0.5}))
                    
        # 將結果整合到資料框
        for index, result in results:
            result_df.at[index, 'sentiment_label'] = result["label"]
            result_df.at[index, 'sentiment_score'] = result["score"]
            
        logger.info("情感分析完成")
        return result_df