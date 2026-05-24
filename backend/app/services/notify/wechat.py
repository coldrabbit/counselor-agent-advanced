import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class WeChatNotifier:
    """企业微信群机器人消息推送。"""

    def __init__(self):
        self.webhook_url = settings.wechat_webhook_url

    def is_configured(self) -> bool:
        return bool(self.webhook_url)

    async def send_markdown(self, content: str) -> dict:
        """发送 Markdown 格式消息到企业微信群。"""
        if not self.is_configured():
            return {"success": False, "error": "企业微信 Webhook 未配置"}

        payload = {"msgtype": "markdown", "markdown": {"content": content}}
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.webhook_url, json=payload, timeout=10)
                data = resp.json()
                if data.get("errcode") == 0:
                    logger.info("WeChat message sent successfully")
                    return {"success": True}
                else:
                    logger.error(f"WeChat send failed: {data}")
                    return {"success": False, "error": data.get("errmsg", "Unknown error")}
        except Exception as e:
            logger.exception("WeChat send error")
            return {"success": False, "error": str(e)}

    async def send_text(self, content: str, mentioned_list: list[str] | None = None) -> dict:
        """发送文本消息，可 @指定成员（通过手机号）。"""
        if not self.is_configured():
            return {"success": False, "error": "企业微信 Webhook 未配置"}

        payload = {"msgtype": "text", "text": {"content": content}}
        if mentioned_list:
            payload["text"]["mentioned_mobile_list"] = mentioned_list

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.webhook_url, json=payload, timeout=10)
                data = resp.json()
                return {"success": data.get("errcode") == 0, "error": data.get("errmsg", "")}
        except Exception as e:
            return {"success": False, "error": str(e)}
