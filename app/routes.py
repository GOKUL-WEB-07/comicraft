import logging
import re
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.models.schemas import PromptRequest
from app.services.gemini_service import generate_comic_story
from app.services.image_service import generate_image
from app.services.layout_builder import build_comic_layout
from app.services.pdf_service import save_comic_pdf
from app.services.pdf_service import EXPORTS_DIR

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
DEMO_NOTICE = "Demo mode: AI service unavailable, using generated sample content."


def create_comic(prompt: PromptRequest) -> dict:
    story, story_fallback = generate_comic_story(prompt)
    images = [generate_image(panel.image_prompt, panel.panel_number, prompt.art_style, panel.title)
              for panel in story.panels]
    layout = build_comic_layout(story, images)
    pdf_url = save_comic_pdf(story.comic_title, story.summary, layout)
    panels = [{key: value for key, value in panel.items() if key != "image_path"} for panel in layout]
    return {
        "comic": {"comic_title": story.comic_title, "summary": story.summary},
        "panels": panels, "pdf_url": pdf_url, "story_fallback": story_fallback,
        "image_fallback": any(image["fallback"] for image in images),
    }


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.post("/generate", response_class=HTMLResponse)
def generate(request: Request, story_prompt: str = Form(...), character_name: str = Form(...),
             setting: str = Form(...), tone: str = Form(...), art_style: str = Form(...)):
    try:
        prompt = PromptRequest(story_prompt=story_prompt, character_name=character_name,
                               setting=setting, tone=tone, art_style=art_style)
    except ValidationError:
        return templates.TemplateResponse(request, "error.html", {"message": "Please check the form fields and try again."}, status_code=422)
    try:
        result = create_comic(prompt)
    except Exception:
        logger.exception("Comic generation failed")
        return templates.TemplateResponse(request, "error.html", {"message": "We couldn't prepare your comic. Please try again."}, status_code=500)
    return templates.TemplateResponse(request, "comic_preview.html", result)


@router.post("/generate-comic/json")
def generate_json(prompt: PromptRequest):
    try:
        return {"success": True, **create_comic(prompt)}
    except Exception:
        logger.exception("JSON comic generation failed")
        raise HTTPException(status_code=500, detail="We couldn't prepare your comic. Please try again.") from None


@router.post("/test-image")
def test_image(prompt: str = Form(..., min_length=3, max_length=1200)):
    try:
        image = generate_image(prompt, 1, "Comic Book", "Test illustration")
        return {"success": True, "image_url": image["image_url"], "fallback": image["fallback"]}
    except Exception:
        logger.exception("Test image generation failed")
        raise HTTPException(status_code=500, detail="The image could not be created.") from None


@router.get("/export-success", response_class=HTMLResponse)
def export_success(request: Request, pdf: str = ""):
    match = re.fullmatch(r"/static/exports/(comic-[a-f0-9]{32}\.pdf)", pdf)
    pdf_url = pdf if match and (EXPORTS_DIR / match.group(1)).is_file() else ""
    return templates.TemplateResponse(request, "export_success.html", {"pdf_url": pdf_url})
