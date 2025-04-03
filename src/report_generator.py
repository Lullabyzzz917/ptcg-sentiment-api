"""
報告生成模組 - 負責根據分析結果生成比較報告
"""
import json
import pandas as pd
import logging
from datetime import datetime
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.font_manager import FontProperties
import numpy as np
import re

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReportGenerator:
    """生成玩家輿情比較報告"""
    
    def __init__(self, output_dir='reports'):
        """
        初始化報告生成器
        
        Args:
            output_dir (str): 報告輸出目錄
        """
        self.output_dir = output_dir
        
        os.makedirs(output_dir, exist_ok=True)
        
        plt.style.use('ggplot')
        matplotlib.rcParams['figure.figsize'] = (10, 6)
        matplotlib.rcParams['figure.dpi'] = 100
        
        self.set_chinese_font()
        
    def set_chinese_font(self):
        """設定適合不同作業系統的中文字體"""
        matplotlib.rcParams['axes.unicode_minus'] = False
        
        font_found = False
        
        import platform
        system = platform.system()
        
        if system == 'Windows':
            font_list = ['Microsoft YaHei', 'SimHei', 'SimSun']
        elif system == 'Darwin':
            font_list = ['PingFang SC', 'Hiragino Sans GB', 'Heiti SC']
        else:
            font_list = ['WenQuanYi Zen Hei', 'Droid Sans Fallback', 'Noto Sans CJK TC']
        
        additional_fonts = ['Arial Unicode MS', 'DejaVu Sans']
        font_list.extend(additional_fonts)
        
        from matplotlib.font_manager import findfont, FontProperties
        
        for font_name in font_list:
            try:
                if findfont(FontProperties(family=font_name)) is not None:
                    matplotlib.rcParams['font.family'] = ['sans-serif']
                    matplotlib.rcParams['font.sans-serif'] = [font_name] + matplotlib.rcParams['font.sans-serif']
                    logger.info(f"找到並設定中文字體: {font_name}")
                    font_found = True
                    break
            except:
                continue
        
        if not font_found:
            logger.warning("找不到合適的中文字體，將使用預設字體，中文可能無法正確顯示")
            matplotlib.rcParams['font.family'] = ['sans-serif']
        
        plt.rcParams.update(matplotlib.rcParams)
    
    def _generate_filename(self, comparison_result, period1_name, period2_name, extension, description=''):
        """
        生成簡潔的檔案名稱，包含月日時分的時間戳記
        
        Args:
            comparison_result (dict): 比較結果，包含時間段資訊
            period1_name (str): 第一個時間段名稱
            period2_name (str): 第二個時間段名稱
            extension (str): 檔案副檔名，如 'html', 'json', 'txt', 'png'
            description (str, optional): 檔案描述，例如 '評分圖'
            
        Returns:
            str: 格式化的檔案名稱
        """
        # 取得時間段資訊
        p1_info = comparison_result["time_periods"][period1_name]
        p2_info = comparison_result["time_periods"][period2_name]
        
        # 簡化時間段名稱
        def simplify_name(name):
            if len(name) >= 2:
                short_name = name[:2]
            else:
                short_name = name
            return re.sub(r'[\\/*?:"<>|]', '', short_name)
        
        p1_short = simplify_name(period1_name)
        p2_short = simplify_name(period2_name)
        
        # 簡化日期格式 (YYYY-MM-DD -> MMDD)
        def simplify_date(date_str):
            if date_str and len(date_str) >= 10:
                return date_str[5:7] + date_str[8:10]
            return date_str
        
        p1_start = simplify_date(p1_info['start_date'])
        p1_end = simplify_date(p1_info['end_date'])
        p2_start = simplify_date(p2_info['start_date'])
        p2_end = simplify_date(p2_info['end_date'])
        
        # 生成日期時間標記 (月日時分)：MMDDHHMM
        now = datetime.now().strftime('%m%d%H%M')
        
        # 確定檔案類型簡稱
        type_abbr = {
            'html': 'HTML',
            'json': 'JSON',
            'txt': 'TXT',
            'png': 'IMG'
        }.get(extension.lower(), extension.upper())
        
        # 針對圖片進行特殊處理
        if extension.lower() == 'png':
            if '評分' in description:
                type_abbr = '評分圖'
            elif '情感' in description:
                type_abbr = '情感圖'
            elif '趨勢' in description or '每日' in description:
                type_abbr = '趨勢圖'
            else:
                type_abbr = '圖表'
        
        # 構建精簡的檔案名稱
        filename = f"PTCG_{p1_short}{p1_start}-{p1_end}_vs_{p2_short}{p2_start}-{p2_end}_{type_abbr}_{now}.{extension}"
        
        return filename
    
    def generate_json_report(self, comparison_result, period1_name, period2_name, filename=None):
        """
        生成JSON格式的報告
        
        Args:
            comparison_result (dict): 比較結果
            period1_name (str): 第一個時間段名稱
            period2_name (str): 第二個時間段名稱
            filename (str, optional): 輸出檔案名稱，如果未提供則自動生成
            
        Returns:
            str: 報告檔案路徑
        """
        # 如果沒有提供檔案名稱，自動生成一個
        if filename is None:
            filename = self._generate_filename(comparison_result, period1_name, period2_name, 'json', 'JSON報告')
        
        # 確保檔案名稱有.json副檔名
        if not filename.endswith('.json'):
            filename += '.json'
        
        # 完整檔案路徑
        file_path = os.path.join(self.output_dir, filename)
        
        # 建立報告內容
        report = {
            "title": f"PTCG Pocket 玩家輿情比較報告：{period1_name} vs {period2_name}",
            "generated_at": datetime.now().isoformat(),
            "comparison_result": comparison_result
        }
        
        # 寫入JSON檔案
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"JSON報告已生成：{file_path}")
            return file_path
        except Exception as e:
            logger.error(f"生成JSON報告時發生錯誤：{str(e)}")
            raise
    
    def generate_text_report(self, comparison_result, period1_name, period2_name, filename=None):
        """
        生成文字格式的報告
        
        Args:
            comparison_result (dict): 比較結果
            period1_name (str): 第一個時間段名稱
            period2_name (str): 第二個時間段名稱
            filename (str, optional): 輸出檔案名稱，如果未提供則自動生成
            
        Returns:
            str: 報告檔案路徑
        """
        # 如果沒有提供檔案名稱，自動生成一個
        if filename is None:
            filename = self._generate_filename(comparison_result, period1_name, period2_name, 'txt', '文字報告')
        
        # 確保檔案名稱有.txt副檔名
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        # 完整檔案路徑
        file_path = os.path.join(self.output_dir, filename)
        
        # 建立報告內容
        lines = []
        lines.append("="*80)
        lines.append(f"PTCG Pocket 玩家輿情比較報告：{period1_name} vs {period2_name}")
        lines.append(f"生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("="*80)
        lines.append("")
        
        # 時間段資訊
        lines.append("1. 時間段資訊")
        lines.append("-"*80)
        p1_info = comparison_result["time_periods"][period1_name]
        p2_info = comparison_result["time_periods"][period2_name]
        lines.append(f"{period1_name}：{p1_info['start_date']} 至 {p1_info['end_date']} ({p1_info['days']} 天)")
        lines.append(f"{period2_name}：{p2_info['start_date']} 至 {p2_info['end_date']} ({p2_info['days']} 天)")
        lines.append("")
        
        # 評論數量與頻率
        lines.append("2. 評論數量與頻率變化")
        lines.append("-"*80)
        review_vol = comparison_result["review_volume"]
        p1_rev = review_vol[period1_name]
        p2_rev = review_vol[period2_name]
        change = review_vol["change"]
        
        lines.append(f"{period1_name}：共 {p1_rev['total_reviews']} 則評論，平均每日 {p1_rev['daily_average']} 則")
        lines.append(f"{period2_name}：共 {p2_rev['total_reviews']} 則評論，平均每日 {p2_rev['daily_average']} 則")
        
        if change["total_reviews_percent"] > 0:
            lines.append(f"評論總數變化：增加 {change['total_reviews_percent']}%")
        else:
            lines.append(f"評論總數變化：減少 {abs(change['total_reviews_percent'])}%")
            
        if change["daily_average_percent"] > 0:
            lines.append(f"每日平均評論數變化：增加 {change['daily_average_percent']}%")
        else:
            lines.append(f"每日平均評論數變化：減少 {abs(change['daily_average_percent'])}%")
        lines.append("")
        
        # 評分變化
        lines.append("3. 評分變化")
        lines.append("-"*80)
        rating = comparison_result["rating"]
        p1_rating = rating[period1_name]
        p2_rating = rating[period2_name]
        rating_change = rating["change"]
        
        lines.append(f"{period1_name}：平均評分 {p1_rating['average_rating']}")
        lines.append(f"{period2_name}：平均評分 {p2_rating['average_rating']}")
        
        if rating_change["average_rating"] > 0:
            lines.append(f"評分變化：上升 {rating_change['average_rating']} 分")
        else:
            lines.append(f"評分變化：下降 {abs(rating_change['average_rating'])} 分")
        lines.append("")
        
        # 情感分析
        lines.append("4. 評論情感分析")
        lines.append("-"*80)
        sentiment = comparison_result["sentiment"]
        p1_sent = sentiment[period1_name]
        p2_sent = sentiment[period2_name]
        sent_change = sentiment["change"]
        
        lines.append(f"{period1_name}：")
        lines.append(f"  - 正面評論佔比：{p1_sent['positive_ratio']}%")
        lines.append(f"  - 負面評論佔比：{p1_sent['negative_ratio']}%")
        lines.append(f"  - 中立評論佔比：{p1_sent['neutral_ratio']}%")
        lines.append(f"  - 平均情感分數：{p1_sent['average_sentiment_score']}")
        
        lines.append(f"{period2_name}：")
        lines.append(f"  - 正面評論佔比：{p2_sent['positive_ratio']}%")
        lines.append(f"  - 負面評論佔比：{p2_sent['negative_ratio']}%")
        lines.append(f"  - 中立評論佔比：{p2_sent['neutral_ratio']}%")
        lines.append(f"  - 平均情感分數：{p2_sent['average_sentiment_score']}")
        
        lines.append("情感變化：")
        if sent_change["positive_ratio_points"] > 0:
            lines.append(f"  - 正面評論佔比：增加 {sent_change['positive_ratio_points']} 個百分點")
        else:
            lines.append(f"  - 正面評論佔比：減少 {abs(sent_change['positive_ratio_points'])} 個百分點")
            
        if sent_change["negative_ratio_points"] > 0:
            lines.append(f"  - 負面評論佔比：增加 {sent_change['negative_ratio_points']} 個百分點")
        else:
            lines.append(f"  - 負面評論佔比：減少 {abs(sent_change['negative_ratio_points'])} 個百分點")
            
        if sent_change["neutral_ratio_points"] > 0:
            lines.append(f"  - 中立評論佔比：增加 {sent_change['neutral_ratio_points']} 個百分點")
        else:
            lines.append(f"  - 中立評論佔比：減少 {abs(sent_change['neutral_ratio_points'])} 個百分點")
            
        if sent_change["average_sentiment_score"] > 0:
            lines.append(f"  - 平均情感分數：上升 {sent_change['average_sentiment_score']}")
        else:
            lines.append(f"  - 平均情感分數：下降 {abs(sent_change['average_sentiment_score'])}")
        lines.append("")
        
        # 遊戲版本
        lines.append("5. 遊戲版本")
        lines.append("-"*80)
        version = comparison_result["version"]
        p1_ver = version[period1_name]
        p2_ver = version[period2_name]
        
        lines.append(f"{period1_name} 主要版本：{p1_ver['main_version']}")
        lines.append(f"{period2_name} 主要版本：{p2_ver['main_version']}")
        
        if version["version_changed"]:
            lines.append(f"版本已更新：從 {p1_ver['main_version']} 到 {p2_ver['main_version']}")
        else:
            lines.append("版本未變更")
        lines.append("")
        
        # 摘要判斷
        lines.append("6. 摘要判斷")
        lines.append("-"*80)
        for point in comparison_result["summary"]:
            lines.append(f"- {point}")
        lines.append("")
        
        # 詳細分析與趨勢判斷
        lines.append("7. 深入分析與影響因素")
        lines.append("-"*80)
        if "detailed_insights" in comparison_result:
            for insight in comparison_result["detailed_insights"]:
                lines.append(f"- {insight}")
        else:
            lines.append("- 暫無詳細分析資料")
        lines.append("")
        
        # 寫入檔案
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            logger.info(f"文字報告已生成：{file_path}")
            return file_path
        except Exception as e:
            logger.error(f"生成文字報告時發生錯誤：{str(e)}")
            raise
    
    def generate_charts(self, df1, df2, period1_name, period2_name, comparison_result, output_prefix=None):
        """
        生成視覺化圖表，加強圖表生成的穩定性
        
        Args:
            df1 (pandas.DataFrame): 第一個時間段的資料
            df2 (pandas.DataFrame): 第二個時間段的資料
            period1_name (str): 第一個時間段名稱
            period2_name (str): 第二個時間段名稱
            comparison_result (dict): 比較結果，用於生成文件名
            output_prefix (str, optional): 輸出檔案名稱前綴
            
        Returns:
            list: 生成的圖表檔案路徑列表
        """
        if output_prefix is None:
            pass
        
        chart_files = []
        
        # 記錄與處理異常
        def safe_save_figure(file_path, fig=None):
            try:
                if fig is None:
                    plt.savefig(file_path, dpi=100, bbox_inches='tight')
                else:
                    fig.savefig(file_path, dpi=100, bbox_inches='tight')
                logger.info(f"成功保存圖表: {file_path}")
                return file_path
            except Exception as e:
                logger.error(f"保存圖表時發生錯誤 {file_path}: {str(e)}")
                try:
                    plt.figure(figsize=(10, 6))
                    plt.text(0.5, 0.5, "圖表生成失敗", 
                            horizontalalignment='center', 
                            verticalalignment='center',
                            fontsize=20)
                    plt.tight_layout()
                    plt.savefig(file_path, dpi=100)
                    plt.close()
                    logger.info(f"已生成替代圖表: {file_path}")
                    return file_path
                except Exception as e2:
                    logger.error(f"生成替代圖表也失敗: {str(e2)}")
                    return None
        
        # 確保DataFrame非空
        if df1.empty or df2.empty:
            logger.warning("一個或兩個資料框為空，無法生成比較圖表")
            # 生成空圖表
            for chart_type in ['rating_distribution', 'sentiment_distribution', 'daily_review_trend']:
                plt.figure(figsize=(10, 6))
                plt.text(0.5, 0.5, f"無法生成{chart_type}圖表 - 資料不足", 
                        horizontalalignment='center', 
                        verticalalignment='center',
                        fontsize=20)
                chart_path = os.path.join(self.output_dir, 
                                          self._generate_filename(comparison_result, period1_name, period2_name, 'png', f"{chart_type}圖表"))
                plt.savefig(chart_path, dpi=100)
                plt.close()
                chart_files.append(chart_path)
            return chart_files
        
        try:
            # 1. 評分分佈比較圖
            plt.figure(figsize=(10, 6))
            
            # 計算每個評分的百分比
            try:
                rating_counts1 = df1['Rating'].value_counts().sort_index()
                rating_counts2 = df2['Rating'].value_counts().sort_index()
                
                rating_pcts1 = (rating_counts1 / rating_counts1.sum() * 100).to_dict()
                rating_pcts2 = (rating_counts2 / rating_counts2.sum() * 100).to_dict()
                
                # 確保所有評分值都存在
                all_ratings = sorted(set(list(rating_pcts1.keys()) + list(rating_pcts2.keys())))
                
                # 準備繪圖資料
                rating_values = []
                p1_pcts = []
                p2_pcts = []
                
                for rating in all_ratings:
                    rating_values.append(rating)
                    p1_pcts.append(rating_pcts1.get(rating, 0))
                    p2_pcts.append(rating_pcts2.get(rating, 0))
                
                x = range(len(rating_values))
                width = 0.35
                
                # 繪製長條圖
                bar1 = plt.bar([i - width/2 for i in x], p1_pcts, width, label=period1_name, color='#3498db')
                bar2 = plt.bar([i + width/2 for i in x], p2_pcts, width, label=period2_name, color='#f39c12')
                
                # 設定標籤和標題
                plt.xlabel('評分', fontsize=14)
                plt.ylabel('百分比 (%)', fontsize=14)
                plt.title('評分分佈比較', fontsize=16, fontweight='bold')
                plt.xticks(x, rating_values, fontsize=12)
                plt.yticks(fontsize=12)
                
                # 設定圖例
                plt.legend(fontsize=12)
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                
                # 儲存圖表
                rating_chart_path = os.path.join(self.output_dir, 
                                               self._generate_filename(comparison_result, period1_name, period2_name, 'png', "評分分佈圖"))
                rating_chart_path = safe_save_figure(rating_chart_path)
                if rating_chart_path:
                    chart_files.append(rating_chart_path)
            except Exception as e:
                logger.error(f"生成評分分佈圖時發生錯誤: {str(e)}")
                # 創建一個錯誤提示圖
                plt.figure(figsize=(10, 6))
                plt.text(0.5, 0.5, "評分分佈圖生成失敗", 
                        horizontalalignment='center', 
                        verticalalignment='center',
                        fontsize=20)
                rating_chart_path = os.path.join(self.output_dir, 
                                               self._generate_filename(comparison_result, period1_name, period2_name, 'png', "評分分佈圖_錯誤"))
                plt.savefig(rating_chart_path, dpi=100)
                chart_files.append(rating_chart_path)
            finally:
                plt.close()
            
            # 2. 情感分佈比較圖
            if 'sentiment_label' in df1.columns and 'sentiment_label' in df2.columns:
                plt.figure(figsize=(10, 6))
                
                try:
                    # 計算情感分佈
                    sentiment_counts1 = df1['sentiment_label'].value_counts()
                    sentiment_counts2 = df2['sentiment_label'].value_counts()
                    
                    sentiment_pcts1 = (sentiment_counts1 / sentiment_counts1.sum() * 100).to_dict()
                    sentiment_pcts2 = (sentiment_counts2 / sentiment_counts2.sum() * 100).to_dict()
                    
                    # 確保所有情感標籤都存在
                    all_sentiments = ['positive', 'neutral', 'negative']
                    sentiment_labels = ['正面', '中立', '負面']
                    
                    # 準備繪圖資料
                    p1_sentiment_pcts = [sentiment_pcts1.get(s, 0) for s in all_sentiments]
                    p2_sentiment_pcts = [sentiment_pcts2.get(s, 0) for s in all_sentiments]
                    
                    x = range(len(all_sentiments))
                    width = 0.35
                    
                    # 繪製長條圖，設定顏色
                    bar1 = plt.bar([i - width/2 for i in x], p1_sentiment_pcts, width, label=period1_name, color='#3498db')
                    bar2 = plt.bar([i + width/2 for i in x], p2_sentiment_pcts, width, label=period2_name, color='#f39c12')
                    
                    # 設定標籤和標題
                    plt.xlabel('情感類別', fontsize=14)
                    plt.ylabel('百分比 (%)', fontsize=14)
                    plt.title('情感分佈比較', fontsize=16, fontweight='bold')
                    plt.xticks(x, sentiment_labels, fontsize=12)
                    plt.yticks(fontsize=12)
                    
                    # 設定圖例和網格
                    plt.legend(fontsize=12)
                    plt.grid(axis='y', linestyle='--', alpha=0.7)
                    
                    # 儲存圖表
                    sentiment_chart_path = os.path.join(self.output_dir, 
                                                      self._generate_filename(comparison_result, period1_name, period2_name, 'png', "情感分佈圖"))
                    sentiment_chart_path = safe_save_figure(sentiment_chart_path)
                    if sentiment_chart_path:
                        chart_files.append(sentiment_chart_path)
                except Exception as e:
                    logger.error(f"生成情感分佈圖時發生錯誤: {str(e)}")
                    # 創建一個錯誤提示圖
                    plt.figure(figsize=(10, 6))
                    plt.text(0.5, 0.5, "情感分佈圖生成失敗", 
                            horizontalalignment='center', 
                            verticalalignment='center',
                            fontsize=20)
                    sentiment_chart_path = os.path.join(self.output_dir, 
                                                      self._generate_filename(comparison_result, period1_name, period2_name, 'png', "情感分佈圖_錯誤"))
                    plt.savefig(sentiment_chart_path, dpi=100)
                    chart_files.append(sentiment_chart_path)
                finally:
                    plt.close()
            
            # 3. 每日評論數量趨勢圖
            if len(df1) > 0 and len(df2) > 0:
                plt.figure(figsize=(12, 6))
                
                try:
                    # 確保日期欄位是datetime類型
                    if not pd.api.types.is_datetime64_dtype(df1['Date']):
                        df1['Date'] = pd.to_datetime(df1['Date'])
                    if not pd.api.types.is_datetime64_dtype(df2['Date']):
                        df2['Date'] = pd.to_datetime(df2['Date'])
                    
                    # 計算每日評論數
                    daily_counts1 = df1.groupby(df1['Date'].dt.date).size()
                    daily_counts2 = df2.groupby(df2['Date'].dt.date).size()
                    
                    # 繪製趨勢線
                    plt.plot(daily_counts1.index, daily_counts1.values, 'o-', color='#3498db', linewidth=2, 
                            label=f"{period1_name} 每日評論數", markersize=5)
                    plt.plot(daily_counts2.index, daily_counts2.values, 'o-', color='#f39c12', linewidth=2, 
                            label=f"{period2_name} 每日評論數", markersize=5)
                    
                    # 設定標籤和標題
                    plt.xlabel('日期', fontsize=14)
                    plt.ylabel('評論數量', fontsize=14)
                    plt.title('每日評論數量趨勢', fontsize=16, fontweight='bold')
                    
                    # 設定圖例和網格
                    plt.legend(fontsize=12)
                    plt.grid(True, linestyle='--', alpha=0.7)
                    
                    # 設定x軸日期格式
                    plt.gcf().autofmt_xdate()  # 自動格式化日期標籤
                    plt.xticks(fontsize=12)
                    plt.yticks(fontsize=12)
                    
                    plt.tight_layout()
                    
                    # 儲存圖表
                    trend_chart_path = os.path.join(self.output_dir, 
                                                  self._generate_filename(comparison_result, period1_name, period2_name, 'png', "每日評論趨勢圖"))
                    trend_chart_path = safe_save_figure(trend_chart_path)
                    if trend_chart_path:
                        chart_files.append(trend_chart_path)
                except Exception as e:
                    logger.error(f"生成每日評論趨勢圖時發生錯誤: {str(e)}")
                    # 創建一個錯誤提示圖
                    plt.figure(figsize=(10, 6))
                    plt.text(0.5, 0.5, "每日評論趨勢圖生成失敗", 
                            horizontalalignment='center', 
                            verticalalignment='center',
                            fontsize=20)
                    trend_chart_path = os.path.join(self.output_dir, 
                                                  self._generate_filename(comparison_result, period1_name, period2_name, 'png', "每日評論趨勢圖_錯誤"))
                    plt.savefig(trend_chart_path, dpi=100)
                    chart_files.append(trend_chart_path)
                finally:
                    plt.close()
        
        except Exception as e:
            logger.error(f"圖表生成過程中發生未捕獲錯誤: {str(e)}")
        
        return chart_files
    
    def generate_html_report(self, comparison_result, df1, df2, period1_name, period2_name, filename=None):
        """
        生成HTML格式的報告
        
        Args:
            comparison_result (dict): 比較結果
            df1 (pandas.DataFrame): 第一個時間段的資料
            df2 (pandas.DataFrame): 第二個時間段的資料
            period1_name (str): 第一個時間段名稱
            period2_name (str): 第二個時間段名稱
            filename (str, optional): 輸出檔案名稱，如果未提供則自動生成
            
        Returns:
            str: 報告檔案路徑
        """
        # 如果沒有提供檔案名稱，自動生成一個
        if filename is None:
            filename = self._generate_filename(comparison_result, period1_name, period2_name, 'html', 'HTML報告')
        
        # 確保檔案名稱有.html副檔名
        if not filename.endswith('.html'):
            filename += '.html'
        
        # 完整檔案路徑
        file_path = os.path.join(self.output_dir, filename)
        
        # 先確保中文字體設定
        logger.info("正在生成視覺化圖表...")
        
        # 生成圖表
        chart_files = self.generate_charts(df1, df2, period1_name, period2_name, comparison_result)
        
        # 準備圖表相對路徑（確保相對路徑正確）
        chart_rel_paths = []
        for chart_file in chart_files:
            if chart_file is not None:
                chart_rel_paths.append(os.path.basename(chart_file))
        
        # 確保有足夠的圖表相對路徑，如果不夠則添加空字符串
        while len(chart_rel_paths) < 3:
            chart_rel_paths.append('')
        
        # 建立HTML內容
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-TW">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>PTCG Pocket 玩家輿情比較報告</title>
            <style>
                body {{
                    font-family: Arial, 'Microsoft JhengHei', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                }}
                h1 {{
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    border-bottom: 1px solid #bdc3c7;
                    padding-bottom: 5px;
                    margin-top: 30px;
                }}
                .header {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .summary {{
                    background-color: #e8f4f8;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .chart-container {{
                    margin: 30px 0;
                    text-align: center;
                }}
                .chart {{
                    max-width: 100%;
                    height: auto;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    border-radius: 5px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px 15px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
                .positive {{
                    color: #27ae60;
                }}
                .negative {{
                    color: #e74c3c;
                }}
                .neutral {{
                    color: #7f8c8d;
                }}
                .bg-yellow-50 {{
                    background-color: #fefce8;
                }}
                .border-yellow-500 {{
                    border-color: #eab308;
                }}
                .border-l-4 {{
                    border-left-width: 4px;
                    border-left-style: solid;
                }}
                .text-gray-700 {{
                    color: #374151;
                }}
                .missing-chart {{
                    padding: 40px;
                    background-color: #f8f9fa;
                    border: 1px dashed #ccc;
                    border-radius: 5px;
                    text-align: center;
                    color: #666;
                    font-style: italic;
                }}
                footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    text-align: center;
                    font-size: 0.9em;
                    color: #7f8c8d;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>PTCG Pocket 玩家輿情比較報告</h1>
                <p>報告生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <h2>1. 時間段資訊</h2>
            <table>
                <tr>
                    <th>時間段</th>
                    <th>開始日期</th>
                    <th>結束日期</th>
                    <th>天數</th>
                </tr>
                <tr>
                    <td>{period1_name}</td>
                    <td>{comparison_result["time_periods"][period1_name]["start_date"]}</td>
                    <td>{comparison_result["time_periods"][period1_name]["end_date"]}</td>
                    <td>{comparison_result["time_periods"][period1_name]["days"]}</td>
                </tr>
                <tr>
                    <td>{period2_name}</td>
                    <td>{comparison_result["time_periods"][period2_name]["start_date"]}</td>
                    <td>{comparison_result["time_periods"][period2_name]["end_date"]}</td>
                    <td>{comparison_result["time_periods"][period2_name]["days"]}</td>
                </tr>
            </table>
            
            <div class="summary">
                <h3>摘要判斷</h3>
                <ul>
                    {"".join([f"<li>{point}</li>" for point in comparison_result["summary"]])}
                </ul>
            </div>
            
            <h2>2. 評論數量與頻率變化</h2>
            <table>
                <tr>
                    <th>指標</th>
                    <th>{period1_name}</th>
                    <th>{period2_name}</th>
                    <th>變化</th>
                </tr>
                <tr>
                    <td>評論總數</td>
                    <td>{comparison_result["review_volume"][period1_name]["total_reviews"]}</td>
                    <td>{comparison_result["review_volume"][period2_name]["total_reviews"]}</td>
                    <td class="{'positive' if comparison_result["review_volume"]["change"]["total_reviews_percent"] > 0 else 'negative'}">
                        {'+' if comparison_result["review_volume"]["change"]["total_reviews_percent"] > 0 else ''}{comparison_result["review_volume"]["change"]["total_reviews_percent"]}%
                    </td>
                </tr>
                <tr>
                    <td>每日平均評論數</td>
                    <td>{comparison_result["review_volume"][period1_name]["daily_average"]}</td>
                    <td>{comparison_result["review_volume"][period2_name]["daily_average"]}</td>
                    <td class="{'positive' if comparison_result["review_volume"]["change"]["daily_average_percent"] > 0 else 'negative'}">
                        {'+' if comparison_result["review_volume"]["change"]["daily_average_percent"] > 0 else ''}{comparison_result["review_volume"]["change"]["daily_average_percent"]}%
                    </td>
                </tr>
            </table>
            
            <div class="chart-container">
                <h3>每日評論數量趨勢</h3>
                {f'<img class="chart" src="{chart_rel_paths[2]}" alt="每日評論數量趨勢圖">' if len(chart_rel_paths) > 2 and chart_rel_paths[2] else '<div class="missing-chart">圖表生成失敗或暫無數據</div>'}
            </div>
            
            <h2>3. 評分變化</h2>
            <table>
                <tr>
                    <th>指標</th>
                    <th>{period1_name}</th>
                    <th>{period2_name}</th>
                    <th>變化</th>
                </tr>
                <tr>
                    <td>平均評分</td>
                    <td>{comparison_result["rating"][period1_name]["average_rating"]}</td>
                    <td>{comparison_result["rating"][period2_name]["average_rating"]}</td>
                    <td class="{'positive' if comparison_result["rating"]["change"]["average_rating"] > 0 else 'negative'}">
                        {'+' if comparison_result["rating"]["change"]["average_rating"] > 0 else ''}{comparison_result["rating"]["change"]["average_rating"]}
                    </td>
                </tr>
            </table>
            
            <div class="chart-container">
                <h3>評分分佈比較</h3>
                {f'<img class="chart" src="{chart_rel_paths[0]}" alt="評分分佈比較圖">' if len(chart_rel_paths) > 0 and chart_rel_paths[0] else '<div class="missing-chart">圖表生成失敗或暫無數據</div>'}
            </div>
            
            <h2>4. 評論情感分析</h2>
            <table>
                <tr>
                    <th>指標</th>
                    <th>{period1_name}</th>
                    <th>{period2_name}</th>
                    <th>變化</th>
                </tr>
                <tr>
                    <td>正面評論佔比</td>
                    <td>{comparison_result["sentiment"][period1_name]["positive_ratio"]}%</td>
                    <td>{comparison_result["sentiment"][period2_name]["positive_ratio"]}%</td>
                    <td class="{'positive' if comparison_result["sentiment"]["change"]["positive_ratio_points"] > 0 else 'negative'}">
                        {'+' if comparison_result["sentiment"]["change"]["positive_ratio_points"] > 0 else ''}{comparison_result["sentiment"]["change"]["positive_ratio_points"]} 百分點
                    </td>
                </tr>
                <tr>
                    <td>負面評論佔比</td>
                    <td>{comparison_result["sentiment"][period1_name]["negative_ratio"]}%</td>
                    <td>{comparison_result["sentiment"][period2_name]["negative_ratio"]}%</td>
                    <td class="{'negative' if comparison_result["sentiment"]["change"]["negative_ratio_points"] > 0 else 'positive'}">
                        {'+' if comparison_result["sentiment"]["change"]["negative_ratio_points"] > 0 else ''}{comparison_result["sentiment"]["change"]["negative_ratio_points"]} 百分點
                    </td>
                </tr>
                <tr>
                    <td>中立評論佔比</td>
                    <td>{comparison_result["sentiment"][period1_name]["neutral_ratio"]}%</td>
                    <td>{comparison_result["sentiment"][period2_name]["neutral_ratio"]}%</td>
                    <td class="neutral">
                        {'+' if comparison_result["sentiment"]["change"]["neutral_ratio_points"] > 0 else ''}{comparison_result["sentiment"]["change"]["neutral_ratio_points"]} 百分點
                    </td>
                </tr>
                <tr>
                    <td>平均情感分數</td>
                    <td>{comparison_result["sentiment"][period1_name]["average_sentiment_score"]}</td>
                    <td>{comparison_result["sentiment"][period2_name]["average_sentiment_score"]}</td>
                    <td class="{'positive' if comparison_result["sentiment"]["change"]["average_sentiment_score"] > 0 else 'negative'}">
                        {'+' if comparison_result["sentiment"]["change"]["average_sentiment_score"] > 0 else ''}{comparison_result["sentiment"]["change"]["average_sentiment_score"]}
                    </td>
                </tr>
            </table>
            
            <div class="chart-container">
                <h3>情感分佈比較</h3>
                {f'<img class="chart" src="{chart_rel_paths[1]}" alt="情感分佈比較圖">' if len(chart_rel_paths) > 1 and chart_rel_paths[1] else '<div class="missing-chart">圖表生成失敗或暫無數據</div>'}
            </div>
            
            <h2>5. 遊戲版本</h2>
            <table>
                <tr>
                    <th>時間段</th>
                    <th>主要版本</th>
                </tr>
                <tr>
                    <td>{period1_name}</td>
                    <td>{comparison_result["version"][period1_name]["main_version"]}</td>
                </tr>
                <tr>
                    <td>{period2_name}</td>
                    <td>{comparison_result["version"][period2_name]["main_version"]}</td>
                </tr>
            </table>
            <p>版本狀態: {"已更新" if comparison_result["version"]["version_changed"] else "未變更"}</p>
            
            <h2>6. 摘要判斷</h2>
            <div class="summary">
                <ul>
                    {"".join([f"<li>{point}</li>" for point in comparison_result["summary"]])}
                </ul>
            </div>
            
            <h2>7. 深入分析與影響因素</h2>
            <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4" style="border-radius: 5px; margin-bottom: 2rem; padding: 1rem;">
                <ul style="list-style-type: disc; padding-left: 2rem; margin-top: 0.5rem;">
                    {"".join([f"<li>{insight}</li>" for insight in comparison_result.get("detailed_insights", ["暫無詳細分析資料"])])}
                </ul>
            </div>
            
            <footer>
                <p>此報告由 PTCG Pocket 玩家輿情比較 API 自動生成 &copy; {datetime.now().year}</p>
                <p>報告檔案名稱: {filename}</p>
            </footer>
        </body>
        </html>
        """
        
        # 寫入HTML檔案
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"HTML報告已生成：{file_path}")
            return file_path
        except Exception as e:
            logger.error(f"生成HTML報告時發生錯誤：{str(e)}")
            raise