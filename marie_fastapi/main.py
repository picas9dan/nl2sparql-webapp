import logging
from fastapi import FastAPI

from api import translate, sparql

logger = logging.getLogger(__name__)
app = FastAPI()


app.include_router(translate.router, prefix="/translate")
app.include_router(sparql.router, prefix="/sparql")
