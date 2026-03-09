#!/usr/bin/env python3
"""
全球市场数据聚合器
多源获取 + 交叉验证 + 可信度评分
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class DataPoint:
    """带可信度评分的数据点"""
    value: float
    source: str
    timestamp: datetime
    confidence: int  # 0-100
    is_verified: bool = False
    
@dataclass
class MarketData:
    """市场数据对象"""
    symbol: str
    name: str
    price: Optional[DataPoint] = None
    change: Optional[DataPoint] = None
    change_pct: Optional[DataPoint] = None
    volume: Optional[DataPoint] = None
    
class DataSource:
    """数据源基类"""
    def __init__(self, name: str, priority: int = 50):
        self.name = name
        self.priority = priority
        self.timeout = 10
        
    def fetch(self, symbol: str) -> Optional[Dict]:
        raise NotImplementedError
        
class YahooFinanceSource(DataSource):
    """Yahoo Finance 数据源"""
    def __init__(self):
        super().__init__("Yahoo Finance", 80)
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"
        
    def fetch(self, symbol: str) -> Optional[Dict]:
        try:
            url = f"{self.base_url}{symbol}?interval=1d&range=5d"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            resp = requests.get(url, headers=headers, timeout=self.timeout)
            data = resp.json()
            
            if "chart" not in data or "result" not in data["chart"] or not data["chart"]["result"]:
                return None
                
            result = data["chart"]["result"][0]
            meta = result["meta"]
            closes = result["indicators"]["quote"][0]["close"]
            volumes = result["indicators"]["quote"][0].get("volume", [])
            
            latest_price = closes[-1]
            prev_price = closes[-2] if len(closes) > 1 else closes[-1]
            change = latest_price - prev_price
            change_pct = (change / prev_price) * 100 if prev_price != 0 else 0
            
            return {
                "price": latest_price,
                "change": change,
                "change_pct": change_pct,
                "volume": volumes[-1] if volumes else None,
                "timestamp": datetime.now(),
                "source": self.name,
                "confidence": 80
            }
        except Exception as e:
            return None

class AlphaVantageSource(DataSource):
    """Alpha Vantage 数据源（需要API Key）"""
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Alpha Vantage", 85)
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        
    def fetch(self, symbol: str) -> Optional[Dict]:
        if not self.api_key:
            return None
        try:
            url = f"{self.base_url}?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.api_key}"
            resp = requests.get(url, timeout=self.timeout)
            data = resp.json()
            
            if "Global Quote" not in data:
                return None
                
            quote = data["Global Quote"]
            price = float(quote.get("05. price", 0))
            change = float(quote.get("09. change", 0))
            change_pct = float(quote.get("10. change percent", "0%").replace("%", ""))
            volume = int(quote.get("06. volume", 0))
            
            return {
                "price": price,
                "change": change,
                "change_pct": change_pct,
                "volume": volume,
                "timestamp": datetime.now(),
                "source": self.name,
                "confidence": 85
            }
        except Exception as e:
            return None

class EastMoneySource(DataSource):
    """东方财富数据源（A股）"""
    def __init__(self):
        super().__init__("东方财富", 75)
        
    def fetch(self, symbol: str) -> Optional[Dict]:
        # A股代码转换
        if symbol.endswith(".SS"):
            em_symbol = symbol.replace(".SS", "")
        elif symbol.endswith(".SZ"):
            em_symbol = symbol.replace(".SZ", "")
        else:
            return None
            
        try:
            # 东方财富API
            url = f"http://push2.eastmoney.com/api/qt/stock/get?secid=1.{em_symbol}&fields=f43,f44,f45,f46,f47,f48,f57,f58,f60,f170"
            resp = requests.get(url, timeout=self.timeout)
            data = resp.json()
            
            if "data" not in data or not data["data"]:
                return None
                
            d = data["data"]
            price = d.get("f43", 0) / 100 if d.get("f43") else 0
            prev_close = d.get("f60", 0) / 100 if d.get("f60") else 0
            change = price - prev_close
            change_pct = (change / prev_close * 100) if prev_close else 0
            volume = d.get("f47", 0)
            
            return {
                "price": price,
                "change": change,
                "change_pct": change_pct,
                "volume": volume,
                "timestamp": datetime.now(),
                "source": self.name,
                "confidence": 75
            }
        except Exception as e:
            return None

class CoinGeckoSource(DataSource):
    """CoinGecko 加密货币数据源"""
    def __init__(self):
        super().__init__("CoinGecko", 80)
        self.base_url = "https://api.coingecko.com/api/v3"
        
    def fetch(self, symbol: str) -> Optional[Dict]:
        # 转换 symbol (BTC-USD -> bitcoin)
        coin_map = {
            "BTC-USD": "bitcoin",
            "ETH-USD": "ethereum",
            "SOL-USD": "solana"
        }
        coin_id = coin_map.get(symbol)
        if not coin_id:
            return None
            
        try:
            url = f"{self.base_url}/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true"
            resp = requests.get(url, timeout=self.timeout)
            data = resp.json()
            
            if coin_id not in data:
                return None
                
            d = data[coin_id]
            price = d.get("usd", 0)
            change_pct = d.get("usd_24h_change", 0)
            volume = d.get("usd_24h_vol", 0)
            
            # 估算 change (从 percentage 反推)
            prev_price = price / (1 + change_pct/100) if change_pct != -100 else price
            change = price - prev_price
            
            return {
                "price": price,
                "change": change,
                "change_pct": change_pct,
                "volume": volume,
                "timestamp": datetime.now(),
                "source": self.name,
                "confidence": 80
            }
        except Exception as e:
            return None

class FredSource(DataSource):
    """FRED 宏观数据源"""
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("FRED", 95)
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred"
        
    def fetch(self, series_id: str) -> Optional[Dict]:
        if not self.api_key:
            return None
        try:
            url = f"{self.base_url}/series/observations?series_id={series_id}&api_key={self.api_key}&file_type=json&sort_order=desc&limit=2"
            resp = requests.get(url, timeout=self.timeout)
            data = resp.json()
            
            if "observations" not in data or len(data["observations"]) < 2:
                return None
                
            latest = data["observations"][0]
            prev = data["observations"][1]
            
            value = float(latest.get("value", 0)) if latest.get("value") != "." else 0
            prev_value = float(prev.get("value", 0)) if prev.get("value") != "." else 0
            change = value - prev_value
            change_pct = (change / prev_value * 100) if prev_value else 0
            
            return {
                "price": value,
                "change": change,
                "change_pct": change_pct,
                "volume": None,
                "timestamp": datetime.now(),
                "source": self.name,
                "confidence": 95
            }
        except Exception as e:
            return None

class GlobalMarketDataAggregator:
    """全球市场数据聚合器"""
    
    # 全球市场标的配置
    MARKETS = {
        # 美股
        "SP500": {"symbol": "^GSPC", "name": "标普500", "region": "US", "sources": ["yahoo", "av"]},
        "NASDAQ": {"symbol": "^IXIC", "name": "纳斯达克", "region": "US", "sources": ["yahoo", "av"]},
        "DJI": {"symbol": "^DJI", "name": "道琼斯", "region": "US", "sources": ["yahoo", "av"]},
        
        # A股
        "SH_COMP": {"symbol": "000001.SS", "name": "上证指数", "region": "CN", "sources": ["yahoo", "eastmoney"]},
        "SZ_COMP": {"symbol": "399001.SZ", "name": "深证成指", "region": "CN", "sources": ["yahoo", "eastmoney"]},
        "CSI300": {"symbol": "000300.SS", "name": "沪深300", "region": "CN", "sources": ["yahoo", "eastmoney"]},
        
        # 港股
        "HSI": {"symbol": "^HSI", "name": "恒生指数", "region": "HK", "sources": ["yahoo"]},
        "HS_TECH": {"symbol": "^HSTECH", "name": "恒生科技", "region": "HK", "sources": ["yahoo"]},
        
        # 亚太
        "NIKKEI": {"symbol": "^N225", "name": "日经225", "region": "JP", "sources": ["yahoo"]},
        "KOSPI": {"symbol": "^KS11", "name": "韩国KOSPI", "region": "KR", "sources": ["yahoo"]},
        "ASX": {"symbol": "^AXJO", "name": "澳洲ASX200", "region": "AU", "sources": ["yahoo"]},
        
        # 欧洲
        "FTSE": {"symbol": "^FTSE", "name": "英国富时100", "region": "UK", "sources": ["yahoo"]},
        "DAX": {"symbol": "^GDAXI", "name": "德国DAX", "region": "DE", "sources": ["yahoo"]},
        "CAC": {"symbol": "^FCHI", "name": "法国CAC40", "region": "FR", "sources": ["yahoo"]},
        "EUROSTOXX": {"symbol": "^STOXX50E", "name": "欧洲STOXX50", "region": "EU", "sources": ["yahoo"]},
        
        # 外汇
        "DXY": {"symbol": "DX-Y.NYB", "name": "美元指数", "region": "FX", "sources": ["yahoo"]},
        "EURUSD": {"symbol": "EURUSD=X", "name": "欧元/美元", "region": "FX", "sources": ["yahoo"]},
        "USDJPY": {"symbol": "JPY=X", "name": "美元/日元", "region": "FX", "sources": ["yahoo"]},
        "USDCNY": {"symbol": "CNY=X", "name": "美元/人民币", "region": "FX", "sources": ["yahoo"]},
        
        # 商品
        "GOLD": {"symbol": "GC=F", "name": "黄金", "region": "COMM", "sources": ["yahoo"]},
        "SILVER": {"symbol": "SI=F", "name": "白银", "region": "COMM", "sources": ["yahoo"]},
        "CRUDE": {"symbol": "CL=F", "name": "原油(WTI)", "region": "COMM", "sources": ["yahoo"]},
        "BRENT": {"symbol": "BZ=F", "name": "原油(布伦特)", "region": "COMM", "sources": ["yahoo"]},
        "COPPER": {"symbol": "HG=F", "name": "铜", "region": "COMM", "sources": ["yahoo"]},
        
        # 加密货币
        "BTC": {"symbol": "BTC-USD", "name": "比特币", "region": "CRYPTO", "sources": ["yahoo", "coingecko"]},
        "ETH": {"symbol": "ETH-USD", "name": "以太坊", "region": "CRYPTO", "sources": ["yahoo", "coingecko"]},
        
        # 波动率/情绪
        "VIX": {"symbol": "^VIX", "name": "VIX波动率", "region": "US", "sources": ["yahoo"]},
        "VXN": {"symbol": "^VXN", "name": "纳斯达克波动率", "region": "US", "sources": ["yahoo"]},
    }
    
    def __init__(self, alpha_vantage_key: Optional[str] = None, fred_key: Optional[str] = None):
        self.sources = {
            "yahoo": YahooFinanceSource(),
            "av": AlphaVantageSource(alpha_vantage_key),
            "eastmoney": EastMoneySource(),
            "coingecko": CoinGeckoSource(),
            "fred": FredSource(fred_key)
        }
        self.data_cache = {}
        self.cache_time = 60  # 缓存60秒
        
    def fetch_with_fallback(self, symbol: str, source_list: List[str]) -> Optional[Dict]:
        """多源获取，自动故障转移"""
        results = []
        
        for source_name in source_list:
            if source_name in self.sources:
                source = self.sources[source_name]
                result = source.fetch(symbol)
                if result:
                    results.append(result)
                    
        if not results:
            return None
            
        # 如果有多个结果，进行交叉验证
        if len(results) > 1:
            return self._validate_and_merge(results)
        else:
            return results[0]
            
    def _validate_and_merge(self, results: List[Dict]) -> Dict:
        """多源数据验证与合并"""
        # 按可信度排序
        results.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        # 取最高可信度的价格
        best = results[0]
        
        # 验证其他源是否一致（价格偏差<1%）
        verified = True
        for r in results[1:]:
            if r["price"] > 0:
                deviation = abs(r["price"] - best["price"]) / best["price"]
                if deviation > 0.01:  # 1%偏差阈值
                    verified = False
                    break
                    
        best["is_verified"] = verified
        best["sources_used"] = [r["source"] for r in results]
        
        return best
        
    def get_market_data(self, market_id: str) -> Optional[MarketData]:
        """获取指定市场数据"""
        if market_id not in self.MARKETS:
            return None
            
        config = self.MARKETS[market_id]
        symbol = config["symbol"]
        source_list = config["sources"]
        
        data = self.fetch_with_fallback(symbol, source_list)
        
        if not data:
            return None
            
        return MarketData(
            symbol=symbol,
            name=config["name"],
            price=DataPoint(
                value=data["price"],
                source=data["source"],
                timestamp=data["timestamp"],
                confidence=data["confidence"],
                is_verified=data.get("is_verified", False)
            ),
            change=DataPoint(
                value=data["change"],
                source=data["source"],
                timestamp=data["timestamp"],
                confidence=data["confidence"]
            ),
            change_pct=DataPoint(
                value=data["change_pct"],
                source=data["source"],
                timestamp=data["timestamp"],
                confidence=data["confidence"]
            ),
            volume=DataPoint(
                value=data["volume"] if data["volume"] else 0,
                source=data["source"],
                timestamp=data["timestamp"],
                confidence=data["confidence"]
            ) if data["volume"] else None
        )
        
    def get_all_markets(self, region_filter: Optional[str] = None) -> Dict[str, MarketData]:
        """获取所有市场数据（并行）"""
        results = {}
        
        markets_to_fetch = self.MARKETS
        if region_filter:
            markets_to_fetch = {k: v for k, v in self.MARKETS.items() 
                              if v["region"] == region_filter}
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_market = {
                executor.submit(self.get_market_data, market_id): market_id 
                for market_id in markets_to_fetch
            }
            
            for future in as_completed(future_to_market):
                market_id = future_to_market[future]
                try:
                    data = future.result()
                    if data:
                        results[market_id] = data
                except Exception as e:
                    print(f"Error fetching {market_id}: {e}")
                    
        return results
        
    def get_region_summary(self) -> Dict:
        """按地区汇总市场数据"""
        all_data = self.get_all_markets()
        
        regions = {
            "US": {"name": "美股", "markets": [], "avg_change": 0},
            "CN": {"name": "A股", "markets": [], "avg_change": 0},
            "HK": {"name": "港股", "markets": [], "avg_change": 0},
            "JP": {"name": "日本", "markets": [], "avg_change": 0},
            "EU": {"name": "欧洲", "markets": [], "avg_change": 0},
            "FX": {"name": "外汇", "markets": [], "avg_change": 0},
            "COMM": {"name": "商品", "markets": [], "avg_change": 0},
            "CRYPTO": {"name": "加密", "markets": [], "avg_change": 0},
        }
        
        for market_id, data in all_data.items():
            config = self.MARKETS[market_id]
            region = config["region"]
            if region in regions:
                regions[region]["markets"].append(data)
                
        # 计算各地区平均涨跌幅
        for region, info in regions.items():
            if info["markets"]:
                changes = [m.change_pct.value for m in info["markets"] if m.change_pct]
                if changes:
                    info["avg_change"] = sum(changes) / len(changes)
                    
        return regions

if __name__ == "__main__":
    # 测试
    aggregator = GlobalMarketDataAggregator()
    
    print("🌍 全球市场数据聚合器测试")
    print("=" * 60)
    
    # 获取地区汇总
    summary = aggregator.get_region_summary()
    
    for region, info in summary.items():
        if info["markets"]:
            emoji = "🟢" if info["avg_change"] >= 0 else "🔴"
            print(f"\n{emoji} {info['name']} (平均: {info['avg_change']:+.2f}%)")
            print("-" * 40)
            for market in info["markets"]:
                if market.change_pct:
                    e = "🟢" if market.change_pct.value >= 0 else "🔴"
                    verified = "✓" if market.price and market.price.is_verified else " "
                    print(f"  {e}{verified} {market.name:15} {market.price.value:>10.2f}  {market.change_pct.value:>+.2f}%")
