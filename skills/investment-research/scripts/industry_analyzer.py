#!/usr/bin/env python3
"""
行业与市场影响分析模块
提供具体的数据支撑和行业逻辑
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class SectorData:
    """行业数据"""
    name: str
    symbol: str  # ETF代码
    change_pct: float
    volume: Optional[float]
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None

@dataclass
class MacroToSectorImpact:
    """宏观到行业的影响"""
    macro_factor: str
    affected_sectors: List[str]
    direction: str  # positive/negative
    mechanism: str  # 传导机制
    confidence: str  # high/medium/low

class IndustryImpactAnalyzer:
    """行业影响分析器"""
    
    # 美股行业ETF
    US_SECTOR_ETFS = {
        "科技": {"symbol": "XLK", "name": "Technology Select Sector SPDR"},
        "金融": {"symbol": "XLF", "name": "Financial Select Sector SPDR"},
        "医疗": {"symbol": "XLV", "name": "Health Care Select Sector SPDR"},
        "消费非必需": {"symbol": "XLY", "name": "Consumer Discretionary SPDR"},
        "消费必需": {"symbol": "XLP", "name": "Consumer Staples SPDR"},
        "能源": {"symbol": "XLE", "name": "Energy Select Sector SPDR"},
        "工业": {"symbol": "XLI", "name": "Industrial Select Sector SPDR"},
        "材料": {"symbol": "XLB", "name": "Materials Select Sector SPDR"},
        "公用事业": {"symbol": "XLU", "name": "Utilities Select Sector SPDR"},
        "房地产": {"symbol": "XLRE", "name": "Real Estate Select Sector SPDR"},
        "通信": {"symbol": "XLC", "name": "Communication Services SPDR"},
    }
    
    # 风格ETF
    STYLE_ETFS = {
        "大盘价值": {"symbol": "VTV", "name": "Vanguard Value ETF"},
        "大盘成长": {"symbol": "VUG", "name": "Vanguard Growth ETF"},
        "小盘价值": {"symbol": "VBR", "name": "Vanguard Small-Cap Value"},
        "小盘成长": {"symbol": "VBK", "name": "Vanguard Small-Cap Growth"},
    }
    
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"
        
    def fetch_etf_data(self, symbol: str) -> Optional[Dict]:
        """获取ETF数据"""
        try:
            url = f"{self.base_url}{symbol}?interval=1d&range=5d"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            
            if "chart" not in data or "result" not in data["chart"] or not data["chart"]["result"]:
                return None
                
            result = data["chart"]["result"][0]
            closes = result["indicators"]["quote"][0]["close"]
            volumes = result["indicators"]["quote"][0].get("volume", [])
            
            latest_price = closes[-1]
            prev_price = closes[-2] if len(closes) > 1 else closes[-1]
            change_pct = ((latest_price - prev_price) / prev_price) * 100
            
            return {
                "price": latest_price,
                "change_pct": change_pct,
                "volume": volumes[-1] if volumes else None
            }
        except Exception as e:
            return None
            
    def get_sector_performance(self, max_etfs: int = 6) -> Dict[str, SectorData]:
        """获取各行业表现（限制数量以加快速度）"""
        sectors = {}
        
        # 只获取关键行业
        key_sectors = list(self.US_SECTOR_ETFS.items())[:max_etfs]
        
        for sector_name, info in key_sectors:
            data = self.fetch_etf_data(info["symbol"])
            if data:
                sectors[sector_name] = SectorData(
                    name=sector_name,
                    symbol=info["symbol"],
                    change_pct=data["change_pct"],
                    volume=data["volume"]
                )
                
        return sectors
        
    def get_style_performance(self) -> Dict[str, Dict]:
        """获取风格表现"""
        styles = {}
        
        for style_name, info in self.STYLE_ETFS.items():
            data = self.fetch_etf_data(info["symbol"])
            if data:
                styles[style_name] = {
                    "name": style_name,
                    "change_pct": data["change_pct"]
                }
                
        return styles
        
    def analyze_macro_to_sector_impact(self, 
                                       vix_level: float,
                                       yield_curve_status: str,
                                       market_regime: str) -> List[MacroToSectorImpact]:
        """分析宏观因素对行业的影响"""
        impacts = []
        
        # 1. VIX/波动率影响
        if vix_level > 25:
            impacts.append(MacroToSectorImpact(
                macro_factor=f"VIX飙升至{vix_level:.1f}",
                affected_sectors=["科技", "生物制药", "新兴市场"],
                direction="negative",
                mechanism="高估值成长股对风险情绪敏感，波动率上升导致估值压缩",
                confidence="high"
            ))
            impacts.append(MacroToSectorImpact(
                macro_factor=f"VIX飙升至{vix_level:.1f}",
                affected_sectors=["公用事业", "消费必需", "黄金"],
                direction="positive",
                mechanism="避险需求上升，资金流入防御性板块",
                confidence="high"
            ))
            
        # 2. 收益率曲线影响
        if yield_curve_status == "inverted":
            impacts.append(MacroToSectorImpact(
                macro_factor="收益率曲线倒挂",
                affected_sectors=["银行", "房地产"],
                direction="negative",
                mechanism="利差收窄压缩银行净息差，衰退预期压制信贷需求",
                confidence="high"
            ))
            impacts.append(MacroToSectorImpact(
                macro_factor="收益率曲线倒挂",
                affected_sectors=["长期国债", "高股息股票"],
                direction="positive",
                mechanism="降息预期升温，长久期资产受益",
                confidence="medium"
            ))
            
        # 3. 市场状态影响
        if market_regime == "risk_off":
            impacts.append(MacroToSectorImpact(
                macro_factor="全球风险规避",
                affected_sectors=["半导体", "奢侈品", "工业"],
                direction="negative",
                mechanism="周期股和可选消费对经济增长敏感，衰退担忧压制盈利预期",
                confidence="high"
            ))
            
        return impacts
        
    def analyze_commodity_impact(self, oil_change: float, gold_change: float) -> List[Dict]:
        """分析大宗商品对行业的影响"""
        impacts = []
        
        # 原油影响
        if abs(oil_change) > 5:
            direction = "上涨" if oil_change > 0 else "下跌"
            impacts.append({
                "commodity": f"原油{direction} {abs(oil_change):.1f}%",
                "positive_sectors": ["能源", "油气设备", "油轮运输"] if oil_change > 0 else ["航空", "化工", "物流"],
                "negative_sectors": ["航空", "化工", "物流"] if oil_change > 0 else ["能源", "油气设备"],
                "mechanism": f"油价{direction}直接影响能源企业盈利和下游成本" if oil_change > 0 else f"油价{direction}降低下游成本但压制上游投资",
                "confidence": "high"
            })
            
        # 黄金影响
        if abs(gold_change) > 2:
            direction = "上涨" if gold_change > 0 else "下跌"
            impacts.append({
                "commodity": f"黄金{direction} {abs(gold_change):.1f}%",
                "positive_sectors": ["黄金矿业", "贵金属"] if gold_change > 0 else [],
                "negative_sectors": [],
                "mechanism": "金价上涨提升金矿企业盈利预期，反映避险需求",
                "confidence": "medium"
            })
            
        return impacts
        
    def generate_sector_rotation_analysis(self) -> Dict:
        """生成板块轮动分析"""
        sectors = self.get_sector_performance()
        styles = self.get_style_performance()
        
        if not sectors:
            return {"error": "无法获取行业数据"}
            
        # 排序
        sorted_sectors = sorted(sectors.items(), key=lambda x: x[1].change_pct, reverse=True)
        
        # 分类
        outperformers = [(name, data) for name, data in sorted_sectors if data.change_pct > 0]
        underperformers = [(name, data) for name, data in sorted_sectors if data.change_pct <= 0]
        
        # 风格判断
        style_analysis = {}
        if styles:
            value_change = styles.get("大盘价值", {}).get("change_pct", 0)
            growth_change = styles.get("大盘成长", {}).get("change_pct", 0)
            style_analysis = {
                "value_vs_growth": "价值占优" if value_change > growth_change else "成长占优",
                "value_change": value_change,
                "growth_change": growth_change
            }
            
        return {
            "top_performers": outperformers[:3],
            "bottom_performers": underperformers[-3:] if underperformers else [],
            "style_analysis": style_analysis,
            "all_sectors": sorted_sectors
        }
        
    def generate_impact_report(self, 
                              vix_level: float = 20,
                              yield_curve_status: str = "normal",
                              market_regime: str = "mixed",
                              oil_change: float = 0,
                              gold_change: float = 0) -> str:
        """生成行业影响报告"""
        lines = []
        lines.append("=" * 70)
        lines.append("📊 行业与市场影响分析")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 70)
        
        # 1. 板块表现
        lines.append("\n📈 板块表现排名")
        lines.append("-" * 50)
        rotation = self.generate_sector_rotation_analysis()
        
        if "error" in rotation:
            lines.append(f"  ⚪ {rotation['error']}")
        else:
            lines.append("\n🟢 领涨板块:")
            for name, data in rotation["top_performers"]:
                lines.append(f"  {name:12} {data.symbol:6}  {data.change_pct:>+.2f}%")
                
            lines.append("\n🔴 领跌板块:")
            for name, data in rotation["bottom_performers"]:
                lines.append(f"  {name:12} {data.symbol:6}  {data.change_pct:>+.2f}%")
                
            # 风格分析
            if rotation["style_analysis"]:
                sa = rotation["style_analysis"]
                lines.append(f"\n📊 风格轮动:")
                lines.append(f"  {sa['value_vs_growth']}")
                lines.append(f"  价值: {sa.get('value_change', 0):+.2f}% | 成长: {sa.get('growth_change', 0):+.2f}%")
        
        # 2. 宏观影响
        lines.append("\n" + "=" * 70)
        lines.append("🎯 宏观因素 → 行业影响")
        lines.append("=" * 70)
        
        macro_impacts = self.analyze_macro_to_sector_impact(
            vix_level, yield_curve_status, market_regime
        )
        
        if macro_impacts:
            for impact in macro_impacts:
                emoji = "🟢" if impact.direction == "positive" else "🔴"
                lines.append(f"\n{emoji} {impact.macro_factor}")
                lines.append(f"   影响行业: {', '.join(impact.affected_sectors)}")
                lines.append(f"   传导机制: {impact.mechanism}")
                lines.append(f"   置信度: {impact.confidence}")
        else:
            lines.append("\n  ⚪ 当前宏观环境对行业影响中性")
            
        # 3. 商品影响
        commodity_impacts = self.analyze_commodity_impact(oil_change, gold_change)
        
        if commodity_impacts:
            lines.append("\n" + "=" * 70)
            lines.append("⛽ 大宗商品 → 行业影响")
            lines.append("=" * 70)
            
            for impact in commodity_impacts:
                lines.append(f"\n📌 {impact['commodity']}")
                if impact['positive_sectors']:
                    lines.append(f"   🟢 受益: {', '.join(impact['positive_sectors'])}")
                if impact['negative_sectors']:
                    lines.append(f"   🔴 承压: {', '.join(impact['negative_sectors'])}")
                lines.append(f"   逻辑: {impact['mechanism']}")
        
        # 4. 具体投资建议
        lines.append("\n" + "=" * 70)
        lines.append("💡 基于行业逻辑的投资思考")
        lines.append("=" * 70)
        
        if vix_level > 25:
            lines.append("\n🔍 高波动环境下的行业选择:")
            lines.append("  • 防御性配置: 公用事业、消费必需、医疗")
            lines.append("    └─ 原因: 盈利稳定，股息率高，波动率低")
            lines.append("  • 回避: 高估值科技、生物制药、新兴市场")
            lines.append("    └─ 原因: 对贴现率敏感，估值压缩风险大")
            
        if yield_curve_status == "inverted":
            lines.append("\n🔍 收益率曲线倒挂下的行业选择:")
            lines.append("  • 受益: 长期国债、高股息公用事业")
            lines.append("    └─ 原因: 降息预期升温，长久期资产受益")
            lines.append("  • 回避: 银行、商业地产")
            lines.append("    └─ 原因: 利差收窄，信贷需求下降")
            
        if oil_change > 10:
            lines.append("\n🔍 高油价环境下的行业选择:")
            lines.append("  • 受益: 能源企业、油气设备、替代能源")
            lines.append("    └─ 原因: 现金流改善，资本开支增加")
            lines.append("  • 受损: 航空、航运、化工")
            lines.append("    └─ 原因: 成本上升，利润率压缩")
        
        lines.append("\n" + "=" * 70)
        lines.append("⚠️  免责声明: 以上分析基于公开数据，不构成投资建议")
        lines.append("=" * 70)
        
        return "\n".join(lines)

if __name__ == "__main__":
    analyzer = IndustryImpactAnalyzer()
    
    # 测试报告
    print(analyzer.generate_impact_report(
        vix_level=29.5,
        yield_curve_status="inverted",
        market_regime="risk_off",
        oil_change=26,
        gold_change=-0.9
    ))
