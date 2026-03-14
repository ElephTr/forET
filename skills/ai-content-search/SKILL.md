---
name: ai-content-search
description: AI 内容聚合搜索工具 - 一站式搜索 Reddit、知乎、小红书、Twitter、YouTube 等平台的 AI 相关内容。无需登录，直接获取各平台公开搜索结果。
---

# AI 内容聚合搜索工具

一站式搜索多个平台的 AI 相关内容。

## 支持平台

- **Reddit** - 全球最大社区讨论
- **知乎** - 中文问答社区
- **小红书** - 生活方式分享
- **Twitter/X** - 实时讨论
- **YouTube** - 视频内容
- **GitHub** - 开源项目
- **Hacker News** - 技术讨论
- **Product Hunt** - 新产品发现

## 使用方法

```bash
# 搜索 AI 相关内容
python3 scripts/search.py "AI 工具推荐"

# 指定平台
python3 scripts/search.py "ChatGPT" --platforms reddit,zhihu

# 启动 Web 界面
python3 scripts/web_server.py
```

## 部署

```bash
./deploy.sh
```

访问 http://localhost:8080/ai-search/