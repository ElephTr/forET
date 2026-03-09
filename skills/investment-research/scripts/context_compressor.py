#!/usr/bin/env python3
"""
上下文压缩工具
用于优化 LLM 调用时的上下文长度
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class MessageSummary:
    """消息摘要"""
    role: str
    content_summary: str  # 压缩后的内容
    key_points: List[str]  # 关键点
    action_items: List[str]  # 行动项
    
@dataclass
class SessionContext:
    """会话上下文摘要"""
    session_id: str
    start_time: str
    task: str
    key_decisions: List[Dict]
    outcomes: List[str]
    errors: List[str]
    user_preferences: List[str]
    current_state: str
    next_steps: List[str]

class ContextCompressor:
    """上下文压缩器"""
    
    # 压缩触发阈值
    TOKEN_THRESHOLD = 4000
    MESSAGE_THRESHOLD = 10
    
    def __init__(self):
        self.compression_rules = {
            "tool_calls": self._compress_tool_calls,
            "code_blocks": self._compress_code,
            "repeated_errors": self._compress_errors,
            "file_listings": self._compress_listings,
        }
    
    def should_compress(self, messages: List[Dict]) -> bool:
        """判断是否需要压缩"""
        if len(messages) > self.MESSAGE_THRESHOLD:
            return True
        
        # 估算 token 数 (简化估算: 1 token ≈ 4 chars)
        total_chars = sum(len(m.get("content", "")) for m in messages)
        estimated_tokens = total_chars / 4
        
        return estimated_tokens > self.TOKEN_THRESHOLD
    
    def compress_session(self, messages: List[Dict]) -> SessionContext:
        """压缩整个会话"""
        
        # 提取关键信息
        task = self._extract_task(messages)
        decisions = self._extract_decisions(messages)
        outcomes = self._extract_outcomes(messages)
        errors = self._extract_errors(messages)
        preferences = self._extract_preferences(messages)
        state = self._extract_current_state(messages)
        next_steps = self._extract_next_steps(messages)
        
        return SessionContext(
            session_id=self._generate_session_id(),
            start_time=datetime.now().isoformat(),
            task=task,
            key_decisions=decisions,
            outcomes=outcomes,
            errors=errors,
            user_preferences=preferences,
            current_state=state,
            next_steps=next_steps
        )
    
    def create_compressed_prompt(self, context: SessionContext, 
                                  recent_messages: List[Dict],
                                  new_query: str) -> str:
        """创建压缩后的提示"""
        
        lines = []
        lines.append("=" * 60)
        lines.append("📋 会话上下文摘要")
        lines.append("=" * 60)
        
        # 任务
        lines.append(f"\n🎯 当前任务: {context.task}")
        
        # 关键决策
        if context.key_decisions:
            lines.append("\n📌 关键决策:")
            for i, d in enumerate(context.key_decisions[-5:], 1):  # 最近5个
                lines.append(f"  {i}. {d.get('decision', 'Unknown')}")
                if 'reason' in d:
                    lines.append(f"     原因: {d['reason']}")
        
        # 当前状态
        lines.append(f"\n📊 当前状态: {context.current_state}")
        
        # 用户偏好
        if context.user_preferences:
            lines.append("\n👤 用户偏好:")
            for p in context.user_preferences[-3:]:
                lines.append(f"  • {p}")
        
        # 最近对话 (保留最近3轮)
        if recent_messages:
            lines.append("\n💬 最近对话:")
            for m in recent_messages[-6:]:  # 最近6条 (3轮)
                role = "用户" if m.get("role") == "user" else "助手"
                content = m.get("content", "")[:200]  # 截断
                if len(m.get("content", "")) > 200:
                    content += "..."
                lines.append(f"  [{role}]: {content}")
        
        # 新查询
        lines.append(f"\n❓ 当前查询: {new_query}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def _extract_task(self, messages: List[Dict]) -> str:
        """提取任务描述"""
        # 从第一条用户消息提取
        for m in messages:
            if m.get("role") == "user":
                content = m.get("content", "")
                # 提取核心意图
                if "investment" in content.lower() or "投资" in content:
                    return "investment-research skill 开发优化"
                elif "skill" in content.lower():
                    return "skill 开发"
                return content[:100]
        return "Unknown task"
    
    def _extract_decisions(self, messages: List[Dict]) -> List[Dict]:
        """提取关键决策"""
        decisions = []
        
        for m in messages:
            content = m.get("content", "")
            
            # 匹配决策模式
            patterns = [
                r"(选择|决定|使用)\s*([^，。]+)",
                r"(修复|解决)\s*([^，。]+)",
                r"(添加|创建)\s*([^，。]+)",
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    decisions.append({
                        "decision": f"{match[0]}{match[1]}",
                        "timestamp": m.get("timestamp", "")
                    })
        
        return decisions
    
    def _extract_outcomes(self, messages: List[Dict]) -> List[str]:
        """提取结果"""
        outcomes = []
        
        for m in messages:
            content = m.get("content", "")
            
            # 匹配完成/成功模式
            if any(kw in content for kw in ["✅", "完成", "修复", "推送成功"]):
                # 提取行
                for line in content.split("\n"):
                    if any(kw in line for kw in ["✅", "修复", "完成"]):
                        outcomes.append(line.strip()[:100])
        
        return list(set(outcomes))  # 去重
    
    def _extract_errors(self, messages: List[Dict]) -> List[str]:
        """提取错误"""
        errors = []
        
        for m in messages:
            content = m.get("content", "")
            
            # 匹配错误模式
            if any(kw in content for kw in ["❌", "Error", "失败", "错误"]):
                for line in content.split("\n"):
                    if any(kw in line for kw in ["❌", "Error", "失败"]):
                        errors.append(line.strip()[:100])
        
        return list(set(errors))
    
    def _extract_preferences(self, messages: List[Dict]) -> List[str]:
        """提取用户偏好"""
        preferences = []
        
        for m in messages:
            content = m.get("content", "")
            
            # 匹配偏好模式
            patterns = [
                r"(重视|关注|需要|偏好)\s*([^，。]+)",
                r"(尽量|希望|要求)\s*([^，。]+)",
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    preferences.append(f"{match[0]}{match[1]}")
        
        return preferences
    
    def _extract_current_state(self, messages: List[Dict]) -> str:
        """提取当前状态"""
        # 从最后几条消息提取
        for m in reversed(messages[-5:]):
            content = m.get("content", "")
            
            if "推送到" in content and "GitHub" in content:
                return "已推送到 GitHub，运行正常"
            elif "修复" in content and "完成" in content:
                return "问题修复完成"
        
        return "进行中"
    
    def _extract_next_steps(self, messages: List[Dict]) -> List[str]:
        """提取下一步"""
        steps = []
        
        for m in messages:
            content = m.get("content", "")
            
            # 匹配下一步模式
            if any(kw in content for kw in ["下一步", "Next", "还需要"]):
                for line in content.split("\n"):
                    if any(kw in line for kw in ["下一步", "[ ]", "待实现"]):
                        steps.append(line.strip()[:100])
        
        return steps
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        return datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # 压缩规则
    def _compress_tool_calls(self, content: str) -> str:
        """压缩工具调用输出"""
        # 保留关键结果，丢弃详细输出
        if "exec" in content and "completed" in content:
            return "[命令执行完成]"
        return content
    
    def _compress_code(self, content: str) -> str:
        """压缩代码块"""
        # 如果代码块过长，只保留签名和关键部分
        lines = content.split("\n")
        if len(lines) > 20:
            return "\n".join(lines[:5]) + "\n... [代码省略] ...\n" + "\n".join(lines[-3:])
        return content
    
    def _compress_errors(self, content: str) -> str:
        """压缩重复错误"""
        # 相同错误只保留一次
        return content
    
    def _compress_listings(self, content: str) -> str:
        """压缩文件列表"""
        # 长列表只显示数量
        lines = content.split("\n")
        if len(lines) > 10:
            return f"[文件列表: {len(lines)} 项]"
        return content

# 便捷函数
def compress_if_needed(messages: List[Dict], new_query: str) -> str:
    """如果需要则压缩上下文"""
    compressor = ContextCompressor()
    
    if compressor.should_compress(messages):
        context = compressor.compress_session(messages)
        return compressor.create_compressed_prompt(context, messages[-3:], new_query)
    
    # 不需要压缩，返回原始格式
    return None

if __name__ == "__main__":
    # 测试
    compressor = ContextCompressor()
    
    # 模拟消息
    test_messages = [
        {"role": "user", "content": "帮我创建一个投资研究 skill"},
        {"role": "assistant", "content": "好的，我来设计... [长内容省略]"},
        {"role": "user", "content": "运行看看有什么问题"},
        {"role": "assistant", "content": "发现美股平均计算错误..."},
    ]
    
    context = compressor.compress_session(test_messages)
    print(json.dumps(asdict(context), indent=2, ensure_ascii=False))
