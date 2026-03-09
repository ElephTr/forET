# Investment Research Skill

基于第一性原理的全球市场投资研究系统。

## 核心架构

### 数据源层 (Multi-Source)
- **Tier 1**: 交易所官方、央行数据 (最高可信度)
- **Tier 2**: Yahoo Finance, Alpha Vantage, FRED
- **Tier 3**: 东方财富、CoinGecko 等聚合平台
- **验证机制**: 多源交叉验证，自动故障转移

### 分析层 (Multi-Dimension)
- **市场数据**: 全球股市、外汇、商品、加密货币
- **宏观数据**: 利率、通胀、就业、流动性
- **情绪指标**: VIX、恐惧贪婪指数、资金流向

### 决策层 (First-Principles)
- 市场状态识别 (Risk-on/Risk-off/Mixed)
- 风险因素评估
- 资产配置建议
- 具体操作指导

## 使用方法

### 完整分析报告
```bash
./scripts/investment_cli.py full-report
```
生成包含市场状态、风险因素、资产配置、操作建议的完整报告。

### 市场数据
```bash
./scripts/investment_cli.py markets
./scripts/investment_cli.py markets --region US
./scripts/investment_cli.py markets --region CN
```

### 宏观数据
```bash
./scripts/investment_cli.py macro
```
需要设置 FRED_API_KEY 环境变量获取完整数据。

### 情绪指标
```bash
./scripts/investment_cli.py sentiment
```

### 单个标的分析
```bash
./scripts/investment_cli.py analyze AAPL
./scripts/investment_cli.py analyze BTC-USD
```

## 分析框架

### 第一性原理
1. **价格包含一切**: 市场是最快的信息处理机器
2. **多源验证**: 单一数据源不可靠，交叉验证提高可信度
3. **风险优先**: 先考虑下行风险，再追求上行收益
4. **系统应对**: 不预测，准备多种情景应对方案

### 市场状态分类
- **Risk-on**: 全球风险偏好，增配股票
- **Risk-off**: 全球风险规避，增配债券/现金/黄金
- **US Leading**: 美股独强，关注美股机会
- **China Leading**: A股独强，关注A股机会
- **Mixed**: 市场分化，保持观望

### 信号生成逻辑
```
市场数据 + 宏观数据 + 情绪指标 → 市场状态 → 资产配置建议 → 具体操作建议
```

## 数据覆盖

### 全球市场
- 美股: 标普500、纳斯达克、道琼斯
- A股: 上证、深证、沪深300
- 港股: 恒生指数、恒生科技
- 亚太: 日经、韩国、澳洲
- 欧洲: 富时、DAX、CAC、STOXX50

### 外汇与商品
- 美元指数、欧元、日元、人民币
- 黄金、白银、原油、铜

### 加密货币
- 比特币、以太坊

### 宏观指标
- 美联储利率、美债收益率
- 通胀数据 (CPI)
- 就业数据
- 央行资产负债表

### 情绪指标
- VIX 波动率
- 恐惧贪婪指数
- 加密货币情绪
- (A股情绪待接入)

## 配置

### 环境变量
```bash
export FRED_API_KEY="your_fred_api_key"  # 可选，用于宏观数据
export ALPHA_VANTAGE_KEY="your_key"       # 可选，备用数据源
```

### 获取 API Key
- FRED: https://fred.stlouisfed.org/docs/api/api_key.html
- Alpha Vantage: https://www.alphavantage.co/support/#api-key

## 输出示例

```
📊 投资分析报告
======================================================================

🏛️ 市场状态分析
--------------------------------------------------
当前状态: 🔴 全球风险规避
风险资产上涨区域: 无
风险资产下跌区域: US, CN, HK, JP, EU

⚠️  主要风险因素
--------------------------------------------------
🔴 波动率飙升
   VIX=32.5，市场恐慌情绪上升
   影响: 短期避险，关注超跌反弹机会

💼 资产配置建议
--------------------------------------------------
🟢 债券 - 买入 (置信度: 高)
   理由: 收益率曲线倒挂，预示降息周期
   
⚪ 股票 - 减仓 (置信度: 中)
   理由: 全球市场普跌，风险规避情绪上升

📝 操作建议
--------------------------------------------------
  🔴 防御为主
     • 降低股票仓位至50%以下
     • 增配黄金和现金
```

## 扩展计划

- [x] 上下文压缩系统 (v1.2.0)
- [ ] A股资金流向 (北向资金、融资余额)
- [ ] 个股基本面分析
- [ ] 行业景气度跟踪
- [ ] 新闻情绪 NLP 分析
- [ ] 技术指标集成
- [ ] 回测框架

## 上下文优化 (v1.2.0)

为降低 LLM 调用成本和延迟，实现了上下文管理系统：

```bash
# 查看统计
./scripts/context_manager.py --stats

# 列出历史会话
./scripts/context_manager.py --list

# 搜索相关记忆
./scripts/context_manager.py --search "investment"
```

### 核心组件

1. **context_compressor.py** - 会话内压缩
   - 触发条件: >10轮对话 或 >4000 tokens
   - 保留: 决策、结果、错误、偏好
   - 丢弃: 中间尝试、重复信息

2. **memory_manager.py** - 跨会话记忆
   - 存储在 `memory/sessions/`
   - 关键词检索相关历史
   - Markdown 格式便于阅读

3. **context_manager.py** - 统一入口
   - 自动判断压缩策略
   - 组合历史记忆 + 当前上下文
   - 生成优化提示

## 免责声明

本系统提供的所有信息仅供参考，不构成投资建议。
投资有风险，决策需自主，过往表现不代表未来收益。
