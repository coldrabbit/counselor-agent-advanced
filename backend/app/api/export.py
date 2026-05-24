import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/export", tags=["export"])


class PDFRequest(BaseModel):
    title: str
    content: str


PDF_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<style>
  @page {{ size: A4; margin: 2cm; }}
  body {{ font-family: "PingFang SC", "Microsoft YaHei", sans-serif; color: #333; line-height: 1.8; font-size: 14px; }}
  h1 {{ color: #4a7c6f; border-bottom: 2px solid #7ec8a0; padding-bottom: 8px; font-size: 20px; }}
  .meta {{ color: #999; font-size: 12px; margin-bottom: 24px; }}
  .content {{ white-space: pre-wrap; margin-top: 16px; }}
  .footer {{ margin-top: 32px; padding-top: 8px; border-top: 1px solid #ddd; font-size: 11px; color: #aaa; text-align: center; }}
  .section {{ margin-bottom: 20px; }}
  .section-title {{ font-weight: bold; color: #4a7c6f; font-size: 15px; margin-bottom: 8px; }}
</style>
</head>
<body>
<h1>{title}</h1>
<div class="content">{content}</div>
<div class="footer">由 Counselor OS 生成 — {date}</div>
</body>
</html>"""


@router.post("/pdf")
def export_pdf(req: PDFRequest):
    from weasyprint import HTML
    from datetime import datetime

    try:
        html_content = PDF_TEMPLATE.format(
            title=req.title,
            content=req.content.replace("\n", "<br>"),
            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
        pdf_bytes = HTML(string=html_content).write_pdf()
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={req.title}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF生成失败: {str(e)}")
