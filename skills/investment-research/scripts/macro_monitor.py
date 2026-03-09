#!/usr/bin/env python3
"""
宏观数据监控模块
跟踪关键经济指标和央行政策
"""

import requests
import json
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass

@dataclass
class MacroIndicator:
    """宏观经济指标"""
    name: str
    value: float
    previous: float
    change_pct: float
    source: str
    last_update: str
    frequency: str  # daily, weekly, monthly, quarterly
    importance: int  # 1-5, 5最高
    
class MacroDataMonitor:
    """宏观数据监控器"""
    
    # 关键宏观指标配置
    INDICATORS = {
        # 美国 - 利率
        "US_FED_RATE": {
            "name": "美联储基准利率",
            "symbol": "FEDFUNDS",
            "source": "fred",
            "frequency": "daily",
            "importance": 5
        },
        "US_10Y_YIELD": {
            "name": "美国10年期国债收益率",
            "symbol": "DGS10",
            "source": "fred",
            "frequency": "daily",
            "importance": 5
        },
        "US_2Y_YIELD": {
            "name": "美国2年期国债收益率",
            "symbol": "DGS2",
            "source": "fred",
            "frequency": "daily",
            "importance": 5
        },
        "US_10Y_2Y_SPREAD": {
            "name": "美债10Y-2Y利差",
            "symbol": "T10Y2Y",
            "source": "fred",
            "frequency": "daily",
            "importance": 5
        },
        
        # 美国 - 通胀与就业
        "US_CPI": {
            "name": "美国CPI同比",
            "symbol": "CPIAUCSL",
            "source": "fred",
            "frequency": "monthly",
            "importance": 5
        },
        "US_CORE_CPI": {
            "name": "美国核心CPI同比",
            "symbol": "CPILFESL",
            "source": "fred",
            "frequency": "monthly",
            "importance": 5
        },
        "US_UNEMPLOYMENT": {
            "name": "美国失业率",
            "symbol": "UNRATE",
            "source": "fred",
            "frequency": "monthly",
            "importance": 5
        },
        "US_NONFARM": {
            "name": "美国非农就业",
            "symbol": "PAYEMS",
            "source": "fred",
            "frequency": "monthly",
            "importance": 5
        },
        
        # 美国 - 经济活动
        "US_GDP": {
            "name": "美国实际GDP",
            "symbol": "GDPC1",
            "source": "fred",
            "frequency": "quarterly",
            "importance": 5
        },
        "US_LEADING": {
            "name": "美国领先经济指标",
            "symbol": "USSLIND",
            "source": "fred",
            "frequency": "monthly",
            "importance": 4
        },
        
        # 中国
        "CN_LPR_1Y": {
            "name": "中国1年期LPR",
            "symbol": "CHINA_LPR_1Y",
            "source": "manual",
            "frequency": "monthly",
            "importance": 5
        },
        "CN_LPR_5Y": {
            "name": "中国5年期LPR",
            "symbol": "CHINA_LPR_5Y",
            "source": "manual",
            "frequency": "monthly",
            "importance": 5
        },
        "CN_CPI": {
            "name": "中国CPI同比",
            "symbol": "CHNCPIALLMINMEI",
            "source": "fred",
            "frequency": "monthly",
            "importance": 4
        },
        "CN_PMI": {
            "name": "中国制造业PMI",
            "symbol": "CHNPMI",
            "source": "manual",
            "frequency": "monthly",
            "importance": 4
        },
        
        # 欧洲
        "ECB_RATE": {
            "name": "欧洲央行基准利率",
            "symbol": "ECBDFR",
            "source": "fred",
            "frequency": "daily",
            "importance": 4
        },
        "EU_CPI": {
            "name": "欧元区CPI同比",
            "symbol": "EA19CPALTT01IXOBM",
            "source": "fred",
            "frequency": "monthly",
            "importance": 4
        },
        
        # 日本
        "BOJ_RATE": {
            "name": "日本央行政策利率",
            "symbol": "IRSTCB01JPM156N",
            "source": "fred",
            "frequency": "daily",
            "importance": 4
        },
        
        # 全球流动性
        "US_M2": {
            "name": "美国M2货币供应",
            "symbol": "M2SL",
            "source": "fred",
            "frequency": "weekly",
            "importance": 4
        },
        "FED_BALANCE_SHEET": {
            "name": "美联储资产负债表",
            "symbol": "WALCL",
            "source": "fred",
            "frequency": "weekly",
            "importance": 4
        },
    }
    
    def __init__(self, fred_api_key: Optional[str] = None):
        self.fred_api_key = fred_api_key
        self.fred_base = "https://api.stlouisfed.org/fred"
        
    def fetch_fred_data(self, series_id: str) -> Optional[Dict]:
        """从FRED获取数据"""
        if not self.fred_api_key:
            return None
            
        try:
            url = f"{self.fred_base}/series/observations"
            params = {
                "series_id": series_id,
                "api_key": self.fred_api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 5  # 获取最近5个数据点
            }
            resp = requests.get(url, params=params, timeout=15)
            data = resp.json()
            
            if "observations" not in data or len(data["observations"]) < 2:
                return None
                
            # 获取最新和上一期数据
            observations = [o for o in data["observations"] if o.get("value") != "."]
            if len(observations) < 2:
                return None
                
            latest = observations[0]
            previous = observations[1]
            
            latest_val = float(latest["value"])
            prev_val = float(previous["value"])
            change_pct = ((latest_val - prev_val) / abs(prev_val)) * 100 if prev_val != 0 else 0
            
            return {
                "value": latest_val,
                "previous": prev_val,
                "change_pct": change_pct,
                "date": latest["date"],
                "source": "FRED"
            }
        except Exception as e:
            print(f"Error fetching FRED data for {series_id}: {e}")
            return None
            
    def get_indicator(self, indicator_id: str) -> Optional[MacroIndicator]:
        """获取单个指标数据"""
        if indicator_id not in self.INDICATORS:
            return None
            
        config = self.INDICATORS[indicator_id]
        
        if config["source"] == "fred":
            data = self.fetch_fred_data(config["symbol"])
        else:
            # manual 或其他来源，需要额外实现
            data = None
            
        if not data:
            return None
            
        return MacroIndicator(
            name=config["name"],
            value=data["value"],
            previous=data["previous"],
            change_pct=data["change_pct"],
            source=data["source"],
            last_update=data["date"],
            frequency=config["frequency"],
            importance=config["importance"]
        )
        
    def get_all_indicators(self) -> Dict[str, MacroIndicator]:
        """获取所有指标"""
        results = {}
        for indicator_id in self.INDICATORS:
            indicator = self.get_indicator(indicator_id)
            if indicator:
                results[indicator_id] = indicator
        return results
        
    def get_key_rates_summary(self) -> Dict:
        """获取关键利率汇总"""
        key_rates = [
            "US_FED_RATE", "US_10Y_YIELD", "US_2Y_YIELD", "US_10Y_2Y_SPREAD",
            "ECB_RATE", "BOJ_RATE"
        ]
        
        results = {}
        for rate_id in key_rates:
            indicator = self.get_indicator(rate_id)
            if indicator:
                results[rate_id] = indicator
                
        return results
        
    def get_inflation_summary(self) -> Dict:
        """获取通胀指标汇总"""
        inflation_ids = ["US_CPI", "US_CORE_CPI", "EU_CPI", "CN_CPI"]
        
        results = {}
        for inf_id in inflation_ids:
            indicator = self.get_indicator(inf_id)
            if indicator:
                results[inf_id] = indicator
                
        return results
        
    def analyze_yield_curve(self) -> Dict:
        """分析收益率曲线"""
        spread = self.get_indicator("US_10Y_2Y_SPREAD")
        
        if not spread:
            return {"status": "unknown", "message": "无法获取收益率曲线数据"}
            
        status = "normal" if spread.value > 0 else "inverted"
        
        return {
            "status": status,
            "spread": spread.value,
            "change_pct": spread.change_pct,
            "signal": "⚠️ 倒挂" if status == "inverted" else "✓ 正常",
            "interpretation": {
                "normal": "收益率曲线正常，经济扩张期",
                "inverted": "收益率曲线倒挂，历史上预示衰退风险"
            }.get(status, "未知")
        }
        
    def get_liquidity_summary(self) -> Dict:
        """获取流动性指标汇总"""
        liquidity_ids = ["FED_BALANCE_SHEET", "US_M2"]
        
        results = {}
        for liq_id in liquidity_ids:
            indicator = self.get_indicator(liq_id)
            if indicator:
                results[liq_id] = indicator
                
        return results

