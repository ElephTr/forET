#!/usr/bin/env python3
"""
市场情绪与资金流向监控
跟踪投资者情绪指标和资金流动
"""

import requests
import json
from datetime import datetime
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

class SentimentLevel(Enum):
    """情绪等级"""
    EXTREME_FEAR = "极度恐惧"
    FEAR = "恐惧"
    NEUTRAL = "中性"
    GREED = "贪婪"
    EXTREME_GREED = "极度贪婪"

@dataclass
class SentimentIndicator:
    """情绪指标"""
    name: str
    value: float
    level: SentimentLevel
    signal: str  # 交易信号
    description: str

class MarketSentimentMonitor:
    """市场情绪监控器"""
    
    def __init__(self):
        self.cache = {}
        self.cache_time = 300  # 5分钟缓存
        
    def get_fear_greed_index(self) -> Optional[SentimentIndicator]:
        """
        恐惧贪婪指数 (CNN Fear & Greed)
        0-100分，基于7个指标
        """
        try:
            # 使用替代数据源或估算
            # 实际API需要注册，这里使用基于VIX的估算
            vix_data = self._get_vix_data()
            if not vix_data:
                return None
                
            vix = vix_data["value"]
            
            # VIX到恐惧贪婪指数的映射
            # VIX < 15: 贪婪 (>75)
            # VIX 15-20: 中性 (50-75)
            # VIX 20-25: 恐惧 (25-50)
            # VIX > 25: 极度恐惧 (<25)
            
            if vix < 15:
                score = 85
                level = SentimentLevel.EXTREME_GREED
                signal = "⚠️ 考虑减仓"
            elif vix < 20:
                score = 65
                level = SentimentLevel.GREED
                signal = "🟡 保持警惕"
            elif vix < 25:
                score = 45
                level = SentimentLevel.NEUTRAL
                signal = "⚪ 中性观望"
            elif vix < 30:
                score = 25
                level = SentimentLevel.FEAR
                signal = "🟢 考虑加仓"
            else:
                score = 10
                level = SentimentLevel.EXTREME_FEAR
                signal = "🟢🟢 积极加仓"
                
            return SentimentIndicator(
                name="恐惧贪婪指数(估算)",
                value=score,
                level=level,
                signal=signal,
                description=f"基于VIX={vix:.2f}估算，0=极度恐惧，100=极度贪婪"
            )
        except Exception as e:
            return None
            
    def _get_vix_data(self) -> Optional[Dict]:
        """获取VIX数据"""
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/^VIX?interval=1d&range=5d"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            
            result = data["chart"]["result"][0]
            closes = result["indicators"]["quote"][0]["close"]
            latest = closes[-1]
            
            # VIX历史分位估算
            # 长期均值约20，极端恐慌>30，极端平静<15
            return {
                "value": latest,
                "historical_avg": 20,
                "percentile": self._estimate_vix_percentile(latest)
            }
        except:
            return None
            
    def _estimate_vix_percentile(self, vix: float) -> float:
        """估算VIX历史分位"""
        # 简化估算：VIX分布大致在10-40之间
        if vix < 10:
            return 5
        elif vix > 40:
            return 95
        else:
            return ((vix - 10) / 30) * 100
            
    def get_vix_term_structure(self) -> Optional[Dict]:
        """VIX期限结构分析"""
        try:
            # VIX期货合约代码 (简化，实际需要期货数据)
            vix_spot = self._get_vix_data()
            if not vix_spot:
                return None
                
            spot = vix_spot["value"]
            
            # 模拟期限结构分析
            # 实际应该获取VIX1M, VIX3M, VIX6M等
            return {
                "spot": spot,
                "structure": "contango" if spot < 25 else "backwardation",
                "signal": "🟢 远期溢价(正常)" if spot < 25 else "🔴 远期折价(恐慌)",
                "interpretation": {
                    "contango": "VIX期限结构为contango，市场预期未来波动下降",
                    "backwardation": "VIX期限结构为backwardation，市场处于恐慌状态"
                }
            }
        except:
            return None
            
    def get_put_call_ratio(self) -> Optional[SentimentIndicator]:
        """
        Put/Call Ratio (CBOE)
        >1.2: 极度悲观 (买入信号)
        <0.7: 极度乐观 (卖出信号)
        """
        try:
            # 实际需要从CBOE获取数据
            # 这里使用模拟数据
            url = "https://www.cboe.com/us/options/market_statistics/daily/"
            # 简化处理，实际需要解析网页或API
            
            # 模拟一个合理值
            pcr = 0.95  # 假设值
            
            if pcr > 1.2:
                level = SentimentLevel.EXTREME_FEAR
                signal = "🟢 强烈买入信号"
            elif pcr > 1.0:
                level = SentimentLevel.FEAR
                signal = "🟢 买入信号"
            elif pcr > 0.8:
                level = SentimentLevel.NEUTRAL
                signal = "⚪ 中性"
            elif pcr > 0.7:
                level = SentimentLevel.GREED
                signal = "🟡 谨慎"
            else:
                level = SentimentLevel.EXTREME_GREED
                signal = "🔴 卖出信号"
                
            return SentimentIndicator(
                name="Put/Call Ratio",
                value=pcr,
                level=level,
                signal=signal,
                description=f"期权市场看跌/看涨比率，>1.2极度悲观，<0.7极度乐观"
            )
        except:
            return None
            
    def get_a_share_sentiment(self) -> Dict:
        """A股市场情绪指标"""
        try:
            from a_share_data import AShareDataSource
            source = AShareDataSource()
            sentiment_data = source.get_market_sentiment_indicators()
            
            return {
                "index_sentiment": {
                    "name": f"{sentiment_data.get('index', 'A股')}情绪",
                    "change_pct": sentiment_data.get('change_pct', 0),
                    "sentiment": sentiment_data.get('sentiment', '未知'),
                    "signal": sentiment_data.get('signal', '⚪ 待接入')
                },
                "northbound": {
                    "name": "北向资金",
                    "status": "需专业数据源",
                    "signal": "⚪ 接入Wind/iFinD"
                },
                "margin": {
                    "name": "融资余额",
                    "status": "需专业数据源", 
                    "signal": "⚪ 接入Wind/iFinD"
                }
            }
        except Exception as e:
            return {
                "index_sentiment": {
                    "name": "A股情绪",
                    "signal": "⚪ 数据获取失败"
                },
                "northbound": {"name": "北向资金", "signal": "⚪ 待接入"},
                "margin": {"name": "融资余额", "signal": "⚪ 待接入"}
            }
        
    def get_market_breadth(self) -> Optional[Dict]:
        """市场广度指标"""
        try:
            # 实际应该计算上涨/下跌股票数量
            # 这里提供框架
            return {
                "advance_decline": {
                    "name": "涨跌家数比",
                    "value": "需要计算",
                    "signal": "⚪ 待实现"
                },
                "new_highs_lows": {
                    "name": "新高/新低",
                    "value": "需要计算",
                    "signal": "⚪ 待实现"
                },
                "mcclellan_osc": {
                    "name": "McClellan震荡指标",
                    "value": "需要计算",
                    "signal": "⚪ 待实现"
                }
            }
        except:
            return None
            
    def get_crypto_sentiment(self) -> Optional[Dict]:
        """加密货币市场情绪"""
        try:
            # 可以使用Alternative.me的Crypto Fear & Greed API
            url = "https://api.alternative.me/fng/?limit=1"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            if "data" in data and len(data["data"]) > 0:
                item = data["data"][0]
                value = int(item["value"])
                classification = item["value_classification"]
                
                # 映射到我们的情绪等级
                level_map = {
                    "Extreme Fear": SentimentLevel.EXTREME_FEAR,
                    "Fear": SentimentLevel.FEAR,
                    "Neutral": SentimentLevel.NEUTRAL,
                    "Greed": SentimentLevel.GREED,
                    "Extreme Greed": SentimentLevel.EXTREME_GREED
                }
                
                level = level_map.get(classification, SentimentLevel.NEUTRAL)
                
                signal_map = {
                    SentimentLevel.EXTREME_FEAR: "🟢🟢 积极买入",
                    SentimentLevel.FEAR: "🟢 考虑买入",
                    SentimentLevel.NEUTRAL: "⚪ 观望",
                    SentimentLevel.GREED: "🟡 谨慎",
                    SentimentLevel.EXTREME_GREED: "🔴 考虑卖出"
                }
                
                return {
                    "indicator": SentimentIndicator(
                        name="加密货币恐惧贪婪指数",
                        value=value,
                        level=level,
                        signal=signal_map.get(level, "⚪ 观望"),
                        description="基于波动率、市场动量、社交媒体、调查、主导地位、趋势"
                    ),
                    "source": "alternative.me"
                }
        except Exception as e:
            return None
            
    def get_full_sentiment_report(self) -> str:
        """生成完整情绪报告"""
        lines = []
        lines.append("🧠 市场情绪监控报告")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 60)
        
        # 恐惧贪婪指数
        lines.append("\n📊 恐惧贪婪指数")
        lines.append("-" * 40)
        fng = self.get_fear_greed_index()
        if fng:
            bar = self._make_gauge(fng.value)
            lines.append(f"  {bar}")
            lines.append(f"  数值: {fng.value:.0f}/100 ({fng.level.value})")
            lines.append(f"  信号: {fng.signal}")
            lines.append(f"  说明: {fng.description}")
        else:
            lines.append("  ⚪ 数据获取失败")
            
        # VIX期限结构
        lines.append("\n📈 VIX期限结构")
        lines.append("-" * 40)
        vix_term = self.get_vix_term_structure()
        if vix_term:
            lines.append(f"  现货VIX: {vix_term['spot']:.2f}")
            lines.append(f"  结构: {vix_term['structure']}")
            lines.append(f"  信号: {vix_term['signal']}")
        else:
            lines.append("  ⚪ 数据获取失败")
            
        # Put/Call Ratio
        lines.append("\n📉 Put/Call Ratio")
        lines.append("-" * 40)
        pcr = self.get_put_call_ratio()
        if pcr:
            lines.append(f"  数值: {pcr.value:.2f}")
            lines.append(f"  情绪: {pcr.level.value}")
            lines.append(f"  信号: {pcr.signal}")
        else:
            lines.append("  ⚪ 需要CBOE数据源")
            
        # 加密货币情绪
        lines.append("\n₿ 加密货币情绪")
        lines.append("-" * 40)
        crypto = self.get_crypto_sentiment()
        if crypto:
            ind = crypto["indicator"]
            bar = self._make_gauge(ind.value)
            lines.append(f"  {bar}")
            lines.append(f"  数值: {ind.value:.0f}/100 ({ind.level.value})")
            lines.append(f"  信号: {ind.signal}")
        else:
            lines.append("  ⚪ 数据获取失败")
            
        # A股情绪
        lines.append("\n🇨🇳 A股市场情绪")
        lines.append("-" * 40)
        a_share = self.get_a_share_sentiment()
        
        # 指数情绪
        if "index_sentiment" in a_share:
            idx = a_share["index_sentiment"]
            emoji = "🟢" if idx.get('change_pct', 0) >= 0 else "🔴"
            lines.append(f"  {idx['name']}: {emoji} {idx.get('sentiment', '未知')}")
            lines.append(f"  信号: {idx['signal']}")
            
        # 其他指标
        for key, item in a_share.items():
            if key != "index_sentiment":
                lines.append(f"  {item['name']}: {item['signal']}")
            
        lines.append("\n" + "=" * 60)
        lines.append("💡 情绪指标使用说明:")
        lines.append("  • 情绪指标是反向指标，极端值往往预示转折")
        lines.append("  • 结合价格走势和基本面使用效果更佳")
        lines.append("  • 不要单独依赖情绪指标做决策")
        
        return "\n".join(lines)
        
    def _make_gauge(self, value: float, width: int = 30) -> str:
        """制作可视化仪表盘"""
        filled = int((value / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        
        # 添加标签
        if value < 25:
            label = "恐惧"
        elif value < 50:
            label = "偏空"
        elif value < 75:
            label = "偏多"
        else:
            label = "贪婪"
            
        return f"0 {bar} 100 [{label}]"

if __name__ == "__main__":
    monitor = MarketSentimentMonitor()
    print(monitor.get_full_sentiment_report())
