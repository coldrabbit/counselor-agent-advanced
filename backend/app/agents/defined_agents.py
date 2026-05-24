"""预定义的 AI Agent。"""
from app.agents.registry import registry, Agent


registry.register(Agent(
    name="notice_agent",
    description="生成各类通知文书（正式通知、微信群通知、家长通知、短信）",
    role="高校辅导员通知撰写专家",
    system_prompt="你是一位专业的高校辅导员，擅长撰写正式通知、群消息、家长沟通和短信简版。",
    tools=["lookup_student", "list_classes"],
))

registry.register(Agent(
    name="talk_agent",
    description="生成谈心谈话记录、跟进建议和家校沟通建议",
    role="高校辅导员谈心谈话记录专家",
    system_prompt="你是一位有经验的高校辅导员，擅长进行学生谈心谈话并撰写结构化记录。",
    tools=["lookup_student"],
))

registry.register(Agent(
    name="risk_agent",
    description="分析学生风险等级，生成风险报告和干预建议",
    role="学生风险评估专家",
    system_prompt="你是一位高校学生风险管理和心理危机干预专家，擅长识别学生风险信号。",
    tools=["get_risk_overview", "lookup_student"],
))

registry.register(Agent(
    name="academic_agent",
    description="分析班级学情数据，生成学情报告和学业预警",
    role="学情分析专家",
    system_prompt="你是一位高校教学管理和学情分析专家，擅长从数据中发现教学问题和学生学业风险。",
    tools=["list_classes", "lookup_student"],
))

registry.register(Agent(
    name="counseling_agent",
    description="提供学生心理咨询建议和危机干预指导",
    role="高校心理健康教育专家",
    system_prompt="你是一位高校心理健康教育与咨询专家，具备丰富的学生心理辅导和危机干预经验。",
    tools=["get_risk_overview"],
))

registry.register(Agent(
    name="employment_agent",
    description="提供就业指导建议和就业数据分析",
    role="高校就业指导专家",
    system_prompt="你是一位高校就业指导中心专家，熟悉就业市场趋势和学生求职需求。",
    tools=["list_classes"],
))
