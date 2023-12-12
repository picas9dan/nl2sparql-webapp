import time
from fastapi import APIRouter
from pydantic import BaseModel

from services.kg_execute import KgExecutor


class SparqlRequest(BaseModel):
    query: str
    domain: str


class SparqlResponse(BaseModel):
    data: dict
    latency: float


router = APIRouter()


@router.post("/")
async def query(req: SparqlRequest):
    print("Received request to KG execution endpoint with the following request body")
    print(req)

    kg_executor = KgExecutor()
    start = time.time()
    data = kg_executor.query(domain=req.domain, query=req.query)
    end = time.time()

    return SparqlResponse(data=data, latency=end - start)
