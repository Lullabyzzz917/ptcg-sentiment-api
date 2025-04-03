"""
API模組的單元測試
"""
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import pandas as pd
from datetime import datetime, timedelta

from src.api import app
from src.data_processor import DataProcessor
from src.sentiment_analyzer import SentimentAnalyzer
from src.data_analyzer import DataAnalyzer
from src.report_generator import ReportGenerator

class TestAPI(unittest.TestCase):
    """測試API模組"""
    
    def setUp(self):
        """測試前設定"""
        self.client = TestClient(app)
        
        # 模擬資料
        dates = pd.date_range(start='2025-01-01', end='2025-01-10')
        self.sample_data = pd.DataFrame({
            'Country': ['US'] * 10,
            'Rating': [5, 4, 5, 3, 4, 5, 2, 4, 5, 3],
            'Date': dates,
            'Version': ['1.1.0'] * 10,
            'Username': [f'User{i}' for i in range(1, 11)],
            'Title': ['Great', 'Good', 'Wow', 'Okay', 'Nice',
                     'Perfect', 'Poor', 'Good stuff', 'Awesome', 'Meh'],
            'Content': ['Great game', 'I like it', 'Amazing', 'It is okay', 'Pretty good',
                       'Excellent', 'Not good', 'Nice features', 'Love it', 'Average game']
        })
        
        # 模擬情感分析後的資料
        self.sample_data_with_sentiment = self.sample_data.copy()
        self.sample_data_with_sentiment['sentiment_label'] = ['positive', 'positive', 'positive', 'neutral', 'positive', 
                                                             'positive', 'negative', 'positive', 'positive', 'neutral']
        self.sample_data_with_sentiment['sentiment_score'] = [0.8, 0.6, 0.7, 0.0, 0.5, 0.9, -0.3, 0.4, 0.7, 0.1]
    
    @patch('src.api.get_data_processor')
    def test_get_data_status(self, mock_get_processor):
        """測試取得資料狀態端點"""
        # 設定模擬
        mock_processor = MagicMock()
        mock_processor.load_data.return_value = self.sample_data
        mock_processor.get_data_stats.return_value = {
            'total_reviews': 10,
            'rating_distribution': {5: 4, 4: 3, 3: 2, 2: 1},
            'average_rating': 4.0,
            'date_range': {'min': '2025-01-01', 'max': '2025-01-10'},
            'version_distribution': {'1.1.0': 10}
        }
        mock_get_processor.return_value = mock_processor
        
        # 呼叫API
        response = self.client.get("/api/data/status")
        
        # 驗證結果
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertIn('data_stats', response.json())
        
        # 驗證調用
        mock_processor.load_data.assert_called_once()
        mock_processor.get_data_stats.assert_called_once()
    
    @patch('src.api.get_data_processor')
    def test_get_data_status_error(self, mock_get_processor):
        """測試取得資料狀態端點的錯誤處理"""
        # 設定模擬
        mock_processor = MagicMock()
        mock_processor.load_data.side_effect = Exception("測試錯誤")
        mock_get_processor.return_value = mock_processor
        
        # 呼叫API
        response = self.client.get("/api/data/status")
        
        # 驗證結果
        self.assertEqual(response.status_code, 500)
        self.assertIn('detail', response.json())
    
    @patch('src.api.get_report_generator')
    @patch('src.api.get_data_analyzer')
    @patch('src.api.get_sentiment_analyzer')
    @patch('src.api.get_data_processor')
    def test_compare_periods(self, mock_get_processor, mock_get_sentiment, mock_get_analyzer, mock_get_report):
        """測試比較時間段端點"""
        # 設定資料處理器模擬
        mock_processor = MagicMock()
        mock_processor.load_data.return_value = self.sample_data
        mock_processor.filter_by_date_range.side_effect = [
            self.sample_data.iloc[:5],  # 第一個時間段
            self.sample_data.iloc[5:]   # 第二個時間段
        ]
        mock_processor.get_data_stats.side_effect = [
            {'total_reviews': 5},  # 第一個時間段
            {'total_reviews': 5}   # 第二個時間段
        ]
        mock_get_processor.return_value = mock_processor
        
        # 設定情感分析器模擬
        mock_sentiment = MagicMock()
        mock_sentiment.analyze_dataframe.side_effect = [
            self.sample_data_with_sentiment.iloc[:5],  # 第一個時間段
            self.sample_data_with_sentiment.iloc[5:]   # 第二個時間段
        ]
        mock_get_sentiment.return_value = mock_sentiment
        
        # 設定資料分析器模擬
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_review_volume.return_value = {'total_reviews': 5}
        mock_analyzer.analyze_sentiment_distribution.return_value = {'sentiment_distribution': {}}
        mock_analyzer.analyze_sentiment_trend.return_value = {'sentiment_trend': {}}
        mock_analyzer.analyze_topics.return_value = {'top_keywords': {}}
        mock_analyzer.compare_time_periods.return_value = {
            'time_periods': {},
            'review_volume': {},
            'rating': {},
            'sentiment': {},
            'version': {},
            'summary': ['測試摘要']
        }
        mock_get_analyzer.return_value = mock_analyzer
        
        # 設定報告生成器模擬
        mock_report = MagicMock()
        mock_report.generate_json_report.return_value = 'reports/test_report.json'
        mock_get_report.return_value = mock_report
        
        # 準備請求資料
        request_data = {
            "period1_start": "2025-01-01",
            "period1_end": "2025-01-05",
            "period2_start": "2025-01-06",
            "period2_end": "2025-01-10",
            "period1_name": "第一週",
            "period2_name": "第二週",
            "output_format": "json"
        }
        
        # 呼叫API
        response = self.client.post("/api/comparison", json=request_data)
        
        # 驗證結果
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertIn('period1_info', response.json())
        self.assertIn('period2_info', response.json())
        self.assertIn('comparison_result', response.json())
        self.assertIn('report_path', response.json())
    
    @patch('src.api.get_data_processor')
    def test_get_date_range(self, mock_get_processor):
        """測試取得日期範圍端點"""
        # 設定模擬
        mock_processor = MagicMock()
        mock_processor.load_data.return_value = self.sample_data
        mock_get_processor.return_value = mock_processor
        
        # 呼叫API
        response = self.client.get("/api/data/date-range")
        
        # 驗證結果
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertIn('min_date', response.json())
        self.assertIn('max_date', response.json())

if __name__ == '__main__':
    unittest.main()