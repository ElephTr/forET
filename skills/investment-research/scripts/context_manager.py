#!/usr/bin/env python3
"""
上下文管理器 - 主入口
整合压缩、记忆、提示优化
"""

import sys
import json
from typing import List, Dict, Optional
from dataclasses import asdict

sys.path.insert(0, '/root/.openclaw/workspace/skills/investment-research/scripts')

from context_compressor import ContextCompressor, SessionContext
from memory_manager import MemoryManager, get_relevant_context

class ContextManager:
    """上下文管理器"""
    
    def __init__(self):
        self.compressor = ContextCompressor()
        self.memory = MemoryManager()
    
    def prepare_prompt(self, 
                      current_messages: List[Dict],
                      new_query: str,
                      use_memory: bool = True) -> str:
        """
        准备优化后的提示
        
        策略:
        1. 如果对话短，直接使用
        2. 如果对话长，压缩为摘要
        3. 检索相关历史记忆
        4. 组合成优化提示
        """
        
        # 1. 检查是否需要压缩
        if self.compressor.should_compress(current_messages):
            # 压缩当前会话
            context = self.compressor.compress_session(current_messages)
            compressed = self.compressor.create_compressed_prompt(
                context, 
                current_messages[-3:],  # 保留最近3轮
                new_query
            )
        else:
            # 不需要压缩，构建简单上下文
            compressed = self._build_simple_context(current_messages, new_query)
        
        # 2. 检索相关历史记忆
        memory_context = ""
        if use_memory:
            memory_context = get_relevant_context(new_query)
        
        # 3. 组合
        if memory_context:
            return f"{memory_context}\n\n{compressed}"
        else:
            return compressed
    
    def _build_simple_context(self, messages: List[Dict], new_query: str) -> str:
        """构建简单上下文（无需压缩时）"""
        lines = []
        lines.append("=" * 60)
        lines.append("💬 当前对话")
        lines.append("=" * 60)
        
        # 只保留最近5轮
        for m in messages[-10:]:
            role = "用户" if m.get("role") == "user" else "助手"
            content = m.get("content", "")[:300]
            if len(m.get("content", "")) > 300:
                content += "..."
            lines.append(f"\n[{role}]: {content}")
        
        lines.append(f"\n[当前查询]: {new_query}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def save_session(self, messages: List[Dict], 
                    task_name: Optional[str] = None):
        """保存会话到长期记忆"""
        context = self.compressor.compress_session(messages)
        
        # 生成文件名
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        task = task_name or context.task.replace(" ", "-")[:30]
        filename = f"{date_str}-{task}.md"
        
        # 保存到 memory/sessions/
        filepath = f"/root/.openclaw/workspace/memory/sessions/{filename}"
        
        # 生成 markdown 格式
        md_content = self._generate_markdown(context)
        
        with open(filepath, 'w') as f:
            f.write(md_content)
        
        return filepath
    
    def _generate_markdown(self, context: SessionContext) -> str:
        """生成 Markdown 格式的会话摘要"""
        lines = []
        lines.append(f"# Session Summary: {context.task}")
        lines.append(f"**Date**: {context.start_time[:10]}")
        lines.append(f"**Status**: {context.current_state}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Key Decisions
        if context.key_decisions:
            lines.append("## Key Decisions")
            for i, d in enumerate(context.key_decisions[:10], 1):
                decision = d.get('decision', 'Unknown')
                lines.append(f"{i}. {decision}")
            lines.append("")
        
        # Outcomes
        if context.outcomes:
            lines.append("## Outcomes")
            for o in context.outcomes[:10]:
                lines.append(f"- {o}")
            lines.append("")
        
        # Errors
        if context.errors:
            lines.append("## Issues Fixed")
            for e in context.errors[:5]:
                lines.append(f"- {e}")
            lines.append("")
        
        # User Preferences
        if context.user_preferences:
            lines.append("## User Preferences")
            for p in context.user_preferences[:5]:
                lines.append(f"- {p}")
            lines.append("")
        
        # Next Steps
        if context.next_steps:
            lines.append("## Next Steps")
            for s in context.next_steps[:5]:
                lines.append(f"- [ ] {s}")
            lines.append("")
        
        return "\n".join(lines)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        sessions = self.memory.list_sessions(limit=100)
        
        return {
            "total_sessions": len(sessions),
            "recent_tasks": list(set(s["task"] for s in sessions[:5])),
            "memory_size_kb": sum(
                s.get("file", "").__sizeof__() 
                for s in sessions
            ) / 1024 if sessions else 0
        }

# CLI 入口
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="上下文管理工具")
    parser.add_argument("--stats", action="store_true", help="显示统计")
    parser.add_argument("--list", action="store_true", help="列出历史会话")
    parser.add_argument("--search", type=str, help="搜索相关会话")
    
    args = parser.parse_args()
    
    manager = ContextManager()
    
    if args.stats:
        stats = manager.get_stats()
        print("📊 上下文管理统计")
        print("=" * 40)
        print(f"总会话数: {stats['total_sessions']}")
        print(f"最近任务: {', '.join(stats['recent_tasks'])}")
        
    elif args.list:
        sessions = manager.memory.list_sessions()
        print("📚 历史会话列表")
        print("=" * 60)
        for s in sessions:
            print(f"\n📄 {s['task']}")
            print(f"   日期: {s['date']}")
            print(f"   文件: {s['file']}")
            
    elif args.search:
        result = get_relevant_context(args.search)
        if result.strip():
            print(result)
        else:
            print("未找到相关会话")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
