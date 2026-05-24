from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.notify.wechat import WeChatNotifier

router = APIRouter(prefix="/notify", tags=["notify"])


class WeChatMessage(BaseModel):
    content: str
    msgtype: str = "markdown"


@router.post("/wechat")
async def send_wechat(msg: WeChatMessage):
    notifier = WeChatNotifier()
    if not notifier.is_configured():
        raise HTTPException(status_code=400, detail="企业微信 Webhook 未配置，请在 .env 中设置 WECHAT_WEBHOOK_URL")
    if msg.msgtype == "markdown":
        result = await notifier.send_markdown(msg.content)
    else:
        result = await notifier.send_text(msg.content)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "发送失败"))
    return {"ok": True}


@router.get("/wechat/status")
def wechat_status():
    return {"configured": WeChatNotifier().is_configured()}
