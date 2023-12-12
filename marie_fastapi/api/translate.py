import time
from fastapi import APIRouter
from pydantic import BaseModel

from services.preprocessing import sanitize_quantities
from services.translate import MultiDomainTranslator


class TranslateRequest(BaseModel):
    question: str


class TranslateResponseSparql(BaseModel):
    predicted: str
    postprocessed: str


class TranslateResponse(BaseModel):
    question: str
    preprocessed_question: str
    domain: str
    sparql: TranslateResponseSparql
    latency: float


router = APIRouter()


@router.post("/")
def translate(req: TranslateRequest):
    print("Received request to translation endpoint with the following request body")
    print(req)

    sanitized_inputs = sanitize_quantities(req.question)
    print("Santized inputs: " + str(sanitized_inputs))

    print("Sending translation request to triton server")
    translator = MultiDomainTranslator()
    start = time.time()
    translation_result = translator.nl2sparql(
        sanitized_inputs["preprocessed_text_for_trans"]
    )
    end = time.time()

    print("Translation result: " + str(translation_result))

    return TranslateResponse(
        question=req.question,
        preprocessed_question=sanitized_inputs["preprocessed_text_for_user"],
        domain=translation_result["domain"],
        sparql=TranslateResponseSparql(
            predicted=translation_result["sparql"]["decoded"],
            postprocessed=translation_result["sparql"]["verbose"],
        ),
        latency=end - start,
    )
