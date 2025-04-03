"""
資料處理模組的單元測試
"""
import unittest
from unittest.mock import patch, mock_open, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime
from src.data_processor import DataProcessor

class TestDataProcessor(unittest.TestCase):
    """測試資料處理模組"""
    
    def setUp(self):
        """測試前設定"""
        self.csv_path = 'test_data.csv'
        self.processor = DataProcessor(self.csv_path)
        
        # 建立範例資料
        self.sample_data = pd.DataFrame({
            'Country': ['US', 'US', 'US', 'US', 'US'],
            'Rating': [5, 4, 3, 2, 1],
            'Date': pd.to_datetime(['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05']),
            'Version': ['1.1.0', '1.1.0', '1.1.1', '1.1.1', '1.1.2'],
            'Username': ['User1', 'User2', 'User3', 'User4', 'User5'],
            'Title': ['Great', 'Good', 'Average', 'Poor', 'Terrible'],
            'Content': ['I love this game', 'Nice game', 'It is okay', 'Not good', 'Hate it']
        })
    
    @patch('pandas.read_csv')
    def test_load_data(self, mock_read_csv):
        """測試資料載入功能"""
        # 設定模擬的回傳值
        mock_read_csv.return_value = self.sample_data
        
        # 呼叫要測試的方法
        result = self.processor.load_data()
        
        # 驗證結果
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 5)
        self.assertEqual(list(result.columns), ['Country', 'Rating', 'Date', 'Version', 'Username', 'Title', 'Content'])
        
        # 確認read_csv被調用，且使用正確的參數
        mock_read_csv.assert_called_once_with(self.csv_path, sep='\t')
    
    def test_clean_data(self):
        """測試資料清理功能"""
        # 準備包含問題的測試資料
        dirty_data = pd.DataFrame({
            'Country': ['US', 'US', None, 'US', 'US'],
            'Rating': [5, 4, 3, 'invalid', 6],  # 包含非數字和超出範圍的評分
            'Date': ['2025-01-01', '2025-01-02', '2025-01-03', 'invalid', '2025-01-05'],
            'Version': ['1.1.0', '1.1.0', '1.1.1', '1.1.1', '1.1.2'],
            'Username': ['User1', 'User2', 'User3', 'User4', 'User5'],
            'Title': ['Great', 'Good', 'Average', 'Poor', 'Terrible'],
            'Content': ['I love this game', 'Nice game', None, 'Not good', 'Hate it']
        })
        
        # 轉換日期欄位為datetime（僅對有效日期）
        dirty_data['Date'] = pd.to_datetime(dirty_data['Date'], errors='coerce')
        
        # 呼叫清理方法
        result = self.processor._clean_data(dirty_data)
        
        # 驗證結果
        self.assertEqual(len(result), 2)  # 只有兩筆資料應該保留
        
        # 驗證清理後的資料只包含有效評分
        self.assertTrue(all(1 <= r <= 5 for r in result['Rating']))
        
        # 驗證清理後的資料只包含有效日期
        self.assertTrue(all(isinstance(d, pd.Timestamp) for d in result['Date']))
        
        # 驗證清理後的資料不包含缺失值
        self.assertFalse(result[['Country', 'Rating', 'Date', 'Content']].isna().any().any())
    
    def test_filter_by_date_range(self):
        """測試日期範圍過濾功能"""
        # 設定處理器的已處理資料
        self.processor.processed_data = self.sample_data
        
        # 設定日期範圍
        start_date = '2025-01-02'
        end_date = '2025-01-04'
        
        # 呼叫過濾方法
        result = self.processor.filter_by_date_range(start_date, end_date)
        
        # 驗證結果
        self.assertEqual(len(result), 3)  # 應該有3筆資料在範圍內
        self.assertTrue(all(pd.to_datetime(start_date) <= d <= pd.to_datetime(end_date) for d in result['Date']))
    
    def test_filter_by_date_range_error(self):
        """測試日期範圍過濾功能的錯誤處理"""
        # 未設定processed_data
        self.processor.processed_data = None
        
        # 設定日期範圍
        start_date = '2025-01-02'
        end_date = '2025-01-04'
        
        # 呼叫過濾方法應該引發ValueError
        with self.assertRaises(ValueError):
            self.processor.filter_by_date_range(start_date, end_date)
    
    def test_get_data_stats(self):
        """測試取得資料統計資訊功能"""
        # 設定處理器的已處理資料
        self.processor.processed_data = self.sample_data
        
        # 呼叫統計方法
        stats = self.processor.get_data_stats()
        
        # 驗證結果
        self.assertEqual(stats['total_reviews'], 5)
        self.assertEqual(stats['average_rating'], 3.0)
        self.assertEqual(stats['date_range']['min'], '2025-01-01')
        self.assertEqual(stats['date_range']['max'], '2025-01-05')
        self.assertIn('rating_distribution', stats)
        self.assertIn('version_distribution', stats)

if __name__ == '__main__':
    unittest.main()