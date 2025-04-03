"""
前端初始化指令碼 - 用於建立前端資料夾並複製 HTML 文件
"""
import os
import shutil
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_frontend():
    """初始化前端目錄和檔案"""
    try:
        # 建立前端資料夾
        frontend_dir = "frontend"
        os.makedirs(frontend_dir, exist_ok=True)
        logger.info(f"已建立前端資料夾: {frontend_dir}")
        
        # 建立報告資料夾
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        logger.info(f"已建立報告資料夾: {reports_dir}")
        
        # 複製前端 HTML 檔案
        html_content = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PTCG Pocket 玩家輿情分析儀表板</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Font Awesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Flatpickr 日期選擇器 -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
    <script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
    <script src="https://cdn.jsdelivr.net/npm/flatpickr/dist/l10n/zh-tw.js"></script>
    <!-- 動畫庫 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
    <!-- 自定義樣式 -->
    <style>
        .card-hover {
            transition: all 0.3s ease;
        }
        .card-hover:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
        .loader {
            border-top-color: #3498db;
            -webkit-animation: spinner 1.5s linear infinite;
            animation: spinner 1.5s linear infinite;
        }
        @-webkit-keyframes spinner {
            0% { -webkit-transform: rotate(0deg); }
            100% { -webkit-transform: rotate(360deg); }
        }
        @keyframes spinner {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .fade-in {
            animation: fadeIn 0.5s ease-in-out;
        }
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
        .slide-in {
            animation: slideIn 0.5s ease-in-out;
        }
        @keyframes slideIn {
            0% { transform: translateY(20px); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
        }
        .pulse {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <!-- 標題區 -->
        <header class="text-center mb-12 animate__animated animate__fadeIn">
            <div class="flex justify-center items-center mb-4">
                <img src="https://via.placeholder.com/60" alt="Logo" class="mr-3 rounded-lg">
                <h1 class="text-4xl font-bold text-indigo-700">PTCG Pocket 玩家輿情分析儀表板</h1>
            </div>
            <p class="text-gray-600 max-w-2xl mx-auto">透過選擇兩個時間段，對玩家評論進行情感與趨勢分析，生成綜合性的輿情比較報告</p>
        </header>

        <!-- 主要內容 -->
        <main>
            <!-- 日期選擇區塊 -->
            <div class="bg-white rounded-xl shadow-md p-6 mb-8 slide-in">
                <h2 class="text-2xl font-semibold mb-6 text-gray-800 flex items-center">
                    <i class="fas fa-calendar-alt text-indigo-500 mr-2"></i> 選擇比較時間段
                </h2>
                
                <form id="comparisonForm" class="grid md:grid-cols-2 gap-6">
                    <!-- 第一個時間段 -->
                    <div class="bg-indigo-50 p-5 rounded-lg border border-indigo-100">
                        <h3 class="text-lg font-medium text-indigo-700 mb-4 flex items-center">
                            <i class="fas fa-hourglass-start mr-2"></i> 時間段 1
                        </h3>
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-medium mb-2" for="period1Name">
                                時間段名稱
                            </label>
                            <input type="text" id="period1Name" name="period1Name" value="第一時間段" 
                                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-gray-700 text-sm font-medium mb-2" for="period1Start">
                                    開始日期
                                </label>
                                <div class="relative">
                                    <input type="text" id="period1Start" name="period1Start" placeholder="選擇日期" 
                                        class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 date-picker">
                                    <div class="absolute left-3 top-2 text-gray-400">
                                        <i class="fas fa-calendar"></i>
                                    </div>
                                </div>
                            </div>
                            <div>
                                <label class="block text-gray-700 text-sm font-medium mb-2" for="period1End">
                                    結束日期
                                </label>
                                <div class="relative">
                                    <input type="text" id="period1End" name="period1End" placeholder="選擇日期" 
                                        class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 date-picker">
                                    <div class="absolute left-3 top-2 text-gray-400">
                                        <i class="fas fa-calendar"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 第二個時間段 -->
                    <div class="bg-blue-50 p-5 rounded-lg border border-blue-100">
                        <h3 class="text-lg font-medium text-blue-700 mb-4 flex items-center">
                            <i class="fas fa-hourglass-end mr-2"></i> 時間段 2
                        </h3>
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-medium mb-2" for="period2Name">
                                時間段名稱
                            </label>
                            <input type="text" id="period2Name" name="period2Name" value="第二時間段" 
                                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-gray-700 text-sm font-medium mb-2" for="period2Start">
                                    開始日期
                                </label>
                                <div class="relative">
                                    <input type="text" id="period2Start" name="period2Start" placeholder="選擇日期" 
                                        class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 date-picker">
                                    <div class="absolute left-3 top-2 text-gray-400">
                                        <i class="fas fa-calendar"></i>
                                    </div>
                                </div>
                            </div>
                            <div>
                                <label class="block text-gray-700 text-sm font-medium mb-2" for="period2End">
                                    結束日期
                                </label>
                                <div class="relative">
                                    <input type="text" id="period2End" name="period2End" placeholder="選擇日期" 
                                        class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 date-picker">
                                    <div class="absolute left-3 top-2 text-gray-400">
                                        <i class="fas fa-calendar"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 輸出選項 -->
                    <div class="md:col-span-2 grid md:grid-cols-3 gap-6 mt-2">
                        <div>
                            <label class="block text-gray-700 text-sm font-medium mb-2">
                                選擇輸出格式
                            </label>
                            <div class="flex space-x-4">
                                <label class="inline-flex items-center">
                                    <input type="radio" name="outputFormat" value="html" checked class="form-radio text-indigo-600">
                                    <span class="ml-2">HTML 報告</span>
                                </label>
                                <label class="inline-flex items-center">
                                    <input type="radio" name="outputFormat" value="json" class="form-radio text-indigo-600">
                                    <span class="ml-2">JSON 數據</span>
                                </label>
                                <label class="inline-flex items-center">
                                    <input type="radio" name="outputFormat" value="text" class="form-radio text-indigo-600">
                                    <span class="ml-2">純文字報告</span>
                                </label>
                            </div>
                        </div>
                        
                        <div class="md:col-span-2 flex justify-end items-end">
                            <button id="dataSummaryBtn" type="button" class="px-4 py-2 mr-4 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-400 transition flex items-center">
                                <i class="fas fa-info-circle mr-2"></i> 查看資料概要
                            </button>
                            <button type="button" id="generateBtn" class="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition flex items-center pulse">
                                <i class="fas fa-chart-bar mr-2"></i> 生成分析報告
                            </button>
                        </div>
                    </div>
                </form>
            </div>
            
            <!-- 資料狀態區塊 (初始隱藏) -->
            <div id="dataStatusCard" class="bg-white rounded-xl shadow-md p-6 mb-8 hidden fade-in">
                <h2 class="text-2xl font-semibold mb-4 text-gray-800 flex items-center">
                    <i class="fas fa-database text-green-500 mr-2"></i> 資料概況
                </h2>
                <div id="dataStatusContent" class="grid md:grid-cols-2 gap-6">
                    <!-- 動態內容將在這裡顯示 -->
                </div>
            </div>
            
            <!-- 功能卡片區 -->
            <div class="grid md:grid-cols-3 gap-6 mb-12">
                <div class="bg-white rounded-xl shadow-md p-6 card-hover">
                    <div class="text-blue-500 text-4xl mb-4">
                        <i class="fas fa-comments"></i>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-800 mb-2">評論數量與頻率</h3>
                    <p class="text-gray-600">分析不同時間段的評論數量變化，識別高峰期和低谷期，探索評論頻率趨勢</p>
                </div>
                
                <div class="bg-white rounded-xl shadow-md p-6 card-hover">
                    <div class="text-purple-500 text-4xl mb-4">
                        <i class="fas fa-heart"></i>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-800 mb-2">情感分析</h3>
                    <p class="text-gray-600">對評論進行情感分析，識別正面、負面和中性評論，比較不同時期的情感變化</p>
                </div>
                
                <div class="bg-white rounded-xl shadow-md p-6 card-hover">
                    <div class="text-green-500 text-4xl mb-4">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-800 mb-2">趨勢判斷</h3>
                    <p class="text-gray-600">基於評論數據分析玩家反饋趨勢，識別遊戲版本更新後的玩家反應變化</p>
                </div>
            </div>
            
            <!-- 結果區塊 (初始隱藏) -->
            <div id="resultCard" class="bg-white rounded-xl shadow-md p-6 mb-8 hidden fade-in">
                <h2 class="text-2xl font-semibold mb-6 text-gray-800 flex items-center">
                    <i class="fas fa-file-alt text-indigo-500 mr-2"></i> 分析報告
                </h2>
                <div id="resultContent">
                    <!-- 動態內容將在這裡顯示 -->
                </div>
            </div>
            
            <!-- 載入中指示器 (初始隱藏) -->
            <div id="loadingIndicator" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 hidden">
                <div class="bg-white p-6 rounded-lg shadow-lg text-center">
                    <div class="loader ease-linear rounded-full border-8 border-t-8 border-gray-200 h-24 w-24 mb-4 mx-auto"></div>
                    <h2 class="text-xl font-semibold text-gray-700">處理中...</h2>
                    <p class="text-gray-600" id="loadingMessage">正在分析玩家評論數據</p>
                </div>
            </div>
        </main>
        
        <!-- 頁腳 -->
        <footer class="mt-12 text-center text-gray-500 text-sm">
            <p>&copy; 2025 PTCG Pocket 玩家輿情分析系統</p>
        </footer>
    </div>
    
    <!-- JavaScript -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // 初始化日期選擇器
            const datePickerOptions = {
                locale: 'zh-tw',
                dateFormat: 'Y-m-d',
                disableMobile: true
            };
            
            document.querySelectorAll('.date-picker').forEach(element => {
                flatpickr(element, datePickerOptions);
            });
            
            // 查詢可用的日期範圍
            fetch('/api/data/date-range')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // 設定日期選擇器的範圍限制
                        const dateRange = {
                            minDate: data.min_date,
                            maxDate: data.max_date
                        };
                        
                        // 自動填充默認日期
                        // 將最後一個月分為兩個時間段
                        const maxDate = new Date(data.max_date);
                        const mid = new Date(maxDate);
                        mid.setDate(mid.getDate() - 15);
                        const mid2 = new Date(mid);
                        mid2.setDate(mid2.getDate() - 1);
                        const min = new Date(mid);
                        min.setDate(min.getDate() - 14);
                        
                        document.getElementById('period1Start').value = formatDate(min);
                        document.getElementById('period1End').value = formatDate(mid2);
                        document.getElementById('period2Start').value = formatDate(mid);
                        document.getElementById('period2End').value = formatDate(maxDate);
                        
                        // 更新日期選擇器配置
                        document.querySelectorAll('.date-picker').forEach(element => {
                            flatpickr(element, {
                                ...datePickerOptions,
                                minDate: data.min_date,
                                maxDate: data.max_date
                            });
                        });
                    }
                })
                .catch(error => {
                    console.error('Error fetching date range:', error);
                });
            
            // 顯示資料概要按鈕點擊事件
            document.getElementById('dataSummaryBtn').addEventListener('click', function() {
                showLoading('正在獲取資料概要...');
                
                fetch('/api/data/status')
                    .then(response => response.json())
                    .then(data => {
                        hideLoading();
                        if (data.status === 'success') {
                            displayDataStatus(data.data_stats);
                        } else {
                            showError('無法獲取資料概要');
                        }
                    })
                    .catch(error => {
                        hideLoading();
                        showError('獲取資料時發生錯誤: ' + error.message);
                    });
            });
            
            // 生成報告按鈕點擊事件
            document.getElementById('generateBtn').addEventListener('click', function() {
                const period1Start = document.getElementById('period1Start').value;
                const period1End = document.getElementById('period1End').value;
                const period2Start = document.getElementById('period2Start').value;
                const period2End = document.getElementById('period2End').value;
                const period1Name = document.getElementById('period1Name').value;
                const period2Name = document.getElementById('period2Name').value;
                const outputFormat = document.querySelector('input[name="outputFormat"]:checked').value;
                
                // 驗證所有日期都已選擇
                if (!period1Start || !period1End || !period2Start || !period2End) {
                    showError('請選擇所有日期');
                    return;
                }
                
                showLoading('正在生成分析報告...');
                
                // 準備API請求
                const requestBody = {
                    period1_start: period1Start,
                    period1_end: period1End,
                    period2_start: period2Start,
                    period2_end: period2End,
                    period1_name: period1Name,
                    period2_name: period2Name,
                    output_format: outputFormat
                };
                
                // 調用API
                fetch('/api/comparison', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestBody)
                })
                .then(response => response.json())
                .then(data => {
                    hideLoading();
                    if (data.status === 'success') {
                        displayResult(data, outputFormat);
                    } else {
                        showError('生成報告失敗: ' + data.message);
                    }
                })
                .catch(error => {
                    hideLoading();
                    showError('請求失敗: ' + error.message);
                });
            });
            
            // 顯示載入中指示器
            function showLoading(message) {
                document.getElementById('loadingMessage').textContent = message;
                document.getElementById('loadingIndicator').classList.remove('hidden');
            }
            
            // 隱藏載入中指示器
            function hideLoading() {
                document.getElementById('loadingIndicator').classList.add('hidden');
            }
            
            // 顯示錯誤提示
            function showError(message) {
                // 可以使用更好的提示元件，這裡用簡單的 alert
                alert(message);
            }
            
            // 格式化日期
            function formatDate(date) {
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                return `${year}-${month}-${day}`;
            }
            
            // 顯示資料概要
            function displayDataStatus(stats) {
                const statusCard = document.getElementById('dataStatusCard');
                const statusContent = document.getElementById('dataStatusContent');
                
                // 清空現有內容
                statusContent.innerHTML = '';
                
                // 創建概要內容
                const ratingDistribution = stats.rating_distribution || {};
                const sortedRatings = Object.keys(ratingDistribution).sort();
                
                // 左側面板：基本統計
                const leftPanel = document.createElement('div');
                leftPanel.innerHTML = `
                    <h3 class="text-lg font-medium text-gray-800 mb-3">基本統計資訊</h3>
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <div class="grid grid-cols-2 gap-4">
                            <div class="flex items-center">
                                <i class="fas fa-comments text-blue-500 mr-2"></i>
                                <div>
                                    <div class="text-sm text-gray-500">總評論數</div>
                                    <div class="font-medium">${stats.total_reviews}</div>
                                </div>
                            </div>
                            <div class="flex items-center">
                                <i class="fas fa-star text-yellow-500 mr-2"></i>
                                <div>
                                    <div class="text-sm text-gray-500">平均評分</div>
                                    <div class="font-medium">${stats.average_rating}</div>
                                </div>
                            </div>
                            <div class="flex items-center">
                                <i class="fas fa-calendar-alt text-green-500 mr-2"></i>
                                <div>
                                    <div class="text-sm text-gray-500">最早日期</div>
                                    <div class="font-medium">${stats.date_range.min}</div>
                                </div>
                            </div>
                            <div class="flex items-center">
                                <i class="fas fa-calendar-check text-purple-500 mr-2"></i>
                                <div>
                                    <div class="text-sm text-gray-500">最晚日期</div>
                                    <div class="font-medium">${stats.date_range.max}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                // 右側面板：評分分佈
                const rightPanel = document.createElement('div');
                rightPanel.innerHTML = `
                    <h3 class="text-lg font-medium text-gray-800 mb-3">評分分佈</h3>
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <div class="flex flex-col space-y-2">
                            ${sortedRatings.map(rating => {
                                const percentage = (ratingDistribution[rating] / stats.total_reviews * 100).toFixed(1);
                                return `
                                    <div>
                                        <div class="flex justify-between mb-1">
                                            <span class="text-sm text-gray-600">${rating} 星</span>
                                            <span class="text-sm text-gray-600">${percentage}%</span>
                                        </div>
                                        <div class="w-full bg-gray-200 rounded-full h-2.5">
                                            <div class="bg-blue-600 h-2.5 rounded-full" style="width: ${percentage}%"></div>
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                `;
                
                // 添加內容到頁面
                statusContent.appendChild(leftPanel);
                statusContent.appendChild(rightPanel);
                
                // 顯示卡片
                statusCard.classList.remove('hidden');
            }
            
            // 顯示分析結果
            function displayResult(data, outputFormat) {
                const resultCard = document.getElementById('resultCard');
                const resultContent = document.getElementById('resultContent');
                
                // 清空現有內容
                resultContent.innerHTML = '';
                
                if (outputFormat === 'html') {
                    // HTML 格式：顯示報告連結
                    resultContent.innerHTML = `
                        <div class="bg-green-50 border-l-4 border-green-500 p-4 mb-6">
                            <div class="flex">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-check-circle text-green-500"></i>
                                </div>
                                <div class="ml-3">
                                    <p class="text-sm text-green-700">報告生成成功！</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="text-center p-8 bg-gray-50 rounded-lg">
                            <i class="fas fa-file-alt text-5xl text-indigo-500 mb-4"></i>
                            <h3 class="text-xl font-semibold text-gray-800 mb-2">報告已準備就緒</h3>
                            <p class="text-gray-600 mb-6">您可以點擊下方按鈕查看完整的分析報告</p>
                            <a href="${data.report_path}" target="_blank" class="inline-flex items-center px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition">
                                <i class="fas fa-external-link-alt mr-2"></i> 查看完整報告
                            </a>
                        </div>
                        
                        <div class="mt-6">
                            <h3 class="text-lg font-medium text-gray-800 mb-3">摘要</h3>
                            <ul class="list-disc pl-5 space-y-2 text-gray-600">
                                ${data.comparison_result.summary.map(point => `<li>${point}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                } else if (outputFormat === 'json') {
                    // JSON 格式：顯示簡化的 JSON
                    const jsonPreview = {
                        status: data.status,
                        message: data.message,
                        report_path: data.report_path,
                        summary: data.comparison_result.summary
                    };
                    
                    resultContent.innerHTML = `
                        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
                            <div class="flex">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-info-circle text-blue-500"></i>
                                </div>
                                <div class="ml-3">
                                    <p class="text-sm text-blue-700">JSON 數據生成成功！完整數據已儲存至 ${data.report_path}</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="bg-gray-800 text-white p-4 rounded-lg overflow-x-auto">
                            <pre class="text-sm">${JSON.stringify(jsonPreview, null, 2)}</pre>
                        </div>
                        
                        <div class="mt-6 text-center">
                            <a href="${data.report_path}" target="_blank" class="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition">
                                <i class="fas fa-download mr-2"></i> 下載完整 JSON 數據
                            </a>
                        </div>
                    `;
                } else if (outputFormat === 'text') {
                    // 文字格式：顯示報告下載連結
                    resultContent.innerHTML = `
                        <div class="bg-purple-50 border-l-4 border-purple-500 p-4 mb-6">
                            <div class="flex">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-file-alt text-purple-500"></i>
                                </div>
                                <div class="ml-3">
                                    <p class="text-sm text-purple-700">文字報告生成成功！</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="text-center p-8 bg-gray-50 rounded-lg">
                            <i class="fas fa-file-text text-5xl text-purple-500 mb-4"></i>
                            <h3 class="text-xl font-semibold text-gray-800 mb-2">文字報告已準備就緒</h3>
                            <p class="text-gray-600 mb-6">您可以下載純文字格式的分析報告</p>
                            <a href="${data.report_path}" target="_blank" class="inline-flex items-center px-6 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition">
                                <i class="fas fa-download mr-2"></i> 下載文字報告
                            </a>
                        </div>
                        
                        <div class="mt-6">
                            <h3 class="text-lg font-medium text-gray-800 mb-3">摘要</h3>
                            <ul class="list-disc pl-5 space-y-2 text-gray-600">
                                ${data.comparison_result.summary.map(point => `<li>${point}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }
                
                // 顯示結果卡片
                resultCard.classList.remove('hidden');
                
                // 滾動到結果卡片
                resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    </script>
</body>
</html>
"""
        
        # 將HTML內容寫入檔案
        frontend_html_path = os.path.join(frontend_dir, "index.html")
        with open(frontend_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(f"已生成前端HTML檔案: {frontend_html_path}")
        
        logo_url = "https://via.placeholder.com/60"
        logger.info(f"使用圖片作為logo: {logo_url}")
        
        logger.info("前端初始化完成")
        
    except Exception as e:
        logger.error(f"初始化前端時發生錯誤: {str(e)}")
        raise

if __name__ == "__main__":
    init_frontend()