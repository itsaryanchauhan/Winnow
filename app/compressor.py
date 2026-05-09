import torch
from llmlingua import PromptCompressor
from sentence_transformers import SentenceTransformer, util
from typing import Optional


_compressor = None
_embedder = None


def get_device():
    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


def get_compressor():
    global _compressor
    if _compressor is None:
        _compressor = PromptCompressor(
            model_name="microsoft/llmlingua-2-xlm-roberta-large-meetingbank",
            use_llmlingua2=True,
            device_map=get_device(),
            model_config={"cache_dir": "/tmp/winnow_cache"}
        )
    return _compressor


def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


def filter_by_question(text: str, question: str, keep_ratio: float = 0.75) -> str:
    """Drop sentences least semantically relevant to the question."""
    embedder = get_embedder()
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    if len(sentences) <= 2:
        return text

    q_emb = embedder.encode(question, convert_to_tensor=True)
    s_embs = embedder.encode(sentences, convert_to_tensor=True)
    scores = util.cos_sim(q_emb, s_embs)[0]

    cutoff = max(1, int(len(sentences) * keep_ratio))
    top_indices = sorted(
        sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)[:cutoff]
    )
    return ". ".join(sentences[i] for i in top_indices) + "."


def chunk_text(text: str, max_tokens: int = 400) -> list:
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_tokens):
        chunks.append(" ".join(words[i:i + max_tokens]))
    return chunks


def compress(
    text: str,
    ratio: float,
    protected: list,
    rag_mode: bool,
    include_diff: bool,
    question: Optional[str] = None
):
    comp = get_compressor()

    # Question-guided semantic pre-filter - runs before LLMLingua-2
    if question:
        text = filter_by_question(text, question, keep_ratio=0.6)

    words = text.split()

    if len(words) > 300:
        chunks = chunk_text(text, max_tokens=400)
        compressed_chunks = []
        total_original = 0
        total_compressed = 0

        for chunk in chunks:
            kwargs = dict(rate=ratio, force_tokens=protected)
            result = comp.compress_prompt([chunk], **kwargs)
            compressed_chunks.append(result["compressed_prompt"])
            total_original += result["origin_tokens"]
            total_compressed += result["compressed_tokens"]

        combined_output = " ".join(compressed_chunks)
        ratio_val = total_original / total_compressed if total_compressed > 0 else 1.0

        diff = None
        if include_diff:
            compressed_words = set(combined_output.split())
            diff = [{"token": w, "kept": w in compressed_words} for w in text.split()]

        return {
            "output": combined_output,
            "original_tokens": total_original,
            "compressed_tokens": total_compressed,
            "ratio": round(ratio_val, 2),
            "diff": diff
        }

    # Single chunk path
    kwargs = dict(rate=ratio, force_tokens=protected)
    result = comp.compress_prompt([text], **kwargs)

    diff = None
    if include_diff:
        compressed_words = set(result["compressed_prompt"].split())
        diff = [{"token": w, "kept": w in compressed_words} for w in text.split()]

    return {
        "output": result["compressed_prompt"],
        "original_tokens": result["origin_tokens"],
        "compressed_tokens": result["compressed_tokens"],
        "ratio": float(str(result["ratio"]).replace("x", "")),
        "diff": diff
    }
