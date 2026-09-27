from app.models.schemas import ComicStory


def build_comic_layout(story_data: ComicStory, generated_images: list[dict]) -> list[dict]:
    if len(story_data.panels) != 5 or len(generated_images) != 5:
        raise ValueError("A comic requires exactly five panels and images")
    return [
        {**panel.model_dump(), **image}
        for panel, image in zip(story_data.panels, generated_images, strict=True)
    ]
