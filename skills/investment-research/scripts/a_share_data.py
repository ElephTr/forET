#!/usr/bin/env python3
"""
A股市场数据获取模块 (简化版)
使用新浪财经API（更稳定）
"""

import requests
import json
from datetime import datetime
from typing import Dict, Optional

class AShareDataSource:
    """A股数据源 - 新浪财经"""
    
    def __init__(self):
        self.timeout = 10
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://finance.sina.com.cn"
        }
        
    def get_northbound_flow(self) -> Optional[Dict]:
        """
        获取北向资金流向
        使用新浪财经港股通数据
        """
        try:
            # 新浪财经北向资金API
            url = "https://quotes.sina.cn/cn/api/quotes.php"
            params = {
                "symbol": "sh000001",  # 上证指数
                "_": int(datetime.now().timestamp() * 1000)
            }
            
            # 简化处理，返回模拟数据框架
            # 实际生产环境应该接入Wind/同花顺iFinD等专业数据
            return {
                "name": "北向资金",
                "status": "需专业数据源",
                "signal": "⚪ 接入Wind/iFinD获取实时数据",
                "note": "新浪财经API不稳定，建议使用专业金融数据终端"
            }
        except Exception as e:
            return None
            
    def get_margin_balance(self) -> Optional[Dict]:
        """融资余额数据"""
        return {
            "name": "融资余额",
            "status": "需专业数据源",
            "signal": "⚪ 接入Wind/iFinD获取实时数据"
        }
        
    def get_market_sentiment_indicators(self) -> Dict:
        """
        获取A股情绪指标（综合）
        基于已有市场数据计算
        """
        try:
            # 通过上证指数数据计算情绪
            url = "https://hq.sinajs.cn/list=s_sh000001"
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            # 解析数据
            data = resp.text
            if "var hq_str_s_sh000001" in data:
                # 格式: var hq_str_s_sh000001="上证指数,点数,涨跌,涨跌幅,成交量,成交额";
                parts = data.split('"')[1].split(',')
                if len(parts) >= 6:
                    index_name = parts[0]
                    price = float(parts[1])
                    change = float(parts[2])
                    change_pct = float(parts[3])
                    volume = float(parts[4])  # 手
                    turnover = float(parts[5])  # 万元
                    
                    # 简单情绪判断
                    if change_pct > 2:
                        sentiment = "极度乐观"
                        signal = "🔴 过热，注意风险"
                    elif change_pct > 1:
                        sentiment = "乐观"
                        signal = "🟡 偏热"
                    elif change_pct > -1:
                        sentiment = "中性"
                        signal = "⚪ 正常"
                    elif change_pct > -2:
                        sentiment = "悲观"
                        signal = "🟢 偏冷"
                    else:
                        sentiment = "极度悲观"
                        signal = "🟢🟢 恐慌，关注机会"
                        
                    return {
                        "index": index_name,
                        "price": price,
                        "change": change,
                        "change_pct": change_pct,
                        "sentiment": sentiment,
                        "signal": signal,
                        "turnover": turnover / 1e4  # 转换为亿元
                    }
        except Exception as e:
            pass
            
        return {
            "index": "上证指数",
            "sentiment": "未知",
            "signal": "⚪ 数据获取失败"
        }

if __name__ == "__main__":
    source = AShareDataSource()
    
    print("🇨🇳 A股市场情绪")
    print("=" * 50)
    
    sentiment = source.get_market_sentiment_indicators()
    print(f"\n{sentiment['index']}: {sentiment.get('price', 'N/A')}")
    if 'change_pct' in sentiment:
        emoji = "🟢" if sentiment['change_pct'] >= 0 else "🔴"
        print(f"  涨跌: {emoji} {sentiment['change_pct']:+.2f}%")
    print(f"  情绪: {sentiment['sentiment']}")
    print(f"  信号: {sentiment['signal']}")
    
    print("\n💡 提示:")
    print("  • 完整A股数据需要接入专业金融终端")
    print("  • 推荐: Wind、同花顺iFinD、Choice")
    print("  • 北向资金、融资余额等需付费API")
