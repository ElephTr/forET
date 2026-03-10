# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Web Search Tool

已安装并配置好网络搜索工具，使用 DuckDuckGo 搜索。

### 使用方法

```bash
# 基本搜索
python3 /root/.openclaw/workspace/tools/websearch.py "搜索关键词"

# 指定结果数量
python3 /root/.openclaw/workspace/tools/websearch.py "搜索关键词" 10

# 搜索新闻
python3 /root/.openclaw/workspace/tools/websearch.py "新闻关键词" 5 --news
```

### 示例

```bash
# 搜索上海活动
python3 /root/.openclaw/workspace/tools/websearch.py "上海 周末活动" 5

# 搜索新闻
python3 /root/.openclaw/workspace/tools/websearch.py "AI 人工智能" 10 --news
```

---

Add whatever helps you do your job. This is your cheat sheet.
