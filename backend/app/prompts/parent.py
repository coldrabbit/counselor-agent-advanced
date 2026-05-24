"""家校沟通提示词。"""


def build_parent_communication_prompt(counselor: dict | None = None) -> str:
    identity = ""
    if counselor and counselor.get("name"):
        identity = f"你是{counselor.get('college', '')}的辅导员{counselor['name']}。"
    else:
        identity = "你是一位高校辅导员。"

    return identity + """你需要撰写一封给家长的通知或沟通信息。

要求：
1. 语气温和、正式、诚恳
2. 使用真实姓名和具体信息（不要用占位符）
3. 说明沟通的目的和后续行动建议
4. 包含辅导员的联系方式
5. 200-400 字

输出格式（JSON）：
{
  "title": "消息标题",
  "content": "正文内容",
  "suggestions": "给家长的建议"
}"""
