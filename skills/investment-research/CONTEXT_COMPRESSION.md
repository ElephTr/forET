# 上下文压缩与记忆系统设计

## 核心原则

1. **分层存储**
   - L1: 当前对话 (完整，最近10轮)
   - L2: 会话摘要 (压缩，关键决策+结果)
   - L3: 长期记忆 (跨会话，模式/偏好)

2. **主动压缩触发条件**
   - 对话轮数 > 10
   - token 估算 > 4000
   - 任务完成/切换时

3. **摘要生成策略**
   - 保留：决策、结果、错误、用户偏好
   - 丢弃：中间尝试、重复信息、已修复问题
   - 格式：结构化，便于检索

## 实现方案

### 1. 会话内压缩 (Session-level)

```python
class ContextCompressor:
    def compress(self, messages: List[Message]) -> Summary:
        # 提取关键信息
        decisions = extract_decisions(messages)
        outcomes = extract_outcomes(messages)
        errors = extract_errors(messages)
        
        return Summary(
            task=identify_task(messages),
            decisions=decisions,
            outcomes=outcomes,
            errors=errors,
            current_state=get_final_state(messages)
        )
```

### 2. 跨会话记忆 (Cross-session)

存储在 `memory/sessions/YYYY-MM-DD-HH-MM-{task}.md`

格式：
```markdown
# Session Summary: {Task Name}
- Date: 2026-03-09
- Duration: 45min
- Status: ✅ Completed

## Key Decisions
1. 使用 Yahoo Finance + 东方财富 多源获取
2. 排除 VIX 从股指平均计算
3. 添加 A 股情绪模块

## Outcomes
- ✅ 修复 5 个核心问题
- ✅ 新增 A 股数据源
- ⚠️ 宏观数据需 FRED API Key

## User Preferences
- 重视数据可信度 (多源验证)
- 需要 A 股市场覆盖
- 偏好结构化输出

## Next Steps
- [ ] 添加技术指标
- [ ] 接入新闻情绪
```

### 3. 检索策略

```python
def retrieve_relevant_context(query: str) -> List[Summary]:
    # 语义搜索历史会话
    relevant = search_memory(query)
    
    # 按相关性和时间排序
    ranked = rank_by_relevance(relevant, query)
    
    # 取 Top 3
    return ranked[:3]
```

## 当前实现

立即执行：
1. 创建会话摘要 (本会话)
2. 存储到 memory/
3. 后续对话优先加载摘要

## 预期效果

| 指标 | 优化前 | 优化后 |
|-----|-------|-------|
| 平均上下文长度 | 8000+ tokens | 2000 tokens |
| 响应延迟 | 高 | 降低 50%+ |
| 成本 | 高 | 降低 60%+ |
| 信息保留 | 完整但冗余 | 精简但关键 |
