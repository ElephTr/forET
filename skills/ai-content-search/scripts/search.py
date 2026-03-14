#!/usr/bin/env python3
"""
AI 内容聚合搜索工具
一站式搜索多个平台的 AI 相关内容
"""

import argparse
import json
import urllib.request
import urllib.parse
import re
from html.parser import HTMLParser
from datetime import datetime

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def make_request(url, headers=None):
    """通用请求函数，带重试"""
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
    }
    if headers:
        default_headers.update(headers)
    
    req = urllib.request.Request(url, headers=default_headers)
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            import gzip
            if response.info().get('Content-Encoding') == 'gzip':
                return gzip.decompress(response.read()).decode('utf-8')
            return response.read().decode('utf-8')
    except Exception as e:
        raise e

def search_reddit(query):
    """搜索 Reddit - 使用旧版界面避免封锁"""
    try:
        encoded_query = urllib.parse.quote(query)
        # 使用旧版界面
        url = f"https://old.reddit.com/search?q={encoded_query}&sort=relevance"
        
        html = make_request(url)
            
        results = []
        # 提取帖子标题和链接
        pattern = r'<a[^>]*href="(/r/[^"]+/comments/[^"]+)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html)[:5]
        
        for match in matches:
            link = f"https://www.reddit.com{match[0]}"
            title = strip_tags(match[1]).strip()
            if title and len(title) > 10:
                results.append({
                    'platform': 'Reddit',
                    'title': title,
                    'url': link,
                    'source': 'reddit.com'
                })
        
        return results
    except Exception as e:
        return [{'platform': 'Reddit', 'error': str(e)}]

def search_zhihu(query):
    """搜索知乎"""
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.zhihu.com/search?type=content&q={encoded_query}"
        
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
        
        results = []
        # 提取问题和文章标题
        patterns = [
            r'<a[^>]*href="(https://www.zhihu.com/question/\d+)"[^>]*>([^<]+)</a>',
            r'<a[^>]*href="(https://zhuanlan.zhihu.com/p/\d+)"[^>]*>([^<]+)</a>'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)[:3]
            for match in matches:
                title = strip_tags(match[1]).strip()
                if title and len(title) > 5:
                    results.append({
                        'platform': '知乎',
                        'title': title,
                        'url': match[0],
                        'source': 'zhihu.com'
                    })
        
        return results[:5]
    except Exception as e:
        return [{'platform': '知乎', 'error': str(e)}]

def search_xiaohongshu(query):
    """搜索小红书"""
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.xiaohongshu.com/search_result?keyword={encoded_query}"
        
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
        
        results = []
        # 提取笔记标题
        pattern = r'"noteTitle":"([^"]+)".*?"noteId":"([^"]+)"'
        matches = re.findall(pattern, html)[:5]
        
        for match in matches:
            title = match[0].encode('utf-8').decode('unicode_escape')
            note_id = match[1]
            results.append({
                'platform': '小红书',
                'title': title,
                'url': f"https://www.xiaohongshu.com/explore/{note_id}",
                'source': 'xiaohongshu.com'
            })
        
        return results
    except Exception as e:
        return [{'platform': '小红书', 'error': str(e)}]

def search_youtube(query):
    """搜索 YouTube"""
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
        
        results = []
        # 提取视频标题和ID
        pattern = r'"videoId":"([^"]+)".*?"title":\{"runs":\[\{"text":"([^"]+)"\}\]\}'
        matches = re.findall(pattern, html)[:5]
        
        for match in matches:
            video_id = match[0]
            title = match[1].encode('utf-8').decode('unicode_escape')
            results.append({
                'platform': 'YouTube',
                'title': title,
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'source': 'youtube.com'
            })
        
        return results
    except Exception as e:
        return [{'platform': 'YouTube', 'error': str(e)}]

