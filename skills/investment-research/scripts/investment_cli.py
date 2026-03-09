#!/usr/bin/env python3
"""
Investment Research CLI - 统一命令行入口
"""

import sys
import argparse
from datetime import datetime

# 添加脚本路径
sys.path.insert(0, '/root/.openclaw/workspace/skills/investment-research/scripts')

from global_market_aggregator import GlobalMarketDataAggregator
from macro_monitor import MacroDataMonitor, format_macro_report
from sentiment_monitor import MarketSentimentMonitor
from analysis_engine import InvestmentAnalysisEngine

def cmd_markets(args):
    """市场数据命令"""
    agg = GlobalMarketDataAggregator()
    
    if args.region:
        markets = agg.get_all_markets(region_filter=args.region)
        print(f"\n📊 {args.region} 地区市场数据")
    else:
        summary = agg.get_region_summary()
        print("\n🌍 全球市场概览")
        print("=" * 60)
        
        for region, info in summary.items():
            if info["markets"]:
                emoji = "🟢" if info["avg_change"] >= 0 else "🔴"
                print(f"\n{emoji} {info['name']} (平均: {info['avg_change']:+.2f}%)")
                print("-" * 40)
                for market in info["markets"]:
                    if market.change_pct:
                        e = "🟢" if market.change_pct.value >= 0 else "🔴"
                        verified = "✓" if market.price and market.price.is_verified else " "
                        print(f"  {e}{verified} {market.name:15} {market.price.value:>12.2f}  {market.change_pct.value:>+.2f}%")

def cmd_macro(args):
    """宏观数据命令"""
    import os
    fred_key = os.environ.get("FRED_API_KEY")
    monitor = MacroDataMonitor(fred_key)
    print(format_macro_report(monitor))

def cmd_sentiment(args):
    """情绪指标命令"""
    monitor = MarketSentimentMonitor()
    print(monitor.get_full_sentiment_report())

def cmd_analyze(args):
    """单个标的分析"""
    symbol = args.symbol
    print(f"\n🔍 分析 {symbol}")
    print("=" * 50)
    
    agg = GlobalMarketDataAggregator()
    
    # 尝试从MARKETS中找到匹配的symbol
    market_data = None
    for market_id, config in agg.MARKETS.items():
        if config["symbol"] == symbol or market_id == symbol:
            market_data = agg.get_market_data(market_id)
            break
    
    if market_data:
        print(f"\n📈 {market_data.name} ({market_data.symbol})")
        if market_data.price:
            print(f"  价格: {market_data.price.value:.2f}")
            print(f"  来源: {market_data.price.source} (可信度: {market_data.price.confidence})")
            print(f"  验证: {'✓ 多源验证' if market_data.price.is_verified else '单源数据'}")
        if market_data.change_pct:
            emoji = "🟢" if market_data.change_pct.value >= 0 else "🔴"
            print(f"  涨跌: {emoji} {market_data.change_pct.value:+.2f}%")
    else:
        print(f"  未找到 {symbol} 的配置，尝试直接获取...")
        # 可以尝试用Yahoo Finance直接获取

def cmd_full_report(args):
    """完整分析报告"""
    import os
    fred_key = os.environ.get("FRED_API_KEY")
    engine = InvestmentAnalysisEngine(fred_key)
    print(engine.generate_full_report())

def main():
    parser = argparse.ArgumentParser(
        description="Investment Research - 全球市场投资研究工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s full-report          # 生成完整分析报告
  %(prog)s markets              # 查看全球市场数据
  %(prog)s markets --region US  # 只看美股
  %(prog)s macro                # 查看宏观数据
  %(prog)s sentiment            # 查看情绪指标
  %(prog)s analyze AAPL         # 分析单个标的
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # markets 命令
    markets_parser = subparsers.add_parser("markets", help="查看市场数据")
    markets_parser.add_argument("--region", choices=["US", "CN", "HK", "JP", "EU", "FX", "COMM", "CRYPTO"],
                               help="筛选特定地区")
    
    # macro 命令
    macro_parser = subparsers.add_parser("macro", help="查看宏观数据")
    
    # sentiment 命令
    sentiment_parser = subparsers.add_parser("sentiment", help="查看情绪指标")
    
    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="分析单个标的")
    analyze_parser.add_argument("symbol", help="标的代码 (如 AAPL, BTC-USD)")
    
    # full-report 命令
    report_parser = subparsers.add_parser("full-report", help="生成完整分析报告")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 执行对应命令
    commands = {
        "markets": cmd_markets,
        "macro": cmd_macro,
        "sentiment": cmd_sentiment,
        "analyze": cmd_analyze,
        "full-report": cmd_full_report,
    }
    
    if args.command in commands:
        try:
            commands[args.command](args)
        except KeyboardInterrupt:
            print("\n\n已取消")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
