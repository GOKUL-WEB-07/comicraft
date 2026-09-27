"""Generate a structured comic story with Gemini or an honest demo fallback."""

import json
import logging
import os
import time

from google import genai
from google.genai import errors, types

from app.models.schemas import ComicStory, PromptRequest

logger = logging.getLogger(__name__)
DEFAULT_MODEL = "gemini-3.1-flash-lite"


def _demo_story(request: PromptRequest) -> ComicStory:
    name = request.character_name
    place = request.setting.lower()
    idea = request.story_prompt.rstrip(" .!?")
    beats = [
        ("The spark", f"{name} arrives in the {place} and notices something unusual.",
         f"It began with a simple idea: {idea}.", "This could be the start of something!"),
        ("A curious clue", f"A strange clue draws {name} deeper into the {place}.",
         f"Every step raised a new question for {name}.", "I need to find out what this means."),
        ("The challenge", f"An unexpected obstacle blocks {name}'s path.",
         f"For a moment, the adventure seemed impossible.", "I can think of another way."),
        ("A bold choice", f"{name} uses courage and quick thinking to overcome the obstacle.",
         f"A small brave choice changed everything.", "Here goes!"),
        ("A new beginning", f"The {place} feels brighter as {name} celebrates and looks ahead.",
         f"{name} discovered that an adventure can begin anywhere.", "What shall we explore next?"),
    ]
    panels = []
    for number, (title, scene, narration, dialogue) in enumerate(beats, 1):
        panels.append({
            "panel_number": number, "title": title, "scene_description": scene,
            "narration": narration, "dialogue": dialogue,
            "image_prompt": (
                f"{request.art_style} comic illustration. Main character {name}, same appearance "
                f"and outfit in every panel. {scene} In the {place}; expressive action and "
                f"emotion, clear composition, cinematic lighting, no text or speech bubbles. "
                f"Story context: {idea}."
            ),
        })
    return ComicStory(comic_title=f"{name} and the {request.setting} Adventure",
                      summary=f"A {request.tone.lower()} five-panel story about {name} in the {place}.",
                      panels=panels)


def generate_comic_story(request: PromptRequest) -> tuple[ComicStory, bool]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return _demo_story(request), True

    instruction = f"""You are an expert comic book writer and storyboard artist.
Create a cohesive five-panel comic from the user's idea. Maintain character consistency.
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Visual art style: {request.art_style}
User story: {request.story_prompt}
Create exactly five sequential panels. Each panel must move the story forward.
Return JSON only. Each panel requires panel_number, title, scene_description,
narration, dialogue, and image_prompt. Make the dialogue an empty string if absent.
Image prompts must describe character appearance, location, composition, lighting,
emotion, action and visual style. Repeat important character details in every image prompt.
"""
    try:
        with genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=30000)) as client:
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model=os.getenv("GEMINI_MODEL", "").strip() or DEFAULT_MODEL,
                        contents=instruction,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json", response_schema=ComicStory
                        ),
                    )
                    break
                except errors.ServerError:
                    if attempt:
                        raise
                    time.sleep(1)
        raw = (response.text or "").strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        return ComicStory.model_validate(json.loads(raw)), False
    except Exception:
        logger.exception("Gemini story generation failed; using demo content")
        return _demo_story(request), True
