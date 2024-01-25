from importlib.resources import files
import json
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")

CHEMISTRY_SAMPLE_QUESTIONS = json.loads(
    files("resources.chemistry").joinpath("sample_questions.json").read_text()
)
CHEMISTRY_METADATA = json.loads(
    files("resources.chemistry").joinpath("metadata.json").read_text()
)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "qa.html",
        dict(
            request=request,
            title=CHEMISTRY_METADATA["title"],
            subtitle=CHEMISTRY_METADATA["subtitle"],
            sample_questions=CHEMISTRY_SAMPLE_QUESTIONS,
        ),
    )
