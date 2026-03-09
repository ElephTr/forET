#!/usr/bin/env python3
"""
商业机会分析 CLI
"""

import sys
import argparse
sys.path.insert(0, '/root/.openclaw/workspace/skills/business-opportunity/scripts')

from opportunity_analyzer import BusinessOpportunityAnalyzer

def cmd_scan(args):
    """扫描商业机会"""
    analyzer = BusinessOpportunityAnalyzer()
    print(analyzer.generate_opportunity_report(
        budget=args.budget or "all",
        difficulty=args.difficulty or "all"
    ))

def cmd_analyze(args):
    """分析具体商业想法"""
    analyzer = BusinessOpportunityAnalyzer()
    analysis = analyzer.analyze_business_model(args.idea)
    
    print("=" * 70)
    print(f"💡 商业想法分析: {args.idea}")
    print("=" * 70)
    
    print("\n📋 需求验证清单")
    print("-" * 50)
    for item in analysis["demand_validation"]["checklist"]:
        print(f"  □ {item}")
    
    print("\n🔍 验证方法")
    print("-" * 50)
    for method in analysis["demand_validation"]["validation_methods"]:
        print(f"  • {method}")
    
    print("\n📊 市场 sizing")
    print("-" * 50)
    print(f"  TAM: {analysis['market_sizing']['tam']}")
    print(f"  SAM: {analysis['market_sizing']['sam']}")
    print(f"  SOM: {analysis['market_sizing']['som']}")
    
    print("\n⚔️  竞争分析")
    print("-" * 50)
    print(f"  直接竞品: {analysis['competition']['direct_competitors']}")
    print(f"  间接竞品: {analysis['competition']['indirect_competitors']}")
    print(f"  竞争优势: {analysis['competition']['competitive_advantage']}")
    
    print("\n💰 商业模式画布")
    print("-" * 50)
    for key, value in analysis["business_model_canvas"].items():
        print(f"  {key}: {value}")
    
    print("\n✅ 可行性评估")
    print("-" * 50)
    for key, value in analysis["feasibility"].items():
        print(f"  {key}: {value}")

def cmd_enhanced(args):
    """增强版分析（基于市场信号和个性化匹配）"""
    from enhanced_analyzer import EnhancedOpportunityAnalyzer
    analyzer = EnhancedOpportunityAnalyzer()
    print(analyzer.generate_enhanced_report())

def cmd_crossborder(args):
    """跨境电商深度分析"""
    from crossborder_analyzer import CrossBorderEcommerceAnalyzer
    analyzer = CrossBorderEcommerceAnalyzer()
    print(analyzer.generate_report())

def cmd_demand(args):
    """需求驱动型机会发现"""
    from demand_driven_finder import DemandDrivenOpportunityFinder
    finder = DemandDrivenOpportunityFinder()
    print(finder.generate_report())

def main():
    parser = argparse.ArgumentParser(
        description="商业机会分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s enhanced                # 增强版分析（推荐）
  %(prog)s scan                    # 基础扫描
  %(prog)s scan --budget 低         # 只显示低资金门槛机会
  %(prog)s analyze "开咖啡店"       # 分析具体想法
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # enhanced 命令
    enhanced_parser = subparsers.add_parser("enhanced", help="增强版分析（基于市场信号）")
    
    # crossborder 命令
    crossborder_parser = subparsers.add_parser("crossborder", help="跨境电商深度分析")
    
    # demand 命令（新增）
    demand_parser = subparsers.add_parser("demand", help="需求驱动型机会发现")
    
    # scan 命令
    scan_parser = subparsers.add_parser("scan", help="扫描商业机会")
    scan_parser.add_argument("--budget", choices=["低", "中", "高"], help="资金门槛")
    scan_parser.add_argument("--difficulty", choices=["低", "中", "高"], help="难度级别")
    
    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="分析商业想法")
    analyze_parser.add_argument("idea", help="商业想法描述")
    
    args = parser.parse_args()
    
    if not args.command:
        # 默认运行增强版
        cmd_enhanced(args)
        sys.exit(0)
    
    commands = {
        "enhanced": cmd_enhanced,
        "crossborder": cmd_crossborder,
        "demand": cmd_demand,
        "scan": cmd_scan,
        "analyze": cmd_analyze,
    }
    
    if args.command in commands:
        try:
            commands[args.command](args)
        except KeyboardInterrupt:
            print("\n\n已取消")
            sys.exit(0)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
