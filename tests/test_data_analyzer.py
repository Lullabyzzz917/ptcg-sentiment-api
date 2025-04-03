"""
情感分析模組的單元測試
"""
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from src.sentiment_analyzer import SentimentAnalyzer

class TestSentimentAnalyzer(unittest.TestCase):
    """測試情感分析模組"""
    
    def setUp(self):
        """測試前設定"""
        # Patch NLTK下載功能避免在測試時下載
        patcher = patch('nltk.download')
        self.mock_nltk_download = patcher.start()
        self.addCleanup(patcher.stop)
        
        # Patch NLTK VADER功能
        patcher = patch('nltk.sentiment.SentimentIntensityAnalyzer')
        self.mock_vader = patcher.start()
        self.mock_vader_instance = self.mock_vader.return_value
        self.addCleanup(patcher.stop)
        
        # 建立範例資料
        self.sample_data = pd.DataFrame({
            'Content': [
                'I love this game, it is amazing!',
                'The game is okay, but could be better.',
                'This is the worst game ever, hate it!',
                None,
                ''
            ],
            'Title': [
                'Great game',
                'Average',
                'Terrible',
                'No comment',
                ''
            ]
        })
        
        # 設定VADER模擬回傳值
        self.mock_polarity_scores = {
            'I love this game, it is amazing!': {'compound': 0.8, 'neg': 0.0, 'neu': 0.4, 'pos': 0.6},
            'Great game': {'compound': 0.6, 'neg': 0.0, 'neu': 0.4, 'pos': 0.6},
            'The game is okay, but could be better.': {'compound': 0.0, 'neg': 0.2, 'neu': 0.6, 'pos': 0.2},
            'Average': {'compound': 0.0, 'neg': 0.0, 'neu': 1.0, 'pos': 0.0},
            'This is the worst game ever, hate it!': {'compound': -0.8, 'neg': 0.7, 'neu': 0.3, 'pos': 0.0},
            'Terrible': {'compound': -0.6, 'neg': 0.6, 'neu': 0.4, 'pos': 0.0},
            'No comment': {'compound': 0.0, 'neg': 0.0, 'neu': 1.0, 'pos': 0.0},
            '': {'compound': 0.0, 'neg': 0.0, 'neu': 0.0, 'pos': 0.0}
        }
        
        def side_effect(text):
            return self.mock_polarity_scores.get(text, {'compound': 0.0, 'neg': 0.0, 'neu': 1.0, 'pos': 0.0})
        
        self.mock_vader_instance.polarity_scores.side_effect = side_effect
        
        # 初始化情感分析器
        self.analyzer = SentimentAnalyzer(use_transformers=False)
    
    def test_init_with_vader(self):
        """測試使用VADER初始化"""
        analyzer = SentimentAnalyzer(use_transformers=False)
        self.assertFalse(analyzer.use_transformers)
        self.mock_vader.assert_called_once()
    
    @patch('transformers.pipeline')
    def test_init_with_transformers(self, mock_pipeline):
        """測試使用transformers初始化"""
        analyzer = SentimentAnalyzer(use_transformers=True)
        self.assertTrue(analyzer.use_transformers)
        mock_pipeline.assert_called_once_with("sentiment-analysis")
    
    def test_analyze_text_with_vader(self):
        """測試使用VADER分析文字"""
        # 測試正面情感
        result = self.analyzer.analyze_text("I love this game, it is amazing!")
        self.assertEqual(result["label"], "positive")
        self.assertEqual(result["score"], 0.8)
        
        # 測試中性情感
        result = self.analyzer.analyze_text("The game is okay, but could be better.")
        self.assertEqual(result["label"], "neutral")
        self.assertEqual(result["score"], 0.0)
        
        # 測試負面情感
        result = self.analyzer.analyze_text("This is the worst game ever, hate it!")
        self.assertEqual(result["label"], "negative")
        self.assertEqual(result["score"], -0.8)
        
        # 測試空文字
        result = self.analyzer.analyze_text("")
        self.assertEqual(result["label"], "neutral")
        self.assertEqual(result["score"], 0.0)
        
        # 測試None
        result = self.analyzer.analyze_text(None)
        self.assertEqual(result["label"], "neutral")
        self.assertEqual(result["score"], 0.5)
    
    @patch('transformers.pipeline')
    def test_analyze_text_with_transformers(self, mock_pipeline):
        """測試使用transformers分析文字"""
        # 設定mock回傳值
        mock_analyzer = MagicMock()
        mock_pipeline.return_value = mock_analyzer
        
        # 設定模擬回傳結果
        mock_analyzer.return_value = [{"label": "POSITIVE", "score": 0.9}]
        
        # 初始化使用transformers的分析器
        analyzer = SentimentAnalyzer(use_transformers=True)
        
        # 測試分析
        result = analyzer.analyze_text("I love this game")
        
        # 驗證結果
        self.assertEqual(result["label"], "positive")
        self.assertEqual(result["score"], 0.9)
        
        # 驗證调用
        mock_analyzer.assert_called_once_with("I love this game")
    
    def test_analyze_dataframe(self):
        """測試對資料框進行批次分析"""
        # 分析資料框
        result_df = self.analyzer.analyze_dataframe(self.sample_data)
        
        # 驗證結果
        self.assertEqual(len(result_df), 5)
        self.assertIn('sentiment_label', result_df.columns)
        self.assertIn('sentiment_score', result_df.columns)
        
        # 驗證具體結果
        self.assertEqual(result_df.iloc[0]['sentiment_label'], 'positive')
        self.assertEqual(result_df.iloc[1]['sentiment_label'], 'neutral')
        self.assertEqual(result_df.iloc[2]['sentiment_label'], 'negative')
        
        # 驗證缺失值處理
        self.assertEqual(result_df.iloc[3]['sentiment_label'], 'neutral')
        self.assertEqual(result_df.iloc[4]['sentiment_label'], 'neutral')
    
    def test_analyze_empty_dataframe(self):
        """測試處理空資料框"""
        empty_df = pd.DataFrame()
        result = self.analyzer.analyze_dataframe(empty_df)
        
        # 驗證返回空資料框
        self.assertTrue(result.empty)
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()