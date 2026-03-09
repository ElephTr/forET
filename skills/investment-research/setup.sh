#!/bin/bash
# Investment Research Skill - Setup Script
# 安装依赖和配置环境

set -e

echo "🚀 安装投资研究 Skill 依赖..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python 3，请先安装"
    exit 1
fi

# 创建虚拟环境（可选）
VENV_DIR="${HOME}/.investment-research-venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# 安装 Python 依赖
echo "📦 安装 Python 依赖..."
pip install -q --upgrade pip
pip install -q requests pandas numpy

echo "✅ 依赖安装完成"

# 创建数据目录
mkdir -p "${HOME}/.investment-data"
echo "📁 数据目录: ${HOME}/.investment-data"

# 配置 API Keys（用户需要手动设置）
CONFIG_FILE="${HOME}/.investment-research.conf"
if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << 'EOF'
# Investment Research Skill 配置文件
# 请填写你的 API Keys（可选，大部分功能不需要）

# FRED API Key (免费，推荐)
# 获取: https://fred.stlouisfed.org/docs/api/api_key.html
# export FRED_API_KEY="your_key_here"

# Alpha Vantage API Key (免费版: 每天5次调用)
# 获取: https://www.alphavantage.co/support/#api-key
# export ALPHA_VANTAGE_KEY="your_key_here"

# 数据存储路径
export INVESTMENT_DATA_DIR="${HOME}/.investment-data"
EOF
    echo "⚙️  配置文件已创建: $CONFIG_FILE"
    echo "   如需更多数据，请配置 API Keys"
fi

echo ""
echo "✅ 安装完成！"
echo ""
echo "使用方法:"
echo "  cd skills/investment-research"
echo "  ./scripts/investment_cli.py full-report    # 完整分析报告"
echo "  ./scripts/investment_cli.py markets        # 全球市场数据"
echo "  ./scripts/investment_cli.py macro          # 宏观数据"
echo "  ./scripts/investment_cli.py sentiment      # 情绪指标"
echo ""
echo "配置 API Keys (可选):"
echo "  export FRED_API_KEY=your_key_here"
echo ""
