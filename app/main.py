from fastapi import FastAPI, Header, HTTPException
from app.models import CompressRequest, BatchCompressRequest, CompressResponse
from app.compressor import compress
import httpx
from typing import Optional
from fastapi.responses import RedirectResponse


app = FastAPI(title="Winnow API", version="0.1.1")


@app.get("/")
def root():
    return RedirectResponse(url="/docs")


def attach_savings(result: dict, price: Optional[float]) -> dict:
    if price:
        saved_tokens = result["original_tokens"] - result["compressed_tokens"]
        result["estimated_savings_usd"] = round((saved_tokens / 1_000_000) * price, 6)
    return result


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/compress", response_model=CompressResponse)
def compress_single(req: CompressRequest):
    result = compress(
        text=req.input,
        ratio=req.compression_ratio,
        protected=req.protected_strings,
        rag_mode=req.rag_mode,
        include_diff=req.diff,
        question=req.question
    )
    return attach_savings(result, req.price_per_million_tokens)


@app.post("/v1/compress/batch")
def compress_batch(req: BatchCompressRequest):
    results = [
        attach_savings(
            compress(
                text=text,
                ratio=req.compression_ratio,
                protected=req.protected_strings,
                rag_mode=req.rag_mode,
                include_diff=req.diff,
                question=req.question
            ),
            req.price_per_million_tokens
        )
        for text in req.inputs
    ]
    return {"results": results, "count": len(results)}


@app.post("/v1/chat/completions")
async def proxy(req: dict, authorization: str = Header(...)):
    messages = req.get("messages", [])
    ratio = req.pop("compression_ratio", 0.5)
    protected = req.pop("protected_strings", [])
    rag_mode = req.pop("rag_mode", False)
    question = req.pop("question", None)

    for msg in messages:
        if msg.get("role") == "user":
            result = compress(
                text=msg["content"],
                ratio=ratio,
                protected=protected,
                rag_mode=rag_mode,
                include_diff=False,
                question=question
            )
            msg["content"] = result["output"]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": authorization},
            json={**req, "messages": messages},
            timeout=60
        )
    return response.json()
