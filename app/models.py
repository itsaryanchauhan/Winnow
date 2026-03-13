from pydantic import BaseModel, Field
from typing import Optional


class CompressRequest(BaseModel):
    input: str
    question: Optional[str] = None
    compression_ratio: float = Field(default=0.5, ge=0.1, le=0.9)
    protected_strings: list[str] = []
    rag_mode: bool = False
    diff: bool = False
    price_per_million_tokens: Optional[float] = None


class BatchCompressRequest(BaseModel):
    inputs: list[str]
    question: Optional[str] = None
    compression_ratio: float = Field(default=0.5, ge=0.1, le=0.9)
    protected_strings: list[str] = []
    rag_mode: bool = False
    diff: bool = False
    price_per_million_tokens: Optional[float] = None


class CompressResponse(BaseModel):
    output: str
    original_tokens: int
    compressed_tokens: int
    ratio: float
    diff: Optional[list[dict]] = None
    estimated_savings_usd: Optional[float] = None
