"""
資料分析模組 - 負責評論數量、情感與趨勢分析
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from collections import Counter

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataAnalyzer:
    """分析評論資料的數量、情感與趨勢"""
    
    def __init__(self):
        """初始化資料分析器"""
        pass
    
    def analyze_review_volume(self, df, freq='D'):
        """
        分析評論數量隨時間的變化
        
        Args:
            df (pandas.DataFrame): 包含評論資料的資料框
            freq (str): 時間頻率，例如 'D'表示天，'W'表示週，'M'表示月
            
        Returns:
            dict: 包含評論數量統計的字典
        """
        if df.empty:
            logger.warning("傳入的資料框為空，無法進行評論數量分析")
            return {"review_counts": {}}
        
        # 確保日期欄位是datetime類型
        if not pd.api.types.is_datetime64_dtype(df['Date']):
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna(subset=['Date'])
        
        # 按時間頻率統計評論數量
        review_counts = df.groupby(pd.Grouper(key='Date', freq=freq)).size()
        
        # 轉換為字典，將日期格式化為字串
        review_counts_dict = {date.strftime('%Y-%m-%d'): count for date, count in review_counts.items()}
        
        # 計算平均每日評論數
        avg_daily_reviews = review_counts.mean()
        
        # 計算評論數量最高的日期
        peak_date = review_counts.idxmax().strftime('%Y-%m-%d')
        peak_count = review_counts.max()
        
        result = {
            "review_counts": review_counts_dict,
            "total_reviews": int(review_counts.sum()),
            "average_daily_reviews": float(avg_daily_reviews),
            "peak_date": peak_date,
            "peak_count": int(peak_count)
        }
        
        return result
    
    def analyze_sentiment_distribution(self, df):
        """
        分析情感分佈
        
        Args:
            df (pandas.DataFrame): 包含評論和情感分析結果的資料框
            
        Returns:
            dict: 包含情感分析統計的字典
        """
        if df.empty or 'sentiment_label' not in df.columns:
            logger.warning("傳入的資料框為空或缺少情感分析結果，無法進行情感分佈分析")
            return {"sentiment_distribution": {}}
        
        # 計算情感分佈
        sentiment_counts = df['sentiment_label'].value_counts().to_dict()
        
        # 計算正面評論的比例
        positive_ratio = sentiment_counts.get('positive', 0) / len(df) if len(df) > 0 else 0
        negative_ratio = sentiment_counts.get('negative', 0) / len(df) if len(df) > 0 else 0
        neutral_ratio = sentiment_counts.get('neutral', 0) / len(df) if len(df) > 0 else 0
        
        # 計算平均情感分數
        avg_sentiment_score = df['sentiment_score'].mean() if 'sentiment_score' in df.columns else 0
        
        # 情感分數的標準差
        sentiment_score_std = df['sentiment_score'].std() if 'sentiment_score' in df.columns else 0
        
        # 評分與情感的相關性
        rating_sentiment_corr = df[['Rating', 'sentiment_score']].corr().iloc[0, 1] if 'Rating' in df.columns and len(df) > 1 else 0
        
        result = {
            "sentiment_distribution": sentiment_counts,
            "positive_ratio": float(positive_ratio),
            "negative_ratio": float(negative_ratio),
            "neutral_ratio": float(neutral_ratio),
            "average_sentiment_score": float(avg_sentiment_score),
            "sentiment_score_std": float(sentiment_score_std),
            "rating_sentiment_correlation": float(rating_sentiment_corr)
        }
        
        return result
    
    def analyze_sentiment_trend(self, df, freq='D'):
        """
        分析隨時間的情感趨勢
        
        Args:
            df (pandas.DataFrame): 包含評論和情感分析結果的資料框
            freq (str): 時間頻率，例如 'D'表示天，'W'表示週，'M'表示月
            
        Returns:
            dict: 包含情感趨勢分析的字典
        """
        if df.empty or 'sentiment_label' not in df.columns:
            logger.warning("傳入的資料框為空或缺少情感分析結果，無法進行情感趨勢分析")
            return {"sentiment_trend": {}}
        
        # 確保日期欄位是datetime類型
        if not pd.api.types.is_datetime64_dtype(df['Date']):
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna(subset=['Date'])
        
        # 按時間頻率計算每日平均情感分數
        sentiment_trend = df.groupby(pd.Grouper(key='Date', freq=freq))['sentiment_score'].mean()
        
        # 轉換為字典，將日期格式化為字串
        sentiment_trend_dict = {date.strftime('%Y-%m-%d'): score for date, score in sentiment_trend.items() if not pd.isna(score)}
        
        # 計算最正面和最負面的日期
        if not sentiment_trend.empty:
            most_positive_date = sentiment_trend.idxmax().strftime('%Y-%m-%d')
            most_positive_score = float(sentiment_trend.max())
            most_negative_date = sentiment_trend.idxmin().strftime('%Y-%m-%d')
            most_negative_score = float(sentiment_trend.min())
        else:
            most_positive_date = None
            most_positive_score = 0
            most_negative_date = None
            most_negative_score = 0
        
        # 計算情感趨勢的線性回歸係數 (簡單估計趨勢方向)
        if len(sentiment_trend) > 1:
            x = np.arange(len(sentiment_trend))
            y = sentiment_trend.values
            valid_indices = ~np.isnan(y)
            if np.sum(valid_indices) > 1:
                x_valid = x[valid_indices]
                y_valid = y[valid_indices]
                try:
                    slope = np.polyfit(x_valid, y_valid, 1)[0]
                except:
                    slope = 0
            else:
                slope = 0
        else:
            slope = 0
        
        # 判斷趨勢方向
        if slope > 0.01:
            trend_direction = "上升"
        elif slope < -0.01:
            trend_direction = "下降"
        else:
            trend_direction = "穩定"
        
        result = {
            "sentiment_trend": sentiment_trend_dict,
            "most_positive_date": most_positive_date,
            "most_positive_score": most_positive_score,
            "most_negative_date": most_negative_date,
            "most_negative_score": most_negative_score,
            "trend_slope": float(slope),
            "trend_direction": trend_direction
        }
        
        return result
    
    def analyze_topics(self, df, content_column='Content', title_column='Title', top_n=20):
        """
        簡單的話題分析 (基於詞頻)
        
        Args:
            df (pandas.DataFrame): 包含評論的資料框
            content_column (str): 評論內容欄位名稱
            title_column (str): 評論標題欄位名稱
            top_n (int): 返回前N個熱門詞彙
            
        Returns:
            dict: 包含話題分析結果的字典
        """
        if df.empty:
            logger.warning("傳入的資料框為空，無法進行話題分析")
            return {"top_keywords": {}}
        
        # 結合標題和內容進行分析
        all_texts = []
        
        for _, row in df.iterrows():
            text = ""
            if title_column in df.columns and pd.notna(row[title_column]):
                text += str(row[title_column]) + " "
            
            if content_column in df.columns and pd.notna(row[content_column]):
                text += str(row[content_column])
                
            all_texts.append(text.lower())
        
        # 簡單的詞頻統計
        # 過濾常見的停用詞
        english_stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
                           'when', 'where', 'how', 'to', 'in', 'is', 'it', 'of', 'for', 'with',
                           'this', 'that', 'be', 'on', 'are', 'was', 'were', 'has', 'have',
                           'had', 'not', 'by', 'at', 'from', 'so', 'some', 'other', 'than',
                           'then', 'can', 'could', 'will', 'would', 'my', 'your', 'his', 'her',
                           'their', 'our', 'its', 'i', 'you', 'he', 'she', 'they', 'we', 'who',
                           'whom', 'whose', 'which', 'there', 'here', 'all', 'any', 'each', 'more',
                           'most', 'need', 'im', 'just', 'dont', 'get', 'also', 'ill', 'very'}
        
        # 合併所有文字並分割為詞彙
        all_words = []
        for text in all_texts:
            words = text.split()
            # 過濾停用詞和短詞
            words = [word for word in words if word not in english_stopwords and len(word) > 2]
            all_words.extend(words)
        
        # 計算詞頻
        word_counts = Counter(all_words)
        
        # 取前N個熱門詞彙
        top_keywords = dict(word_counts.most_common(top_n))
        
        result = {
            "top_keywords": top_keywords
        }
        
        return result
    
    def compare_time_periods(self, df1, df2, period1_name="Period 1", period2_name="Period 2"):
        """
        比較兩個時間段的評論數據
        
        Args:
            df1 (pandas.DataFrame): 第一個時間段的資料
            df2 (pandas.DataFrame): 第二個時間段的資料
            period1_name (str): 第一個時間段的名稱
            period2_name (str): 第二個時間段的名稱
            
        Returns:
            dict: 包含兩個時間段比較結果的字典
        """
        # 檢查資料框是否為空
        if df1.empty or df2.empty:
            logger.warning("一個或兩個傳入的資料框為空，無法進行時間段比較")
            return {"comparison_result": "無法比較，資料不足"}
        
        # 檢查情感分析結果是否存在
        if 'sentiment_label' not in df1.columns or 'sentiment_label' not in df2.columns:
            logger.warning("一個或兩個傳入的資料框缺少情感分析結果，無法進行完整比較")
        
        # 1. 評論數量比較
        total_reviews1 = len(df1)
        total_reviews2 = len(df2)
        review_change = (total_reviews2 - total_reviews1) / total_reviews1 if total_reviews1 > 0 else float('inf')
        
        # 計算時間段天數
        if not pd.api.types.is_datetime64_dtype(df1['Date']):
            df1['Date'] = pd.to_datetime(df1['Date'], errors='coerce')
        if not pd.api.types.is_datetime64_dtype(df2['Date']):
            df2['Date'] = pd.to_datetime(df2['Date'], errors='coerce')
            
        days1 = (df1['Date'].max() - df1['Date'].min()).days + 1 if not df1.empty else 0
        days2 = (df2['Date'].max() - df2['Date'].min()).days + 1 if not df2.empty else 0
        
        # 計算每日平均評論數
        daily_avg1 = total_reviews1 / days1 if days1 > 0 else 0
        daily_avg2 = total_reviews2 / days2 if days2 > 0 else 0
        daily_avg_change = (daily_avg2 - daily_avg1) / daily_avg1 if daily_avg1 > 0 else float('inf')
        
        # 2. 評分比較
        avg_rating1 = df1['Rating'].mean() if 'Rating' in df1.columns else 0
        avg_rating2 = df2['Rating'].mean() if 'Rating' in df2.columns else 0
        rating_change = avg_rating2 - avg_rating1
        
        # 3. 情感比較
        if 'sentiment_label' in df1.columns and 'sentiment_label' in df2.columns:
            # 正面評論比例
            positive_ratio1 = df1[df1['sentiment_label'] == 'positive'].shape[0] / total_reviews1 if total_reviews1 > 0 else 0
            positive_ratio2 = df2[df2['sentiment_label'] == 'positive'].shape[0] / total_reviews2 if total_reviews2 > 0 else 0
            positive_ratio_change = positive_ratio2 - positive_ratio1
            
            # 負面評論比例
            negative_ratio1 = df1[df1['sentiment_label'] == 'negative'].shape[0] / total_reviews1 if total_reviews1 > 0 else 0
            negative_ratio2 = df2[df2['sentiment_label'] == 'negative'].shape[0] / total_reviews2 if total_reviews2 > 0 else 0
            negative_ratio_change = negative_ratio2 - negative_ratio1
            
            # 中性評論比例
            neutral_ratio1 = df1[df1['sentiment_label'] == 'neutral'].shape[0] / total_reviews1 if total_reviews1 > 0 else 0
            neutral_ratio2 = df2[df2['sentiment_label'] == 'neutral'].shape[0] / total_reviews2 if total_reviews2 > 0 else 0
            neutral_ratio_change = neutral_ratio2 - neutral_ratio1
            
            # 平均情感分數
            avg_sentiment1 = df1['sentiment_score'].mean() if 'sentiment_score' in df1.columns else 0
            avg_sentiment2 = df2['sentiment_score'].mean() if 'sentiment_score' in df2.columns else 0
            sentiment_change = avg_sentiment2 - avg_sentiment1
        else:
            positive_ratio1 = positive_ratio2 = positive_ratio_change = 0
            negative_ratio1 = negative_ratio2 = negative_ratio_change = 0
            neutral_ratio1 = neutral_ratio2 = neutral_ratio_change = 0
            avg_sentiment1 = avg_sentiment2 = sentiment_change = 0
        
        # 4. 版本比較
        if 'Version' in df1.columns and 'Version' in df2.columns:
            version1_counts = df1['Version'].value_counts().to_dict()
            version2_counts = df2['Version'].value_counts().to_dict()
            
            # 找出主要版本
            main_version1 = max(version1_counts.items(), key=lambda x: x[1])[0] if version1_counts else None
            main_version2 = max(version2_counts.items(), key=lambda x: x[1])[0] if version2_counts else None
            
            version_changed = main_version1 != main_version2
        else:
            main_version1 = main_version2 = None
            version_changed = False
        
        # 建立比較結果
        comparison = {
            "time_periods": {
                period1_name: {
                    "start_date": df1['Date'].min().strftime('%Y-%m-%d') if not df1.empty else None,
                    "end_date": df1['Date'].max().strftime('%Y-%m-%d') if not df1.empty else None,
                    "days": days1
                },
                period2_name: {
                    "start_date": df2['Date'].min().strftime('%Y-%m-%d') if not df2.empty else None,
                    "end_date": df2['Date'].max().strftime('%Y-%m-%d') if not df2.empty else None,
                    "days": days2
                }
            },
            "review_volume": {
                period1_name: {
                    "total_reviews": total_reviews1,
                    "daily_average": round(daily_avg1, 2)
                },
                period2_name: {
                    "total_reviews": total_reviews2,
                    "daily_average": round(daily_avg2, 2)
                },
                "change": {
                    "total_reviews_percent": round(review_change * 100, 2),
                    "daily_average_percent": round(daily_avg_change * 100, 2)
                }
            },
            "rating": {
                period1_name: {
                    "average_rating": round(avg_rating1, 2)
                },
                period2_name: {
                    "average_rating": round(avg_rating2, 2)
                },
                "change": {
                    "average_rating": round(rating_change, 2)
                }
            },
            "sentiment": {
                period1_name: {
                    "positive_ratio": round(positive_ratio1 * 100, 2),
                    "negative_ratio": round(negative_ratio1 * 100, 2),
                    "neutral_ratio": round(neutral_ratio1 * 100, 2),
                    "average_sentiment_score": round(avg_sentiment1, 4)
                },
                period2_name: {
                    "positive_ratio": round(positive_ratio2 * 100, 2),
                    "negative_ratio": round(negative_ratio2 * 100, 2),
                    "neutral_ratio": round(neutral_ratio2 * 100, 2),
                    "average_sentiment_score": round(avg_sentiment2, 4)
                },
                "change": {
                    "positive_ratio_points": round(positive_ratio_change * 100, 2),
                    "negative_ratio_points": round(negative_ratio_change * 100, 2),
                    "neutral_ratio_points": round(neutral_ratio_change * 100, 2),
                    "average_sentiment_score": round(sentiment_change, 4)
                }
            },
            "version": {
                period1_name: {
                    "main_version": main_version1
                },
                period2_name: {
                    "main_version": main_version2
                },
                "version_changed": version_changed
            }
        }
        
        # 5. 提供摘要判斷
        summary = []
        
        # 評論量變化
        if review_change > 0.2:
            summary.append(f"評論數量大幅增加 ({round(review_change * 100, 1)}%)")
        elif review_change < -0.2:
            summary.append(f"評論數量大幅減少 ({round(review_change * 100, 1)}%)")
        
        # 評分變化
        if rating_change > 0.5:
            summary.append(f"評分明顯提高 (+{round(rating_change, 1)})")
        elif rating_change < -0.5:
            summary.append(f"評分明顯降低 ({round(rating_change, 1)})")
        
        # 情感變化
        if sentiment_change > 0.2:
            summary.append("玩家情感顯著轉為正面")
        elif sentiment_change < -0.2:
            summary.append("玩家情感顯著轉為負面")
        
        # 版本變化
        if version_changed:
            summary.append(f"遊戲版本從 {main_version1} 更新到 {main_version2}")
        
        # 如果沒有明顯變化
        if not summary:
            summary.append("兩個時期之間沒有顯著差異")
        
        comparison["summary"] = summary
        
        # 6. 新增：提供詳細深入分析和趨勢判斷
        detailed_insights = []
        
        # 評論量分析深入解釋
        if review_change > 0.2:
            if review_change > 0.5:
                detailed_insights.append(f"評論數量暴增 ({round(review_change * 100, 1)}%)，表明遊戲熱度大幅提升，可能是因為新活動、新功能推出或營銷活動效果顯著。")
            else:
                detailed_insights.append(f"評論數量明顯增加 ({round(review_change * 100, 1)}%)，反映玩家參與度提高，遊戲正受到更多關注。")
        elif review_change < -0.2:
            if review_change < -0.5:
                detailed_insights.append(f"評論數量大幅減少 ({round(abs(review_change) * 100, 1)}%)，可能是遊戲熱度下降、玩家流失嚴重，或缺乏吸引玩家討論的更新內容。")
            else:
                detailed_insights.append(f"評論數量有所下降 ({round(abs(review_change) * 100, 1)}%)，可能表示玩家活躍度略有下降，應關注玩家參與度。")
        
        # 評分與情感綜合分析
        if rating_change > 0.3 and sentiment_change > 0.15:
            detailed_insights.append(f"評分和情感同時提升，證實玩家滿意度確實增加，這種一致的正向變化表明遊戲品質確實得到改善。")
        elif rating_change < -0.3 and sentiment_change < -0.15:
            detailed_insights.append(f"評分和情感同時下降，確認玩家滿意度明顯降低，需要深入分析問題根源並及時採取改進措施。")
        elif rating_change > 0.3 and sentiment_change < -0.15:
            detailed_insights.append(f"評分提高但情感評價下降，這種不一致情況值得關注，可能是因為高評分玩家更願意留下評價，但評論內容仍反映了某些負面問題。")
        elif rating_change < -0.3 and sentiment_change > 0.15:
            detailed_insights.append(f"評分下降但情感評價提高，這種矛盾現象可能反映玩家對遊戲有較高期望，儘管評論內容變得更加正向。")
        
        # 情感分佈分析
        if abs(neutral_ratio_change) > 0.15:
            if neutral_ratio_change > 0:
                detailed_insights.append(f"中立評論比例增加 ({round(neutral_ratio_change * 100, 1)} 個百分點)，表明更多玩家持觀望態度，可能對遊戲既有喜愛的方面也有不滿之處。")
            else:
                detailed_insights.append(f"中立評論比例減少 ({round(abs(neutral_ratio_change) * 100, 1)} 個百分點)，玩家觀點更為明確，情感兩極化趨勢增強。")
        
        if positive_ratio_change > 0.15 and negative_ratio_change < -0.15:
            detailed_insights.append(f"正面評論增加同時負面評論減少，是理想的變化趨勢，表明遊戲體驗全面提升，玩家群體滿意度顯著提高。")
        elif positive_ratio_change < -0.15 and negative_ratio_change > 0.15:
            detailed_insights.append(f"正面評論減少同時負面評論增加，是警訊，表明遊戲體驗可能出現多方面問題，需要全面檢視並改進。")
        
        # 版本變更分析
        if version_changed:
            if rating_change > 0.3:
                detailed_insights.append(f"從 {main_version1} 到 {main_version2} 的版本更新獲得了積極評價，評分提高了 {rating_change:.2f} 分，新版本可能修復了關鍵問題或增加了受歡迎功能。")
            elif rating_change < -0.3:
                detailed_insights.append(f"從 {main_version1} 到 {main_version2} 的版本更新反響不佳，評分下降了 {abs(rating_change):.2f} 分，新版本可能引入了問題或移除了玩家喜愛的功能。")
            else:
                detailed_insights.append(f"版本從 {main_version1} 更新到 {main_version2}，但玩家評價變化不大，可能是小幅更新或改進不夠明顯。")
        
        # 評論量與評價質量關係
        if review_change > 0.2 and rating_change > 0.3:
            detailed_insights.append("評論數量和評分同時上升，顯示遊戲正處於正向循環中，玩家增加且滿意度高。")
        elif review_change < -0.2 and rating_change < -0.3:
            detailed_insights.append("評論數量和評分同時下降，可能表明核心玩家也在流失，情況較為嚴重。")
        elif review_change > 0.2 and rating_change < -0.3:
            detailed_insights.append("評論數量上升但評分下降，可能是遊戲曝光增加但新玩家體驗不佳，或有爭議性更新引發大量負面討論。")
        
        # 情感趨勢分析
        sentiment_trend1 = self.analyze_sentiment_trend(df1)
        sentiment_trend2 = self.analyze_sentiment_trend(df2)
        
        trend_direction1 = sentiment_trend1["trend_direction"]
        trend_direction2 = sentiment_trend2["trend_direction"]
        
        if trend_direction1 != trend_direction2:
            if trend_direction1 == "下降" and trend_direction2 == "上升":
                detailed_insights.append(f"情感趨勢從「下降」轉為「上升」，表明玩家滿意度正在恢復，先前的問題可能已得到解決。")
            elif trend_direction1 == "上升" and trend_direction2 == "下降":
                detailed_insights.append(f"情感趨勢從「上升」轉為「下降」，表明最近的變化可能引起了玩家不滿，應密切關注並及時回應。")
            elif trend_direction1 == "穩定" and trend_direction2 == "上升":
                detailed_insights.append(f"情感趨勢從「穩定」轉為「上升」，顯示遊戲體驗正在改善，玩家滿意度增加。")
            elif trend_direction1 == "穩定" and trend_direction2 == "下降":
                detailed_insights.append(f"情感趨勢從「穩定」轉為「下降」，可能暗示遊戲體驗變差，需要找出問題並調整。")
        elif trend_direction1 == trend_direction2:
            if trend_direction1 == "上升":
                detailed_insights.append(f"情感持續「上升」趨勢，表明遊戲持續獲得玩家好評，應維持現有策略。")
            elif trend_direction1 == "下降":
                detailed_insights.append(f"情感持續「下降」趨勢，表明問題可能尚未得到有效解決，需要更深入的調查和更積極的改進措施。")
        
        # 沒有明顯變化時的深入分析
        if not summary or (len(summary) == 1 and summary[0] == "兩個時期之間沒有顯著差異"):
            if total_reviews1 > 100 and total_reviews2 > 100:  # 確保有足夠樣本
                detailed_insights.append("數據穩定性高，遊戲體驗始終如一，這可能是積極信號（玩家持續滿意）或消極信號（缺乏創新導致體驗單調）。")
                
                if avg_rating1 >= 4.0 and avg_rating2 >= 4.0:
                    detailed_insights.append("評分持續保持在高水平（4分以上），表明玩家總體滿意度高，遊戲核心體驗良好。")
                elif avg_rating1 <= 3.0 and avg_rating2 <= 3.0:
                    detailed_insights.append("評分持續處於較低水平（3分以下），表明存在長期未解決的問題，建議全面檢視遊戲設計和服務質量。")
        
        # 確保至少有一些見解
        if not detailed_insights:
            detailed_insights.append("當前數據顯示變化不明顯，建議持續監測並收集更多數據以識別潛在趨勢。")
        
        # 添加到比較結果中
        comparison["detailed_insights"] = detailed_insights
        
        return comparison