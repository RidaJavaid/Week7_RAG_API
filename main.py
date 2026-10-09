import asyncio
import logging
import threading
import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from starlette.concurrency import run_in_threadpool

from ingestion import ingest_document
from rag import ask_rag, rebuild_index

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI application
app = FastAPI(
    title="Week 7 RAG API",
    description="Hybrid RAG API with latency and cost tracking",
    version="1.1"
)

ingestion_lock = threading.Lock()


# Request models
class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value):
        value = value.strip()

        if len(value) < 3:
            raise ValueError(
                "Question must have at least 3 characters"
            )

        return value


class DocumentRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=100000)


# Home endpoint
@app.get("/")
def home():
    return {
        "status": "running",
        "message": "Week 7 RAG API",
        "performance_tracking": "enabled"
    }


# Health endpoint
@app.get("/health")
def health():
    return {"status": "healthy"}


# RAG processing with timing
def process_question(question: str):
    start_time = time.perf_counter()

    result = ask_rag(question)

    total_time = time.perf_counter() - start_time

    if result is None:
        raise ValueError(
            "ask_rag returned None. Check rag.py."
        )

    if not isinstance(result, dict):
        raise ValueError(
            "ask_rag must return a dictionary."
        )

    result["total_latency_seconds"] = round(
        total_time, 4
    )

    logger.info(
        "RAG processing latency: %.4f seconds",
        total_time
    )

    return result


# Ask endpoint
@app.post("/ask")
async def ask(request: QuestionRequest):
    try:
        result = await run_in_threadpool(
            process_question,
            request.question
        )

        return result

    except TimeoutError as error:
        logger.exception("RAG timeout")

        raise HTTPException(
            status_code=504,
            detail=str(error)
        )

    except Exception as error:
        logger.exception("RAG request failed")

        raise HTTPException(
            status_code=500,
            detail=f"{type(error).__name__}: {error}"
        )


# Streaming endpoint
@app.post("/ask/stream")
async def ask_stream(request: QuestionRequest):
    try:
        result = await run_in_threadpool(
            process_question,
            request.question
        )

    except Exception as error:
        logger.exception("Streaming RAG failed")

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    async def generate():
        answer = str(result.get("answer", ""))
        source = result.get("source")

        if source:
            answer += f" [Source: {source}]"

        for word in answer.split():
            yield word + " "
            await asyncio.sleep(0.03)

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )


# Document ingestion
def process_ingestion(filename, content):
    with ingestion_lock:
        result = ingest_document(
            filename,
            content.encode("utf-8")
        )

        if result["status"] == "indexed":
            result["total_vectors"] = rebuild_index()

        return result


# Ingestion endpoint
@app.post("/ingest")
async def ingest(request: DocumentRequest):
    try:
        return await run_in_threadpool(
            process_ingestion,
            request.filename,
            request.content
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        logger.exception("Document ingestion failed")

        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed"
        )