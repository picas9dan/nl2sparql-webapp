from importlib.resources import files
import json
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")

SAMPLE_QUESTIONS = json.loads(
    files("resources").joinpath("sample_questions.json").read_text()
)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html", dict(request=request, sample_questions=SAMPLE_QUESTIONS)
    )
