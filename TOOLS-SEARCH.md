# TOOLS.md - 工具配置与 API 密钥

## Web Search Tools

### 推荐的搜索 API 服务

| 服务 | 免费额度 | 获取地址 | 配置方式 |
|------|---------|---------|---------|
| **Serper** | 2500次/月 | https://serper.dev/ | `export SERPER_API_KEY='your_key'` |
| **Brave** | 2000次/月 | https://brave.com/search/api/ | `export BRAVE_API_KEY='your_key'` |
| **Tavily** | 1000次/月 | https://tavily.com/ | `export TAVILY_API_KEY='your_key'` |
| **Bing** | 1000次/月 | https://www.microsoft.com/en-us/bing/apis/ | `export BING_API_KEY='your_key'` |

### 使用方法

```bash
# 1. 设置 API 密钥
export SERPER_API_KEY='your_api_key_here'

# 2. 使用搜索工具
/root/.openclaw/workspace/tools/websearch.sh "搜索关键词"

# 3. 或者使用 Python 版本
python3 /root/.openclaw/workspace/tools/websearch.py "搜索关键词"
```

### 添加到 ~/.bashrc 使其永久生效

```bash
echo 'export SERPER_API_KEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

## 其他可用工具

- `/root/.openclaw/workspace/tools/websearch.sh` - Bash 版本搜索工具
- `/root/.openclaw/workspace/tools/websearch.py` - Python 版本搜索工具

## 待安装的工具

### 1. Tavily Python SDK (推荐)
```bash
pip install tavily-python
```

### 2. DuckDuckGo Python
```bash
pip install duckduckgo-search
```

### 3. Playwright (用于浏览器自动化)
```bash
pip install playwright
playwright install chromium
```
