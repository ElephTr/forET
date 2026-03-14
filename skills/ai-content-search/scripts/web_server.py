#!/usr/bin/env python3
"""
AI 内容搜索 Web 服务器
提供 Web 界面进行聚合搜索
"""

import http.server
import socketserver
import urllib.parse
import json
import sys
import os

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from search import aggregate_search

PORT = 8888

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 内容聚合搜索</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            padding: 20px; 
        }
        .container { max-width: 1200px; margin: 0 auto; }
        header { text-align: center; padding: 40px 20px; color: white; }
        header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        header p { font-size: 1.1rem; opacity: 0.9; }
        .search-box { 
            max-width: 700px; 
            margin: 0 auto 30px; 
            display: flex;
            gap: 10px;
        }
        .search-box input { 
            flex: 1;
            padding: 15px 25px; 
            border: none; 
            border-radius: 50px; 
            font-size: 1rem; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.1); 
            outline: none;
        }
        .search-box button {
            padding: 15px 30px;
            border: none;
            border-radius: 50px;
            background: #ff6b6b;
            color: white;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s;
        }
        .search-box button:hover {
            background: #ff5252;
            transform: scale(1.05);
        }
        .platforms {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin-bottom: 30px;
        }
        .platform-tag {
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
            border: 2px solid transparent;
        }
        .platform-tag:hover, .platform-tag.active {
            background: white;
            color: #667eea;
        }
        .results { display: grid; gap: 20px; }
        .platform-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .platform-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }
        .platform-icon {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }
        .platform-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #333;
        }
        .result-item {
            padding: 15px;
            border-radius: 10px;
            background: #f8f9fa;
            margin-bottom: 10px;
            transition: all 0.3s;
        }
        .result-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
        .result-title {
            font-size: 1rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        .result-title a {
            color: #667eea;
            text-decoration: none;
        }
        .result-title a:hover {
            text-decoration: underline;
        }
        .result-desc {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 5px;
        }
        .result-source {
            font-size: 0.8rem;
            color: #999;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: white;
        }
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 3px solid rgba(255,255,255,0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        footer {
            text-align: center;
            padding: 40px;
            color: white;
            opacity: 0.8;
        }
        @media (max-width: 768px) {
            header h1 { font-size: 1.8rem; }
            .search-box { flex-direction: column; }
            .search-box button { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 AI 内容聚合搜索</h1>
            <p>一站式搜索 Reddit、知乎、小红书、YouTube 等平台的 AI 内容</p>
        </header>
        
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="输入关键词搜索 AI 内容..." value="{query}">
            <button onclick="doSearch()">搜索</button>
        </div>
        
        <div class="platforms">
            <span class="platform-tag active" data-platform="all">全部</span>
            <span class="platform-tag" data-platform="reddit">Reddit</span>
            <span class="platform-tag" data-platform="zhihu">知乎</span>
            <span class="platform-tag" data-platform="xiaohongshu">小红书</span>
            <span class="platform-tag" data-platform="youtube">YouTube</span>
            <span class="platform-tag" data-platform="github">GitHub</span>
            <span class="platform-tag" data-platform="hackernews">Hacker News</span>
            <span class="platform-tag" data-platform="producthunt">Product Hunt</span>
        </div>
        
        <div id="results" class="results">
            {results}
        </div>
        
        <footer>
            <p>AI 内容聚合搜索 - 无需登录，直接搜索</p>
        </footer>
    </div>
    
    <script>
        let selectedPlatforms = ['all'];
        
        document.querySelectorAll('.platform-tag').forEach(tag => {
            tag.addEventListener('click', function() {
                document.querySelectorAll('.platform-tag').forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                selectedPlatforms = [this.dataset.platform];
            });
        });
        
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') doSearch();
        });
        
        function doSearch() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) return;
            
            const platforms = selectedPlatforms.includes('all') ? '' : selectedPlatforms.join(',');
            window.location.href = '/search?q=' + encodeURIComponent(query) + (platforms ? '&p=' + platforms : '');
        }
        
        {autosearch}
    </script>
</body>
</html>'''

PLATFORM_ICONS = {
    'reddit': ('🤖', '#FF4500'),
    'zhihu': ('📚', '#0084FF'),
    'xiaohongshu': ('📕', '#FF2442'),
    'youtube': ('▶️', '#FF0000'),
    'github': ('💻', '#333'),
    'hackernews': ('🗞️', '#FF6600'),
    'producthunt': ('🚀', '#DA552F')
}

class SearchHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path == '/':
            self.send_html(HTML_TEMPLATE.format(query='', results='', autosearch=''))
        
        elif parsed.path == '/search':
            params = urllib.parse.parse_qs(parsed.query)
            query = params.get('q', [''])[0]
            platforms = params.get('p', [''])[0].split(',') if params.get('p') else None
            
            if not query:
                self.send_html(HTML_TEMPLATE.format(query='', results='', autosearch=''))
                return
            
            # 执行搜索
            results = aggregate_search(query, platforms)
            
            # 生成结果 HTML
            results_html = self.generate_results_html(results)
            
            autosearch = f'''
                document.getElementById("searchInput").value = {json.dumps(query)};
            '''
            
            self.send_html(HTML_TEMPLATE.format(
                query=query,
                results=results_html,
                autosearch=autosearch
            ))
        
        elif parsed.path == '/api/search':
            params = urllib.parse.parse_qs(parsed.query)
            query = params.get('q', [''])[0]
            platforms = params.get('p', [''])[0].split(',') if params.get('p') else None
            
            results = aggregate_search(query, platforms)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(results, ensure_ascii=False).encode())
        
        else:
            super().do_GET()
    
    def send_html(self, content):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(content.encode())
    
    def generate_results_html(self, results):
        if not results:
            return '<div class="platform-section"><p style="text-align:center;color:#999">暂无结果</p></div>'
        
        html = ''
        for platform, items in results.items():
            icon, color = PLATFORM_ICONS.get(platform, ('🔍', '#667eea'))
            
            html += f'''
                <div class="platform-section">
                    <div class="platform-header">
                        <div class="platform-icon" style="background:{color}20;color:{color}">{icon}</div>
                        <div class="platform-title">{platform.upper()}</div>
                    </div>
            '''
            
            if not items or 'error' in items[0]:
                html += f'<div class="error">搜索失败: {items[0].get("error", "Unknown error")}</div>'
            else:
                for item in items:
                    title = item.get('title', 'N/A')
                    url = item.get('url', '#')
                    desc = item.get('description', '')
                    source = item.get('source', '')
                    
                    html += f'''
                        <div class="result-item">
                            <div class="result-title"><a href="{url}" target="_blank">{title}</a></div>
                            {f'<div class="result-desc">{desc}</div>' if desc else ''}
                            <div class="result-source">{source}</div>
                        </div>
                    '''
            
            html += '</div>'
        
        return html

def main():
    with socketserver.TCPServer(("", PORT), SearchHandler) as httpd:
        print(f"AI 内容搜索服务器启动在 http://localhost:{PORT}/")
        print("按 Ctrl+C 停止")
        httpd.serve_forever()

if __name__ == '__main__':
    main()