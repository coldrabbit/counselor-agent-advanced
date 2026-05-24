import io
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post("/recognize")
async def recognize_text(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="仅支持图片文件（jpg、png 等）")

    try:
        import pytesseract
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        text = pytesseract.image_to_string(image, lang="chi_sim+eng")
        return {"success": True, "text": text.strip()}
    except ImportError:
        raise HTTPException(status_code=500, detail="OCR 引擎未安装，请运行 brew install tesseract tesseract-lang 并安装 pytesseract")
    except Exception as e:
        logger.exception("OCR failed")
        raise HTTPException(status_code=500, detail=f"识别失败: {str(e)}")
