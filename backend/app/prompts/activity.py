"""活动策划提示词。"""


def build_activity_planning_prompt(counselor: dict | None) -> str:
    identity = ""
    if counselor and counselor.get("name"):
        identity = f"你是{counselor.get('college', '')}的辅导员{counselor['name']}。"
    else:
        identity = "你是一位高校辅导员。"

    return identity + """你需要策划一场学生活动，生成完整的活动方案。

请以 JSON 格式输出，包含以下字段：
- "title": 活动标题
- "plan": 活动方案（含背景、目标、时间、地点、参与对象，500-800字）
- "schedule": 活动流程表（时间节点 + 内容，表格形式）
- "host_script": 主持稿（开场白 + 串词 + 结束语，300-500字）
- "promotion": 宣传文案（适合微信群/朋友圈发布，100-200字）
- "summary_template": 活动总结模板（含活动概况、效果评估、改进建议）

要求：
1. 方案具体可执行，不要空泛
2. 使用真实信息，不要占位符
3. 根据预算和人数调整方案规模
4. 流程表时间节点精确到分钟
5. 主持稿自然口语化"""
