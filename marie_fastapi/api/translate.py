import logging
import time
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

from services.preprocessing import preprocess_text
from services.translate import Translator


class TranslateRequest(BaseModel):
    question: str


class TranslateResponseSparql(BaseModel):
    predicted: str
    postprocessed: Optional[str]


class TranslateResponse(BaseModel):
    question: str
    preprocessed_question: str
    domain: str
    sparql: TranslateResponseSparql
    latency: float


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("")
def translate(req: TranslateRequest):
    logger.info(
        "Received request to translation endpoint with the following request body"
    )
    logger.info(req)

    preprocessed_text = preprocess_text(req.question)
    logger.info("Preprocessed text: " + str(preprocessed_text))

    logger.info("Sending translation request to triton server")
    translator = Translator()
    start = time.time()
    translation_result = translator.nl2sparql(preprocessed_text.for_trans)
    end = time.time()

    logger.info("Translation result: " + str(translation_result))

    return TranslateResponse(
        question=req.question,
        preprocessed_question=preprocessed_text.for_user,
        domain=translation_result.domain,
        sparql=TranslateResponseSparql(
            predicted=translation_result.sparql.decoded,
            postprocessed=translation_result.sparql.verbose,
        ),
        latency=end - start,
    )
