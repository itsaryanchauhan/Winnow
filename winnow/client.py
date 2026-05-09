import httpx
from typing import Optional

class Winnow:
    def __init__(self, base_url: str = "https://yourusername-winnow.hf.space"):
        self.base_url = base_url.rstrip("/")

    def compress(
        self,
        text: str,
        compression_ratio: float = 0.5,
        protected_strings: list = [],
        rag_mode: bool = False,
        diff: bool = False,
        question: Optional[str] = None,
        price_per_million_tokens: Optional[float] = None
    ) -> dict:
        response = httpx.post(
            f"{self.base_url}/v1/compress",
            json={
                "input": text,
                "compression_ratio": compression_ratio,
                "protected_strings": protected_strings,
                "rag_mode": rag_mode,
                "diff": diff,
                "question": question,
                "price_per_million_tokens": price_per_million_tokens
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()

    def compress_batch(
        self,
        texts: list[str],
        compression_ratio: float = 0.5,
        protected_strings: list = [],
        rag_mode: bool = False,
        question: Optional[str] = None,
        price_per_million_tokens: Optional[float] = None
    ) -> list[dict]:
        response = httpx.post(
            f"{self.base_url}/v1/compress/batch",
            json={
                "inputs": texts,
                "compression_ratio": compression_ratio,
                "protected_strings": protected_strings,
                "rag_mode": rag_mode,
                "question": question,
                "price_per_million_tokens": price_per_million_tokens
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()["results"]
