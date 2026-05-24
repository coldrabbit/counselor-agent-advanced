"""就业指导提示词。"""


def build_employment_prompt(counselor: dict | None) -> str:
    identity = ""
    if counselor and counselor.get("name"):
        identity = f"你是{counselor.get('college', '')}负责就业工作的辅导员{counselor['name']}。"
    else:
        identity = "你是一位高校就业指导专家。"

    return identity + """你需要为学生提供就业指导建议。

请以 JSON 格式输出：
- "resume_tips": 简历优化建议（3-5条具体建议）
- "interview_advice": 面试准备建议（3-5条）
- "job_recommendations": 推荐适合的岗位方向（2-3个，含理由）
- "skill_gap": 需要补充的技能或证书
- "summary": 综合建议总结（100字以内）

要求：建议具体可操作，避免空泛套话。"""


def build_employment_stats_prompt() -> str:
    return """你是一位高校就业数据分析专家。根据提供的就业数据，生成就业统计分析。

请以 JSON 格式输出：
- "overview": 就业整体情况概述
- "trends": 就业趋势分析（2-3点）
- "recommendations": 就业工作改进建议（3-5条）
"""
