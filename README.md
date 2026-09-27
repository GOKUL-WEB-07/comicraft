# ComicCraft — AI Comic Story Creator

ComicCraft turns a short idea into a five-panel comic with illustrations, a preview, and a downloadable PDF. It is a small local FastAPI project for college demonstrations. No database or account is needed.

## Install on Windows

1. Install Python 3.11 or newer.
2. Open a terminal in this project folder.
3. Run:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
```

4. Edit `.env` and add your API keys if available. Both keys are optional for a demo. A sample is:

```dotenv
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-3.1-flash-lite
HF_TOKEN=your-hugging-face-token
HF_API_KEY=
HF_IMAGE_MODEL=black-forest-labs/FLUX.1-schnell
```

Replace the sample values with your own credentials. Keep `.env` private; it is listed in `.gitignore`. You can leave either key blank.
5. Start the app:

```powershell
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. API docs: http://127.0.0.1:8000/docs.

## Environment variables

| Variable | Purpose |
| --- | --- |
| `GEMINI_API_KEY` | Gemini story generation; optional |
| `HF_TOKEN` | Hugging Face image generation; preferred token name, optional |
| `HF_API_KEY` | Alternative Hugging Face token name; used when `HF_TOKEN` is empty |
| `GEMINI_MODEL` | Gemini model ID, default `gemini-3.1-flash-lite` |
| `HF_IMAGE_MODEL` | Hugging Face text-to-image model ID, default `black-forest-labs/FLUX.1-schnell` |

The Gemini service asks the configured model for a JSON comic and validates exactly five ordered panels. If the request or validation fails, it uses the demo story. The Hugging Face service sends each panel's image prompt to the configured text-to-image model, requests a 512×512 image, and saves a compressed JPEG under `app/static/panels/`. Use a Hugging Face token with Inference Providers permission and a model your account can access. Hosted generation may use provider credits. The model IDs can be changed in `.env`.

## Demo mode

With no Gemini key, ComicCraft builds a deterministic five-panel sample from the entered details and labels it as demo content. With no Hugging Face token, or when image generation fails, Pillow creates illustrated placeholder panels marked as such. The two services fall back independently: a real Gemini story can still have placeholder images. The preview and PDF still work. If an API request fails, technical details are logged in the terminal.

## How it works

`app/routes.py` validates input and shares one generation workflow between the form and JSON API. `gemini_service.py` produces structured story data, `image_service.py` creates five pictures, `layout_builder.py` pairs panels with images, and `pdf_service.py` exports the comic. Templates and static assets display the result.

Routes: `GET /`, `POST /generate` (form), `POST /generate-comic/json` (JSON), `POST /test-image` (form field `prompt`), and `GET /export-success`.

Generated images are saved in `app/static/panels/`; PDFs are saved in `app/static/exports/`. Both folders are ignored by Git because each request creates new files. You can remove old generated files manually when no longer needed.

## Limits

The fallback story is a fixed five-beat structure based on user input. Hosted image output and character consistency depend on the selected model and provider. Generated files remain on disk until removed. The PDF uses a standard Latin-1 font, so unsupported characters become `?` in the export.
