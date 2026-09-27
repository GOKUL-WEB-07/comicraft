from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


Setting = Literal["Forest", "School", "Space", "City", "Fantasy Kingdom", "Haunted House"]
Tone = Literal["Light-hearted", "Dramatic", "Funny", "Poetic", "Adventure", "Mysterious"]
ArtStyle = Literal["Comic Book", "Anime", "Pixel Art", "Realistic", "Watercolor", "Cartoon"]


class PromptRequest(BaseModel):
    story_prompt: str = Field(min_length=15, max_length=1000)
    character_name: str = Field(min_length=1, max_length=60)
    setting: Setting
    tone: Tone
    art_style: ArtStyle

    @field_validator("story_prompt", "character_name", mode="before")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value


class ComicPanel(BaseModel):
    panel_number: int = Field(ge=1, le=5)
    title: str = Field(min_length=1, max_length=100)
    scene_description: str = Field(min_length=1, max_length=700)
    narration: str = Field(min_length=1, max_length=700)
    dialogue: str = Field(max_length=400)
    image_prompt: str = Field(min_length=1, max_length=1200)


class ComicStory(BaseModel):
    comic_title: str = Field(min_length=1, max_length=120)
    summary: str = Field(min_length=1, max_length=500)
    panels: list[ComicPanel] = Field(min_length=5, max_length=5)

    @model_validator(mode="after")
    def check_panel_order(self):
        if [panel.panel_number for panel in self.panels] != [1, 2, 3, 4, 5]:
            raise ValueError("Panels must be numbered 1 through 5 in order")
        return self