def search_github(query):
    """搜索 GitHub"""
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://github.com/search?q={encoded_query}&type=repositories"
        
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
        
        results = []
        # 提取仓库信息
        pattern = r'<a[^>]*href="(/[^/]+/[^"]+)"[^>]*>([^<]+)</a>.*?<p[^>]*>([^<]+)</p>'
        matches = re.findall(pattern, html)[:5]
        
        for match in matches:
            repo_path = match[0]
            name = strip_tags(match[1]).strip()
            desc = strip_tags(match[2]).strip() if len(match) > 2 else ''
            if name and not name.startswith('http'):
                results.append({
                    'platform': 'GitHub',
                    'title': name,
                    'description': desc[:100] + '...' if len(desc) > 100 else desc,
                    'url': f"https://github.com{repo_path}",
                    'source': 'github.com'
                })
        
        return results
    except Exception as e:
        return [{'platform': 'GitHub', 'error': str(e)}]

def search_hackernews(query):
    """搜索 Hacker News"""
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://hn.algolia.com/?q={encoded_query}"
        
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
        
        results = []
        # 提取文章标题
        pattern = r'<a[^>]*href="([^"]+)"[^>]*class="[^"]*title[^"]*"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html)[:5]
        
        for match in matches:
            link = match[0] if match[0].startswith('http') else f"https://news.ycombinator.com{match[0]}"
            title = strip_tags(match[1]).strip()
            if title and len(title) > 5:
                results.append({
                    'platform': 'Hacker News',
                    'title': title,
                    'url': link,
                    'source': 'news.ycombinator.com'
                })
        
        return results
    except Exception as e:
        return [{'platform': 'Hacker News', 'error': str(e)}]

def search_producthunt(query):
    """搜索 Product Hunt"""
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.producthunt.com/search?q={encoded_query}"
        
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
        
        results = []
        # 提取产品信息
        pattern = r'"name":"([^"]+)".*?"tagline":"([^"]+)".*?"url":"([^"]+)"'
        matches = re.findall(pattern, html)[:5]
        
        for match in matches:
            name = match[0]
            tagline = match[1]
            product_url = match[2]
            results.append({
                'platform': 'Product Hunt',
                'title': name,
                'description': tagline,
                'url': product_url if product_url.startswith('http') else f"https://www.producthunt.com{product_url}",
                'source': 'producthunt.com'
            })
        
        return results
    except Exception as e:
        return [{'platform': 'Product Hunt', 'error': str(e)}]

def aggregate_search(query, platforms=None):
    """聚合搜索多个平台"""
    all_platforms = {
        'reddit': search_reddit,
        'zhihu': search_zhihu,
        'xiaohongshu': search_xiaohongshu,
        'youtube': search_youtube,
        'github': search_github,
        'hackernews': search_hackernews,
        'producthunt': search_producthunt
    }
    
    if platforms:
        selected = {k: v for k, v in all_platforms.items() if k in platforms}
    else:
        selected = all_platforms
    
    results = {}
    for name, func in selected.items():
        print(f"Searching {name}...")
        results[name] = func(query)
    
    return results

def main():
    parser = argparse.ArgumentParser(description='AI 内容聚合搜索工具')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('--platforms', '-p', help='指定平台，逗号分隔 (reddit,zhihu,xiaohongshu,youtube,github,hackernews,producthunt)')
    parser.add_argument('--json', '-j', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    platforms = args.platforms.split(',') if args.platforms else None
    
    results = aggregate_search(args.query, platforms)
    
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"\n🔍 搜索结果: {args.query}\n")
        print("=" * 80)
        
        for platform, items in results.items():
            print(f"\n📌 {platform.upper()}")
            print("-" * 80)
            
            if not items or 'error' in items[0]:
                print(f"  ❌ 搜索失败: {items[0].get('error', 'Unknown error')}")
                continue
            
            for i, item in enumerate(items, 1):
                print(f"\n  {i}. {item.get('title', 'N/A')}")
                if 'description' in item:
                    print(f"     📝 {item['description']}")
                print(f"     🔗 {item.get('url', 'N/A')}")
        
        print("\n" + "=" * 80)

if __name__ == '__main__':
    main()