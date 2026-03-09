#!/usr/bin/env python3
"""
记忆管理器
跨会话检索相关历史上下文
"""

import os
import json
import glob
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

class MemoryManager:
    """记忆管理器"""
    
    MEMORY_DIR = "/root/.openclaw/workspace/memory/sessions"
    
    def __init__(self):
        self.memory_dir = Path(self.MEMORY_DIR)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
    
    def list_sessions(self, limit: int = 10) -> List[Dict]:
        """列出历史会话"""
        session_files = sorted(
            self.memory_dir.glob("*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        sessions = []
        for f in session_files[:limit]:
            # 解析文件名
            # 格式: YYYY-MM-DD-task-name.md
            name = f.stem
            parts = name.split("-")
            
            if len(parts) >= 3:
                date = f"{parts[0]}-{parts[1]}-{parts[2]}"
                task = "-".join(parts[3:]) if len(parts) > 3 else "unknown"
            else:
                date = "unknown"
                task = name
            
            sessions.append({
                "file": str(f),
                "date": date,
                "task": task,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })
        
        return sessions
    
    def get_session_summary(self, file_path: str) -> Optional[Dict]:
        """获取会话摘要"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # 解析 markdown 提取关键信息
            summary = {
                "task": self._extract_section(content, "Task"),
                "status": self._extract_status(content),
                "key_decisions": self._extract_list(content, "Key Decisions"),
                "outcomes": self._extract_list(content, "Outcomes"),
                "next_steps": self._extract_list(content, "Next Steps"),
            }
            
            return summary
        except Exception as e:
            print(f"Error reading session: {e}")
            return None
    
    def search_relevant(self, query: str, limit: int = 3) -> List[Dict]:
        """搜索相关会话"""
        sessions = self.list_sessions(limit=20)
        
        # 简单的关键词匹配
        query_lower = query.lower()
        keywords = [kw for kw in query_lower.split() if len(kw) >= 2]
        
        if not keywords:
            keywords = [query_lower]
        
        scored_sessions = []
        for s in sessions:
            score = 0
            
            # 读取原始文件内容
            try:
                with open(s["file"], 'r') as f:
                    raw_content = f.read().lower()
            except:
                continue
            
            # 获取结构化摘要
            summary = self.get_session_summary(s["file"])
            if not summary:
                summary = {"task": s["task"], "status": "Unknown"}
            
            task_lower = s["task"].lower()
            
            for kw in keywords:
                # 原始内容匹配 (更全面)
                if kw in raw_content:
                    score += 1
                # 任务名匹配 (权重更高)
                if kw in task_lower:
                    score += 3
            
            if score > 0:
                scored_sessions.append({
                    **s,
                    "summary": summary,
                    "relevance_score": score
                })
        
        # 按分数排序
        scored_sessions.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return scored_sessions[:limit]
    
    def format_context_for_prompt(self, relevant_sessions: List[Dict]) -> str:
        """格式化相关会话为提示"""
        if not relevant_sessions:
            return ""
        
        lines = []
        lines.append("\n" + "=" * 60)
        lines.append("📚 相关历史会话")
        lines.append("=" * 60)
        
        for i, session in enumerate(relevant_sessions, 1):
            summary = session.get("summary", {})
            
            lines.append(f"\n{i}. {summary.get('task', 'Unknown')}")
            lines.append(f"   日期: {session['date']}")
            lines.append(f"   状态: {summary.get('status', 'Unknown')}")
            
            if summary.get('key_decisions'):
                lines.append(f"   关键决策:")
                for d in summary['key_decisions'][:3]:
                    lines.append(f"      • {d}")
            
            if summary.get('next_steps'):
                lines.append(f"   待办:")
                for step in summary['next_steps'][:2]:
                    lines.append(f"      • {step}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
    
    def _extract_section(self, content: str, section: str) -> str:
        """提取章节内容"""
        import re
        # 支持 ## Task 或 ## Task Overview
        pattern = rf"##\s*{re.escape(section)}.*\n([^#]+)"
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_status(self, content: str) -> str:
        """提取状态"""
        if "✅ Completed" in content or "✅" in content and "Completed" in content:
            return "✅ 已完成"
        elif "🔄 In Progress" in content:
            return "🔄 进行中"
        elif "⏸️ Paused" in content:
            return "⏸️ 已暂停"
        # 从 Status 行提取
        import re
        match = re.search(r"\*\*Status\*\*:\s*(.+)", content)
        if match:
            return match.group(1).strip()
        return "Unknown"
    
    def _extract_list(self, content: str, section: str) -> List[str]:
        """提取列表项"""
        section_content = self._extract_section(content, section)
        
        items = []
        for line in section_content.split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                items.append(line[1:].strip())
            elif line.startswith("1.") or line.startswith("2."):
                items.append(line[2:].strip())
        
        return items

# 便捷函数
def get_relevant_context(query: str) -> str:
    """获取相关上下文"""
    manager = MemoryManager()
    sessions = manager.search_relevant(query)
    return manager.format_context_for_prompt(sessions)

if __name__ == "__main__":
    manager = MemoryManager()
    
    print("📚 历史会话列表:")
    print("=" * 60)
    
    sessions = manager.list_sessions()
    for s in sessions:
        print(f"\n📄 {s['file']}")
        print(f"   任务: {s['task']}")
        print(f"   日期: {s['date']}")
        
        summary = manager.get_session_summary(s['file'])
        if summary:
            print(f"   状态: {summary.get('status', 'Unknown')}")
    
    print("\n" + "=" * 60)
    print("\n🔍 搜索 'investment':")
    
    relevant = manager.search_relevant("investment")
    print(manager.format_context_for_prompt(relevant))
