from importlib.resources import files
import json
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api import translate, sparql, chat


logging.root.setLevel(logging.DEBUG)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

SAMPLE_QUESTIONS = json.loads(
    files("resources").joinpath("sample_questions.json").read_text()
)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", dict(request=request, sample_questions=SAMPLE_QUESTIONS))

app.include_router(translate.router, prefix="/translate")
app.include_router(sparql.router, prefix="/sparql")
app.include_router(chat.router, prefix="/chat")