"""Image provider and Pillow fallback."""

import logging
import os
import textwrap
from io import BytesIO
from functools import lru_cache
from pathlib import Path
from uuid import uuid4

from huggingface_hub import InferenceClient
from PIL import Image, ImageDraw, ImageFont, ImageOps

logger = logging.getLogger(__name__)
PANELS_DIR = Path(__file__).resolve().parents[1] / "static" / "panels"
DEFAULT_MODEL = "black-forest-labs/FLUX.1-schnell"
HOSTED_IMAGE_SIZE = 512
SAVED_IMAGE_SIZE = 768


@lru_cache(maxsize=2)
def _client(token: str) -> InferenceClient:
    return InferenceClient(api_key=token, timeout=35)


def _font(size: int, bold: bool = False):
    path = "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def _placeholder(number: int, title: str, art_style: str) -> Image.Image:
    image = Image.new("RGB", (768, 768), "#fff8e7")
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 20, 748, 748), outline="#181826", width=10)
    draw.polygon([(50, 90), (690, 50), (710, 410), (140, 500)], fill="#ffe263")
    draw.ellipse((340, 155, 710, 525), fill="#fa6475", outline="#181826", width=8)
    draw.polygon([(90, 360), (340, 190), (430, 420), (260, 610)], fill="#5ccac0", outline="#181826")
    draw.rounded_rectangle((72, 540, 696, 700), radius=20, fill="white", outline="#181826", width=6)
    draw.text((74, 65), f"PANEL {number}", font=_font(54, True), fill="#181826", stroke_width=1)
    lines = textwrap.wrap(title, width=22)[:2]
    for i, line in enumerate(lines):
        draw.text((105, 562 + i * 46), line, font=_font(38, True), fill="#181826")
    draw.text((105, 675), "AI illustration unavailable", font=_font(17), fill="#46465d")
    return image


def generate_image(prompt: str, panel_number: int, art_style: str, title: str = "Your story") -> dict:
    PANELS_DIR.mkdir(parents=True, exist_ok=True)
    file_name = f"{uuid4().hex}.jpg"
    path = PANELS_DIR / file_name
    fallback = False
    token = os.getenv("HF_TOKEN", "").strip() or os.getenv("HF_API_KEY", "").strip()
    if token:
        try:
            image = _client(token).text_to_image(
                prompt,
                model=os.getenv("HF_IMAGE_MODEL", "").strip() or DEFAULT_MODEL,
                width=HOSTED_IMAGE_SIZE,
                height=HOSTED_IMAGE_SIZE,
            )
            if isinstance(image, bytes):
                image = Image.open(BytesIO(image))
            if not isinstance(image, Image.Image):
                raise ValueError("Image provider returned an unsupported response")
            image = image.convert("RGB")
        except Exception:
            logger.exception("Hugging Face image generation failed for panel %s", panel_number)
            fallback = True
            image = _placeholder(panel_number, title, art_style)
    else:
        fallback = True
        image = _placeholder(panel_number, title, art_style)
    image = ImageOps.fit(image, (SAVED_IMAGE_SIZE, SAVED_IMAGE_SIZE), method=Image.Resampling.LANCZOS)
    image.save(path, "JPEG", quality=86, optimize=True)
    return {"image_url": f"/static/panels/{file_name}", "image_path": path, "fallback": fallback}
