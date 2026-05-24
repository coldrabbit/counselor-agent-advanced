from unittest.mock import patch, MagicMock
from app.tasks.talk_record_task import generate_talk_record_task


def mock_record_response():
    return {
        "success": True,
        "content": '{"conversation_record":"谈话记录内容","risk_level":"medium","follow_up_advice":"跟进建议","parent_advice":"家校沟通建议"}',
        "model": "deepseek-chat",
        "token_usage": 1800,
        "duration_ms": 2500,
    }


@patch("app.tasks.talk_record_task.AIService")
def test_generate_talk_record_task_success(mock_ai_class):
    mock_ai = MagicMock()
    mock_ai.chat.return_value = mock_record_response()
    mock_ai_class.return_value = mock_ai

    result = generate_talk_record_task(
        student_name="李明",
        student_id="2024001",
        situation="近期旷课两次",
        counselor_profile=None,
    )

    assert result["success"] is True
    assert result["conversation_record"] == "谈话记录内容"
    assert result["risk_level"] == "medium"
    assert result["follow_up_advice"] == "跟进建议"
    assert result["parent_advice"] == "家校沟通建议"
    assert result["model"] == "deepseek-chat"
    assert result["token_usage"] == 1800
    assert result["duration_ms"] == 2500


@patch("app.tasks.talk_record_task.AIService")
def test_generate_talk_record_invalid_risk_level(mock_ai_class):
    response = mock_record_response()
    response["content"] = '{"conversation_record":"xxx","risk_level":"critical","follow_up_advice":"yyy","parent_advice":"zzz"}'
    mock_ai = MagicMock()
    mock_ai.chat.return_value = response
    mock_ai_class.return_value = mock_ai

    result = generate_talk_record_task(
        student_name="李明",
        student_id="2024001",
        situation="测试",
        counselor_profile=None,
    )

    assert result["success"] is True
    assert result["risk_level"] == "medium"
