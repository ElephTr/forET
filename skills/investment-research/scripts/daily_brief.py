#!/usr/bin/env python3
"""
Investment Research - Daily Market Brief Generator
生成每日市场简报
"""

import json
import requests
from datetime import datetime, timedelta
import sys

# 配置
YAHOO_BASE = "https://query1.finance.yahoo.com/v8/finance/chart/"

# 主要指数
INDICES = {
    "标普500": "^GSPC",
    "纳斯达克": "^IXIC",
    "道琼斯": "^DJI",
    "上证指数": "000001.SS",
    "恒生指数": "^HSI",
    "日经225": "^N225",
    "美元指数": "DX-Y.NYB",
    "黄金": "GC=F",
    "原油": "CL=F",
    "比特币": "BTC-USD",
    "VIX": "^VIX"
}

def get_quote(symbol):
    """获取单个标的价格"""
    try:
        url = f"{YAHOO_BASE}{symbol}?interval=1d&range=5d"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        result = data["chart"]["result"][0]
        meta = result["meta"]
        timestamps = result["timestamp"]
        closes = result["indicators"]["quote"][0]["close"]
        
        # 获取最新和前一天收盘价
        latest_price = closes[-1]
        prev_price = closes[-2] if len(closes) > 1 else closes[-1]
        change = latest_price - prev_price
        change_pct = (change / prev_price) * 100
        
        return {
            "price": round(latest_price, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2)
        }
    except Exception as e:
        return {"error": str(e)}

def generate_brief():
    """生成市场简报"""
    print("📊 每日市场简报")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    print("\n🌍 全球主要指数:")
    print("-" * 50)
    
    for name, symbol in INDICES.items():
        data = get_quote(symbol)
        if "error" not in data:
            emoji = "🟢" if data["change"] >= 0 else "🔴"
            print(f"{emoji} {name:12} {data['price']:>10}  {data['change']:>+7.2f} ({data['change_pct']:>+.2f}%)")
        else:
            print(f"⚪ {name:12} 数据获取失败")
    
    print("\n" + "=" * 50)
    print("\n💡 今日关注:")
    print("  • 检查晚间美股走势对次日A股影响")
    print("  • 关注北向资金流向")
    print("  • 留意重要经济数据发布")
    print("\n⚠️  风险提示: 以上数据仅供参考，不构成投资建议")

if __name__ == "__main__":
    generate_brief()
