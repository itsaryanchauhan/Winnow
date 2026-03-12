# Winnow 🌾

**Open-source RAG prompt compression middleware. Keep the signal. Drop the noise.**

> Built with FastAPI, LLMLingua-2, and tiktoken. MIT licensed, self-hostable, pip installable.

🌐 **[trywinnow.vercel.app](https://trywinnow.vercel.app)** · 📦 [PyPI](https://pypi.org/project/winnow-compress/) · 🤗 [HuggingFace Space](https://huggingface.co/spaces/itsaryanchauhan/winnow) · ⭐ [GitHub](https://github.com/itsaryanchauhan/Winnow)

---

## 🎯 What is Winnow?

Winnow sits between your vector database and your LLM. It takes raw retrieved document chunks, compresses them using LLMLingua-2 token-level scoring guided by your query, and returns a shorter context that preserves answer-relevant content — cutting token costs by ~50% with less than 3% accuracy loss.

## ✨ Key Features

- 🗜️ **Token Compression**: Cuts retrieved context by ~50% using LLMLingua-2
- 🎯 **Query-Guided**: Compression is steered by your question — relevant tokens survive
- 🔒 **Protected Words**: Mark phrases that must never be removed
- ⚖️ **Ratio Control**: Tune aggressiveness from 0.1 (light) to 0.9 (heavy)
- 🔌 **OpenAI-Compatible Proxy**: Drop-in `/v1/chat/completions` — zero code changes
- 🦜 **LangChain Integration**: Native `WinnowCompressor` drop-in wrapper
- 🐳 **Self-Hostable**: Single Docker command, no API key required
- 📦 **Pip Installable**: `pip install winnow-compress`

## 📊 Benchmarks

Tested on SQuAD with LLMLingua-2. Baseline F1: 78.4. Avg latency: ~85ms.

| Preset     | Ratio | Tokens In | Tokens Out | Reduction | F1 Score | F1 Drop |
| ---------- | ----- | --------- | ---------- | --------- | -------- | ------- |
| Light      | 0.7   | 420       | 294        | ~30%      | 77.6     | <1 pt   |
| Balanced   | 0.5   | 420       | 210        | ~50%      | 76.1     | 2.3 pt  |
| Aggressive | 0.3   | 420       | 147        | ~65%      | 73.4     | 5.0 pt  |

## 🚀 Quick Start

```bash
# Self-host in one command
docker run -p 8000:8000 itsaryanchauhan/winnow
```

API live at `http://localhost:8000` · Docs at `http://localhost:8000/docs`

<details>
<summary>📖 Full Integration Examples (Docker, pip, LangChain, REST, OpenAI Proxy)</summary>

### Option 1 — Self-host with Docker

```bash
docker run -p 8000:8000 itsaryanchauhan/winnow
```

### Option 2 — pip install

```bash
pip install winnow-compress
```

```python
from winnow import compress

result = compress(
    context=chunks,
    question=query,
    ratio=0.5
)

print(result["compressed_context"])
print(result["original_tokens"])     # e.g. 420
print(result["compressed_tokens"])   # e.g. 210
print(result["compression_ratio"])   # e.g. 0.5
print(result["savings_estimate"])    # e.g. "$0.000525"
```

### Option 3 — LangChain Drop-in

```python
from winnow.langchain import WinnowCompressor

compressor = WinnowCompressor(ratio=0.5)
compressed_docs = compressor.compress_documents(docs, query)
```

### Option 4 — REST API (curl)

```bash
curl -X POST http://localhost:8000/v1/compress \
  -H "Content-Type: application/json" \
  -d '{
    "context": "your retrieved chunks here",
    "question": "what is the capital of France?",
    "ratio": 0.5,
    "protect": ["Paris", "France"]
  }'
```

### Option 5 — OpenAI-Compatible Proxy

Zero code changes if you already use the OpenAI SDK — just swap the base URL:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": your_prompt}]
)
```

### Request Parameters

| Field      | Type     | Required | Description                                        |
| ---------- | -------- | -------- | -------------------------------------------------- |
| `context`  | string   | ✅       | Retrieved RAG chunks to compress                   |
| `question` | string   | ✅       | User query — guides which tokens to keep           |
| `ratio`    | float    | ❌       | Compression aggressiveness 0.1–0.9. Default: `0.5` |
| `protect`  | string[] | ❌       | Words/phrases that must not be removed             |

### Response Fields

| Field                | Type   | Description                          |
| -------------------- | ------ | ------------------------------------ |
| `compressed_context` | string | The compressed output                |
| `original_tokens`    | int    | Token count before compression       |
| `compressed_tokens`  | int    | Token count after compression        |
| `compression_ratio`  | float  | Actual ratio achieved                |
| `savings_estimate`   | string | Estimated USD saved (gpt-4o pricing) |

### Batch Compression

```bash
curl -X POST http://localhost:8000/v1/compress/batch \
  -H "Content-Type: application/json" \
  -d '{
    "contexts": ["chunk one...", "chunk two..."],
    "question": "your query",
    "ratio": 0.5
  }'
```

</details>

## 📁 Project Structure

```
Winnow/
├── app/               # FastAPI application
│   └── main.py        # API routes and server
├── winnow/            # pip package
│   ├── __init__.py    # compress() function
│   └── langchain.py   # WinnowCompressor
├── benchmarks/        # SQuAD benchmark scripts and results
├── tests/             # Test suite
├── website/           # Next.js website (trywinnow.vercel.app)
├── Dockerfile
└── pyproject.toml
```

## 🔌 API Endpoints

| Method | Endpoint               | Description                                   |
| ------ | ---------------------- | --------------------------------------------- |
| `POST` | `/v1/compress`         | Compress a single context                     |
| `POST` | `/v1/compress/batch`   | Compress multiple contexts                    |
| `POST` | `/v1/chat/completions` | OpenAI-compatible proxy with auto-compression |
| `GET`  | `/health`              | Health check                                  |

## 🛠️ Built With

- **API**: FastAPI + Python
- **Compression**: microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank
- **Tokenizer**: tiktoken (cl100k_base)
- **Deploy**: Docker + HuggingFace Spaces

## 👤 Author

Created by **Aryan Chauhan** ([@itsaryanchauhan](https://github.com/itsaryanchauhan))

## 📞 Get in Touch

Have questions or suggestions? Open an issue on the [GitHub repository](https://github.com/itsaryanchauhan/Winnow).

---

**MIT License · [Live Demo](https://trywinnow.vercel.app) · [HuggingFace Space](https://huggingface.co/spaces/itsaryanchauhan/winnow)**
