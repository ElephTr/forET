#!/usr/bin/env python3
"""
投资分析引擎
整合市场数据、宏观数据、情绪指标，生成投资建议
"""

import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# 导入其他模块
sys.path.insert(0, '/root/.openclaw/workspace/skills/investment-research/scripts')
from global_market_aggregator import GlobalMarketDataAggregator
from macro_monitor import MacroDataMonitor, format_macro_report
from sentiment_monitor import MarketSentimentMonitor

class SignalType(Enum):
    STRONG_BUY = "强烈买入"
    BUY = "买入"
    HOLD = "持有"
    REDUCE = "减仓"
    SELL = "卖出"
    STRONG_SELL = "强烈卖出"
    
class ConfidenceLevel(Enum):
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"

@dataclass
class InvestmentSignal:
    """投资信号"""
    asset_class: str
    signal: SignalType
    confidence: ConfidenceLevel
    reasoning: List[str]
    risk_factors: List[str]
    time_horizon: str  # short, medium, long

class InvestmentAnalysisEngine:
    """投资分析引擎"""
    
    def __init__(self, fred_api_key: Optional[str] = None):
        self.market_agg = GlobalMarketDataAggregator()
        self.macro_monitor = MacroDataMonitor(fred_api_key)
        self.sentiment_monitor = MarketSentimentMonitor()
        
    def analyze_market_regime(self) -> Dict:
        """分析当前市场状态"""
        # 获取全球市场数据
        all_markets = self.market_agg.get_all_markets()
        
        # 计算各区域表现
        region_performance = {}
        for market_id, data in all_markets.items():
            from global_market_aggregator import GlobalMarketDataAggregator
            config = GlobalMarketDataAggregator.MARKETS.get(market_id, {})
            region = config.get("region", "OTHER")
            
            if region not in region_performance:
                region_performance[region] = []
            if data.change_pct:
                region_performance[region].append(data.change_pct.value)
                
        # 计算区域平均
        region_avg = {}
        for region, changes in region_performance.items():
            if changes:
                region_avg[region] = sum(changes) / len(changes)
                
        # 判断市场状态
        regime = self._classify_regime(region_avg)
        
        return {
            "regime": regime,
            "region_performance": region_avg,
            "risk_on_regions": [r for r, v in region_avg.items() if v > 0],
            "risk_off_regions": [r for r, v in region_avg.items() if v < -1],
        }
        
    def _classify_regime(self, region_perf: Dict) -> str:
        """分类市场状态"""
        us_perf = region_perf.get("US", 0)
        cn_perf = region_perf.get("CN", 0)
        
        if us_perf < -2 and cn_perf < -2:
            return "risk_off"  # 全球风险规避
        elif us_perf > 1 and cn_perf > 1:
            return "risk_on"  # 全球风险偏好
        elif us_perf > 0 > cn_perf:
            return "us_leading"  # 美股独强
        elif cn_perf > 0 > us_perf:
            return "china_leading"  # A股独强
        else:
            return "mixed"  # 分化
            
    def analyze_risk_factors(self) -> List[Dict]:
        """分析当前风险因素"""
        risks = []
        
        # 1. VIX水平
        vix_data = self.sentiment_monitor._get_vix_data()
        if vix_data and vix_data["value"] > 25:
            risks.append({
                "factor": "波动率飙升",
                "level": "high" if vix_data["value"] > 30 else "medium",
                "description": f"VIX={vix_data['value']:.2f}，市场恐慌情绪上升",
                "impact": "短期避险，关注超跌反弹机会"
            })
            
        # 2. 收益率曲线
        yield_curve = self.macro_monitor.analyze_yield_curve()
        if yield_curve.get("status") == "inverted":
            risks.append({
                "factor": "收益率曲线倒挂",
                "level": "high",
                "description": f"10Y-2Y利差={yield_curve['spread']:.2f}%",
                "impact": "历史上预示衰退，但时滞不确定，关注防御板块"
            })
            
        # 3. 市场广度（简化版）
        all_markets = self.market_agg.get_all_markets()
        declining = sum(1 for m in all_markets.values() if m.change_pct and m.change_pct.value < 0)
        total = len(all_markets)
        
        if declining / total > 0.7:
            risks.append({
                "factor": "市场普跌",
                "level": "medium",
                "description": f"{declining}/{total}个市场下跌",
                "impact": "系统性风险上升，控制仓位"
            })
            
        return risks
        
    def generate_asset_allocation(self) -> Dict[str, InvestmentSignal]:
        """生成资产配置建议"""
        signals = {}
        
        # 分析市场状态
        regime = self.analyze_market_regime()
        risks = self.analyze_risk_factors()
        sentiment = self.sentiment_monitor.get_fear_greed_index()
        
        # 根据市场状态生成信号
        regime_type = regime["regime"]
        
        # 股票
        if regime_type == "risk_off":
            stock_signal = InvestmentSignal(
                asset_class="股票",
                signal=SignalType.REDUCE,
                confidence=ConfidenceLevel.MEDIUM,
                reasoning=[
                    "全球市场普跌，风险规避情绪上升",
                    "VIX处于高位，波动率预期上升",
                    "建议降低仓位，等待企稳信号"
                ],
                risk_factors=["进一步下跌风险", "流动性收紧"],
                time_horizon="short"
            )
        elif regime_type == "risk_on":
            stock_signal = InvestmentSignal(
                asset_class="股票",
                signal=SignalType.BUY,
                confidence=ConfidenceLevel.MEDIUM,
                reasoning=[
                    "全球市场同步上涨，风险偏好回升",
                    "建议参与趋势，但注意追高风险"
                ],
                risk_factors=["短期超买", "政策转向风险"],
                time_horizon="medium"
            )
        else:
            stock_signal = InvestmentSignal(
                asset_class="股票",
                signal=SignalType.HOLD,
                confidence=ConfidenceLevel.LOW,
                reasoning=["市场分化，方向不明，保持观望"],
                risk_factors=["方向选择风险"],
                time_horizon="short"
            )
            
        signals["stocks"] = stock_signal
        
        # 债券
        yield_curve = self.macro_monitor.analyze_yield_curve()
        if yield_curve.get("status") == "inverted":
            bond_signal = InvestmentSignal(
                asset_class="债券",
                signal=SignalType.BUY,
                confidence=ConfidenceLevel.HIGH,
                reasoning=[
                    "收益率曲线倒挂，预示降息周期",
                    "长期债券价格将受益于利率下行"
                ],
                risk_factors=["通胀反弹", "财政赤字扩大"],
                time_horizon="long"
            )
        else:
            bond_signal = InvestmentSignal(
                asset_class="债券",
                signal=SignalType.HOLD,
                confidence=ConfidenceLevel.LOW,
                reasoning=["利率环境中性，债券配置价值一般"],
                risk_factors=["利率上行风险"],
                time_horizon="medium"
            )
            
        signals["bonds"] = bond_signal
        
        # 黄金
        if regime_type == "risk_off":
            gold_signal = InvestmentSignal(
                asset_class="黄金",
                signal=SignalType.BUY,
                confidence=ConfidenceLevel.MEDIUM,
                reasoning=[
                    "避险需求上升，黄金配置价值增加",
                    "美元走弱预期支撑金价"
                ],
                risk_factors=["美元反弹", "实际利率上升"],
                time_horizon="medium"
            )
        else:
            gold_signal = InvestmentSignal(
                asset_class="黄金",
                signal=SignalType.HOLD,
                confidence=ConfidenceLevel.LOW,
                reasoning=["黄金作为组合对冲工具，保持基准配置"],
                risk_factors=["机会成本"],
                time_horizon="long"
            )
            
        signals["gold"] = gold_signal
        
        # 现金
        if any(r["level"] == "high" for r in risks):
            cash_signal = InvestmentSignal(
                asset_class="现金",
                signal=SignalType.BUY,
                confidence=ConfidenceLevel.HIGH,
                reasoning=[
                    "市场不确定性高，提高现金比例等待机会",
                    "保留弹药用于超跌买入"
                ],
                risk_factors=["通胀侵蚀", "踏空风险"],
                time_horizon="short"
            )
        else:
            cash_signal = InvestmentSignal(
                asset_class="现金",
                signal=SignalType.HOLD,
                confidence=ConfidenceLevel.MEDIUM,
                reasoning=["保持适度现金比例，维持灵活性"],
                risk_factors=["机会成本"],
                time_horizon="medium"
            )
            
        signals["cash"] = cash_signal
        
        return signals
        
    def generate_full_report(self) -> str:
        """生成完整投资分析报告"""
        lines = []
        lines.append("=" * 70)
        lines.append("📊 投资分析报告")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 70)
        
        # 1. 市场状态
        lines.append("\n🏛️ 市场状态分析")
        lines.append("-" * 50)
        regime = self.analyze_market_regime()
        regime_names = {
            "risk_off": "🔴 全球风险规避",
            "risk_on": "🟢 全球风险偏好",
            "us_leading": "🟡 美股独强",
            "china_leading": "🟡 A股独强",
            "mixed": "⚪ 市场分化"
        }
        lines.append(f"当前状态: {regime_names.get(regime['regime'], '未知')}")
        lines.append(f"风险资产上涨区域: {', '.join(regime['risk_on_regions']) or '无'}")
        lines.append(f"风险资产下跌区域: {', '.join(regime['risk_off_regions']) or '无'}")
        
        # 2. 风险因素
        lines.append("\n⚠️  主要风险因素")
        lines.append("-" * 50)
        risks = self.analyze_risk_factors()
        if risks:
            for risk in risks:
                emoji = "🔴" if risk["level"] == "high" else "🟡"
                lines.append(f"{emoji} {risk['factor']}")
                lines.append(f"   {risk['description']}")
                lines.append(f"   影响: {risk['impact']}")
        else:
            lines.append("  🟢 当前无明显风险因素")
            
        # 3. 资产配置建议
        lines.append("\n💼 资产配置建议")
        lines.append("-" * 50)
        signals = self.generate_asset_allocation()
        
        signal_emojis = {
            SignalType.STRONG_BUY: "🟢🟢",
            SignalType.BUY: "🟢",
            SignalType.HOLD: "⚪",
            SignalType.REDUCE: "🟡",
            SignalType.SELL: "🔴",
            SignalType.STRONG_SELL: "🔴🔴"
        }
        
        for asset, signal in signals.items():
            emoji = signal_emojis.get(signal.signal, "⚪")
            lines.append(f"\n{emoji} {signal.asset_class} - {signal.signal.value} (置信度: {signal.confidence.value})")
            lines.append(f"   时间维度: {signal.time_horizon}")
            lines.append(f"   理由:")
            for reason in signal.reasoning:
                lines.append(f"      • {reason}")
            lines.append(f"   风险因素:")
            for risk in signal.risk_factors:
                lines.append(f"      ⚠️  {risk}")
                
        # 4. 操作建议
        lines.append("\n📝 操作建议")
        lines.append("-" * 50)
        
        # 根据整体信号生成操作建议
        buy_signals = sum(1 for s in signals.values() if s.signal in [SignalType.BUY, SignalType.STRONG_BUY])
        sell_signals = sum(1 for s in signals.values() if s.signal in [SignalType.SELL, SignalType.STRONG_SELL, SignalType.REDUCE])
        
        if sell_signals >= 2:
            lines.append("  🔴 防御为主")
            lines.append("     • 降低股票仓位至50%以下")
            lines.append("     • 增配黄金和现金")
            lines.append("     • 关注超跌反弹机会，但控制仓位")
        elif buy_signals >= 2:
            lines.append("  🟢 积极参与")
            lines.append("     • 维持或适度增加股票仓位")
            lines.append("     • 关注领涨板块和个股")
            lines.append("     • 设置止损，控制回撤")
        else:
            lines.append("  ⚪ 保持观望")
            lines.append("     • 维持当前仓位，不做大幅调整")
            lines.append("     • 等待方向明确后再行动")
            lines.append("     • 关注结构性机会")
            
        lines.append("\n" + "=" * 70)
        lines.append("⚠️  免责声明")
        lines.append("  本报告仅供参考，不构成投资建议。")
        lines.append("  投资有风险，入市需谨慎。过往表现不代表未来收益。")
        lines.append("=" * 70)
        
        return "\n".join(lines)

if __name__ == "__main__":
    engine = InvestmentAnalysisEngine()
    print(engine.generate_full_report())
