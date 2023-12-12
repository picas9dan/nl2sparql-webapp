import json
import logging
import os
import time
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    data: str


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("")
async def chat(req: ChatRequest):
    logger.info("Request received to chat endpoint with the following request body")
    logger.info(req)

    CHATBOT_ENDPOINT = os.getenv("CHATBOT_ENDPOINT", "http://localhost:8001/v1")
    logger.info("Connecting to chatbot at endpoint: " + CHATBOT_ENDPOINT)
    chatbot_client = OpenAI(base_url=CHATBOT_ENDPOINT, api_key="placeholder")

    def make_chatbot_response_stream(question: str, data: str):
        prompt_template = "## Query:\n{query}\n\n### Data:\n{data}"
        return chatbot_client.chat.completions.create(
            model="llama-2-7b-chat.Q4_K_M.gguf",
            messages=[
                {
                    "role": "system",
                    "content": "You are a chatbot that succinctly responds to user queries.",
                },
                {
                    "role": "user",
                    "content": prompt_template.format(query=question, data=data),
                },
            ],
            stream=True,
        )

    def generate():
        start = time.time()
        for chunk in make_chatbot_response_stream(req.question, req.data):
            content = chunk.choices[0].delta.content
            if content is not None:
                yield "data: {data}\n\n".format(
                    data=json.dumps(
                        {"content": content, "latency": time.time() - start}
                    )
                )

    return StreamingResponse(generate(), media_type="text/event-stream")
