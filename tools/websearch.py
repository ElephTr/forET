#!/usr/bin/env python3
"""
Web search tool using ddgs (DuckDuckGo Search) library
"""
import sys
import json
from ddgs import DDGS

def search(query, max_results=5, region='zh-cn'):
    """Search using DuckDuckGo"""
    try:
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, region=region, max_results=max_results):
                results.append({
                    'title': r.get('title', ''),
                    'url': r.get('href', ''),
                    'snippet': r.get('body', '')
                })
            return results
    except Exception as e:
        return [{'error': str(e)}]

def search_news(query, max_results=5, region='zh-cn'):
    """Search news using DuckDuckGo"""
    try:
        with DDGS() as ddgs:
            results = []
            for r in ddgs.news(query, region=region, max_results=max_results):
                results.append({
                    'title': r.get('title', ''),
                    'url': r.get('url', ''),
                    'snippet': r.get('body', ''),
                    'source': r.get('source', ''),
                    'date': r.get('date', '')
                })
            return results
    except Exception as e:
        return [{'error': str(e)}]

def main():
    if len(sys.argv) < 2:
        print("Usage: websearch.py <query> [max_results] [--news]", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  websearch.py '上海 线下活动' 5", file=sys.stderr)
        print("  websearch.py 'AI 新闻' 10 --news", file=sys.stderr)
        sys.exit(1)
    
    query = sys.argv[1]
    max_results = 5
    is_news = False
    
    for arg in sys.argv[2:]:
        if arg == '--news':
            is_news = True
        elif arg.isdigit():
            max_results = int(arg)
    
    if is_news:
        results = search_news(query, max_results)
    else:
        results = search(query, max_results)
    
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
