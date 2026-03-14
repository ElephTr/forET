#!/usr/bin/env python3
"""
AI 内容聚合搜索工具 v2
使用 DuckDuckGo 作为搜索源，支持多平台搜索
"""

import argparse
import json
import urllib.request
import urllib.parse
import re
import ssl

# 禁用 SSL 验证（某些环境需要）
ssl._create_default_https_context = ssl._create_unverified_context

def search_duckduckgo(query, site=None):
    """使用 DuckDuckGo 搜索"""
    try:
        if site:
            search_query = f"site:{site} {query}"
        else:
            search_query = query
            
        encoded_query = urllib.parse.quote(search_query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
        
        results = []
        # 提取搜索结果
        pattern = r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
        matches = re.findall(pattern, html, re.DOTALL)[:10]
        
        for match in matches:
            link = match[0]
            # 解码 DuckDuckGo 跳转链接
            if 'duckduckgo.com/l/?' in link:
                uddg_match = re.search(r'uddg=([^&]+)', link)
                if uddg_match:
                    link = urllib.parse.unquote(uddg_match.group(1))
            
            title = re.sub(r'<[^>]+>', '', match[1]).strip()
            
            if title and len(title) > 5:
                results.append({
                    'title': title,
                    'url': link
                })
        
        return results
    except Exception as e:
        return [{'error': str(e)}]

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
    
    site = site_map.get(platform)
    if not site:
        return []
    
    results = search_duckduckgo(query, site)
    
    # 添加平台标识
    for item in results:
        if 'error' not in item:
            item['platform'] = platform.upper()
            item['source'] = site
    
    return results

def aggregate_search(query, platforms=None):
    """聚合搜索"""
    all_platforms = ['reddit', 'zhihu', 'youtube', 'github', 'hackernews', 'producthunt', 'medium']
    
    if platforms:
        selected = [p for p in platforms if p in all_platforms]
    else:
        selected = all_platforms
    
    results = {}
    for platform in selected:
        print(f"🔍 搜索 {platform}...")
        results[platform] = search_platform(query, platform)
    
    return results

def main():
    parser = argparse.ArgumentParser(description='AI 内容聚合搜索工具 v2')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('--platforms', '-p', help='指定平台，逗号分隔')
    parser.add_argument('--json', '-j', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    platforms = args.platforms.split(',') if args.platforms else None
    
    results = aggregate_search(args.query, platforms)
    
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"\n🔍 搜索结果: {args.query}\n")
        print("=" * 80)
        
        total = 0
        for platform, items in results.items():
            print(f"\n📌 {platform.upper()}")
            print("-" * 80)
            
            if not items:
                print("  暂无结果")
                continue
            
            if 'error' in items[0]:
                print(f"  ❌ 搜索失败")
                continue
            
            for i, item in enumerate(items[:5], 1):
                print(f"\n  {i}. {item.get('title', 'N/A')}")
                print(f"     🔗 {item.get('url', 'N/A')}")
                total += 1
        
        print("\n" + "=" * 80)
        print(f"\n✅ 共找到 {total} 条结果")

if __name__ == '__main__':
    main()