def format_macro_report(monitor: MacroDataMonitor) -> str:
    """格式化宏观数据报告"""
    lines = []
    lines.append("📊 宏观数据监控报告")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 60)
    
    # 收益率曲线分析
    lines.append("\n🏛️  收益率曲线与衰退风险")
    lines.append("-" * 40)
    yield_analysis = monitor.analyze_yield_curve()
    lines.append(f"  10Y-2Y利差: {yield_analysis['spread']:.2f}% ({yield_analysis['change_pct']:+.2f}%)")
    lines.append(f"  状态: {yield_analysis['signal']}")
    lines.append(f"  解读: {yield_analysis['interpretation']}")
    
    # 关键利率
    lines.append("\n💰 关键利率水平")
    lines.append("-" * 40)
    rates = monitor.get_key_rates_summary()
    for rate_id, indicator in rates.items():
        emoji = "🟢" if indicator.change_pct >= 0 else "🔴"
        lines.append(f"  {emoji} {indicator.name:20} {indicator.value:>6.2f}% ({indicator.change_pct:>+.2f}%)")
        
    # 通胀数据
    lines.append("\n📈 通胀指标")
    lines.append("-" * 40)
    inflation = monitor.get_inflation_summary()
    for inf_id, indicator in inflation.items():
        emoji = "🔴" if indicator.value > 2.0 else "🟡" if indicator.value > 1.0 else "🟢"
        lines.append(f"  {emoji} {indicator.name:20} {indicator.value:>6.2f}% ({indicator.change_pct:>+.2f}%)")
        
    # 流动性
    lines.append("\n💧 流动性状况")
    lines.append("-" * 40)
    liquidity = monitor.get_liquidity_summary()
    for liq_id, indicator in liquidity.items():
        emoji = "🟢" if indicator.change_pct >= 0 else "🔴"
        # 格式化大数字
        if indicator.value > 1e9:
            val_str = f"${indicator.value/1e9:.2f}T"
        elif indicator.value > 1e6:
            val_str = f"${indicator.value/1e6:.2f}B"
        else:
            val_str = f"{indicator.value:.2f}"
        lines.append(f"  {emoji} {indicator.name:20} {val_str:>10} ({indicator.change_pct:>+.2f}%)")
    
    lines.append("\n" + "=" * 60)
    lines.append("⚠️  数据来源: FRED (Federal Reserve Economic Data)")
    lines.append("   需要FRED API Key才能获取完整数据")
    
    return "\n".join(lines)

if __name__ == "__main__":
    # 测试（不需要API Key会显示提示）
    monitor = MacroDataMonitor()
    
    print(format_macro_report(monitor))
    
    print("\n\n💡 提示: 设置FRED_API_KEY环境变量可获取完整宏观数据")
    print("   获取API Key: https://fred.stlouisfed.org/docs/api/api_key.html")
