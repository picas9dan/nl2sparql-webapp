import logging
from fastapi import FastAPI

from api import translate

logger = logging.getLogger(__name__)
app = FastAPI()


app.include_router(translate.router, prefix="/translate")