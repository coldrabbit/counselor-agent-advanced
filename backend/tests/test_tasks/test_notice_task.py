from unittest.mock import patch, MagicMock
from app.tasks.notice_task import generate_notice_task


def mock_notice_response():
    return {
        "success": True,
        "content": '{"title":"关于召开防诈骗班会的通知","formal_notice":"正式通知内容","wechat_notice":"微信群通知内容","parent_notice":"家长通知内容","sms_notice":"短信简版内容"}',
        "model": "deepseek-chat",
        "token_usage": 1500,
        "duration_ms": 2000,
    }


@patch("app.tasks.notice_task.AIService")
def test_generate_notice_task_success(mock_ai_class):
    mock_ai = MagicMock()
    mock_ai.chat.return_value = mock_notice_response()
    mock_ai_class.return_value = mock_ai

    result = generate_notice_task(
        event="防诈骗班会",
        time="明天下午3点",
        location="A203",
        participants="全体同学",
        counselor_profile={"name": "张伟", "college": "计算机学院"},
    )

    assert result["success"] is True
    assert result["title"] == "关于召开防诈骗班会的通知"
    assert result["formal_notice"] == "正式通知内容"
    assert result["wechat_notice"] == "微信群通知内容"
    assert result["parent_notice"] == "家长通知内容"
    assert result["sms_notice"] == "短信简版内容"
    assert result["model"] == "deepseek-chat"
    assert result["token_usage"] == 1500
    assert result["duration_ms"] == 2000


@patch("app.tasks.notice_task.AIService")
def test_generate_notice_task_ai_failure(mock_ai_class):
    mock_ai = MagicMock()
    mock_ai.chat.return_value = {"success": False, "error": "API timeout"}
    mock_ai_class.return_value = mock_ai

    result = generate_notice_task(
        event="防诈骗班会",
        time="",
        location="",
        participants="",
        counselor_profile=None,
    )

    assert result["success"] is False
    assert "error" in result
