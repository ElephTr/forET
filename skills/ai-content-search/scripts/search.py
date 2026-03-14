#!/usr/bin/env python3
"""
AI 内容聚合搜索工具 v3
增强版：反爬绕过、RSS接口、重试机制
"""

import argparse
import json
import urllib.request
import urllib.parse
import urllib.error
import re
import ssl
import time
import random
from datetime import datetime

# 禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

# 轮换 User-Agent 列表
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

def get_random_headers():
    """获取随机请求头"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }

def make_request(url, headers=None, timeout=20, retries=3):
    """带重试的请求函数"""
    for attempt in range(retries):
        try:
            req_headers = get_random_headers()
            if headers:
                req_headers.update(headers)
            
            req = urllib.request.Request(url, headers=req_headers)
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                import gzip
                data = response.read()
                if response.info().get('Content-Encoding') == 'gzip':
                    data = gzip.decompress(data)
                return data.decode('utf-8', errors='ignore')
        
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Too Many Requests
                wait_time = (attempt + 1) * 2 + random.uniform(0, 1)
                print(f"    ⏳ 被限流，等待 {wait_time:.1f} 秒后重试...")
                time.sleep(wait_time)
            elif e.code in [403, 401]:
                print(f"    ❌ 访问被拒绝 (HTTP {e.code})")
                return None
            else:
                print(f"    ⚠️ HTTP 错误 {e.code}，重试中...")
                time.sleep(1)
        
        except Exception as e:
            if attempt < retries - 1:
                print(f"    ⚠️ 请求失败: {str(e)[:50]}，重试中...")
                time.sleep(1)
            else:
                print(f"    ❌ 请求失败: {str(e)[:50]}")
                return None
    
    return None

def search_duckduckgo(query, site=None):
    """使用 DuckDuckGo 搜索"""
    try:
        if site:
            search_query = f"site:{site} {query}"
        else:
            search_query = query
        
        # 添加随机延迟
        time.sleep(random.uniform(0.5, 1.5))
        
        encoded_query = urllib.parse.quote(search_query)
        # 尝试多个 DuckDuckGo 域名
        domains = ['html.duckduckgo.com', 'duckduckgo.com']
        
        for domain in domains:
            url = f"https://{domain}/html/?q={encoded_query}"
            
            html = make_request(url)
            if not html:
                continue
            
            results = []
            # 多种匹配模式
            patterns = [
                r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                r'<a[^>]*href="([^"]+)"[^>]*class="[^"]*result[^"]*"[^>]*>(.*?)</a>',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.DOTALL)
                for match in matches[:10]:
                    link = match[0]
                    # 解码 DuckDuckGo 跳转链接
                    if 'duckduckgo.com' in link and 'uddg=' in link:
                        uddg_match = re.search(r'uddg=([^&]+)', link)
                        if uddg_match:
                            link = urllib.parse.unquote(uddg_match.group(1))
                    
                    title = re.sub(r'<[^>]+>', '', match[1]).strip()
                    
                    # 过滤广告和无效结果
                    if title and len(title) > 5 and not any(x in title.lower() for x in ['advertisement', 'sponsored', 'ad ']):
                        # 确保链接有效
                        if link.startswith('http') and not link.startswith('https://duckduckgo.com/y.js'):
                            results.append({
                                'title': title,
                                'url': link
                            })
                
                if results:
                    break
            
            if results:
                return results
        
        return []
    
    except Exception as e:
        return [{'error': str(e)}]

def search_reddit_rss(query):
    """通过 Reddit RSS 搜索"""
    try:
        # Reddit 搜索 RSS
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.reddit.com/search.rss?q={encoded_query}&sort=new&limit=10"
        
        time.sleep(random.uniform(0.5, 1))
        
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'application/rss+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        html = make_request(url, headers)
        if not html:
            return []
        
        results = []
        # 解析 RSS
        items = re.findall(r'<item>.*?</item>', html, re.DOTALL)
        
        for item in items[:10]:
            title_match = re.search(r'<title>(.*?)</title>', item)
            link_match = re.search(r'<link>(.*?)</link>', item)
            
            if title_match and link_match:
                title = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', title_match.group(1))
                link = link_match.group(1)
                results.append({
                    'title': title.strip(),
                    'url': link.strip(),
                    'platform': 'REDDIT',
                    'source': 'reddit.com'
                })
        
        return results
    except Exception as e:
        return []

def search_hackernews_api(query):
    """通过 Hacker News API 搜索"""
    try:
        # HN Algolia API
        encoded_query = urllib.parse.quote(query)
        url = f"https://hn.algolia.com/api/v1/search?query={encoded_query}&tags=story&hitsPerPage=10"
        
        time.sleep(random.uniform(0.5, 1))
        
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'application/json',
        }
        
        html = make_request(url, headers)
        if not html:
            return []
        
        data = json.loads(html)
        results = []
        
        for hit in data.get('hits', [])[:10]:
            title = hit.get('title', '')
            url = hit.get('url') or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            if title:
                results.append({
                    'title': title,
                    'url': url,
                    'platform': 'HACKERNEWS',
                    'source': 'news.ycombinator.com'
                })
        
        return results
    except Exception as e:
        return []

def search_github_trending(query):
    """搜索 GitHub 热门仓库"""
    try:
        # GitHub 搜索 API 需要认证，使用网页搜索
        return search_duckduckgo(f"{query} awesome", 'github.com')
    except Exception as e:
        return []

def search_ai_nav_sites():
    """从 AI 导航站获取热门工具"""
    results = []
    
    # 尝试从 theresanaiforthat.com 获取
    try:
        url = "https://theresanaiforthat.com/"
        html = make_request(url, timeout=10)
        if html:
            # 提取工具名称
            tools = re.findall(r'<h3[^>]*>([^<]+)</h3>', html)
            for tool in tools[:10]:
                if len(tool.strip()) > 2:
                    results.append({
                        'title': f"{tool.strip()} - There's An AI For That",
                        'url': 'https://theresanaiforthat.com',
                        'platform': 'AI_NAV',
                        'source': 'theresanaiforthat.com'
                    })
    except:
        pass
    
    # 尝试从 futurepedia.io 获取
    try:
        url = "https://www.futurepedia.io/"
        html = make_request(url, timeout=10)
        if html:
            tools = re.findall(r'alt="([^"]+)"[^>]*class="[^"]*tool[^"]*"', html)
            for tool in tools[:10]:
                if len(tool.strip()) > 2:
                    results.append({
                        'title': f"{tool.strip()} - Futurepedia",
                        'url': 'https://www.futurepedia.io',
                        'platform': 'AI_NAV',
                        'source': 'futurepedia.io'
                    })
    except:
        pass
    
    return results

def search_platform(query, platform):
    """搜索指定平台"""
    site_map = {
        'reddit': 'reddit.com',
        'zhihu': 'zhihu.com',
        'xiaohongshu': 'xiaohongshu.com',
        'youtube': 'youtube.com',
        'github': 'github.com',
        'hackernews': 'news.ycombinator.com',
        'producthunt': 'producthunt.com',
        'twitter': 'twitter.com',
        'medium': 'medium.com',
        'devto': 'dev.to'
    }
    
    print(f"🔍 搜索 {platform}...")
    
    # 特殊处理某些平台
    if platform == 'reddit':
        # 先尝试 RSS
        results = search_reddit_rss(query)
        if results:
            return results
        # 回退到 DuckDuckGo
        site = site_map.get(platform)
        results = search_duckduckgo(query, site)
    
    elif platform == 'hackernews':
        # 使用 HN API
        results = search_hackernews_api(query)
        if results:
            return results
        site = site_map.get(platform)
        results = search_duckduckgo(query, site)
    
    elif platform == 'github':
        results = search_github_trending(query)
    
    elif platform == 'ainav':
        results = search_ai_nav_sites()
    
    else:
        site = site_map.get(platform)
        if not site:
            return []
        results = search_duckduckgo(query, site)
    
    # 添加平台标识
    for item in results:
        if 'error' not in item and 'platform' not in item:
            item['platform'] = platform.upper()
            item['source'] = site_map.get(platform, '')
    
    return results

def aggregate_search(query, platforms=None):
    """聚合搜索"""
    all_platforms = ['reddit', 'zhihu', 'hackernews', 'github', 'youtube', 'producthunt', 'medium', 'ainav']
    
    if platforms:
        selected = [p for p in platforms if p in all_platforms]
    else:
        selected = all_platforms
    
    results = {}
    for platform in selected:
        results[platform] = search_platform(query, platform)
        # 平台间添加延迟
        if platform != selected[-1]:
            time.sleep(random.uniform(1, 2))
    
    return results

def main():
    parser = argparse.ArgumentParser(description='AI 内容聚合搜索工具 v3 - 增强反爬版')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('--platforms', '-p', help='指定平台，逗号分隔 (reddit,zhihu,hackernews,github,youtube,producthunt,medium)')
    parser.add_argument('--json', '-j', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    platforms = args.platforms.split(',') if args.platforms else None
    
    print(f"\n🔍 开始搜索: {args.query}")
    print("=" * 80)
    
    results = aggregate_search(args.query, platforms)
    
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print("\n" + "=" * 80)
        
        total = 0
        for platform, items in results.items():
            print(f"\n📌 {platform.upper()}")
            print("-" * 80)
            
            if not items:
                print("  暂无结果")
                continue
            
            if 'error' in items[0]:
                print(f"  ❌ {items[0].get('error', '搜索失败')}")
                continue
            
            for i, item in enumerate(items[:5], 1):
                print(f"\n  {i}. {item.get('title', 'N/A')}")
                print(f"     🔗 {item.get('url', 'N/A')}")
                total += 1
        
        print("\n" + "=" * 80)
        print(f"\n✅ 共找到 {total} 条结果")
        print(f"⏰ 搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()