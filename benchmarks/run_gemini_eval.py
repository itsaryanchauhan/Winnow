from datasets import load_dataset
from app.compressor import compress
from google import genai
from dotenv import load_dotenv
import json, os, time

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

GEMINI_MODEL = "gemini-2.0-flash-lite"

def ask_gemini(context: str, question: str, retries: int = 4) -> str:
    prompt = f"Answer this question using only the context below. Be concise.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:"
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                if attempt < retries - 1:
                    wait = 60 * (attempt + 1)   # 60s, 120s, 180s
                    print(f"  Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                else:
                    print("  Daily quota exhausted. Stop and resume tomorrow.")
                    raise SystemExit(1)
            elif "404" in error_str:
                raise RuntimeError(f"Model not found: {GEMINI_MODEL}") from e
            else:
                print(f"  Skipping - API error: {e}")
                return ""
    return ""

def answer_matches(predicted: str, gold_answers: list) -> bool:
    predicted = predicted.lower().strip()
    return any(ans.lower().strip() in predicted or predicted in ans.lower().strip()
               for ans in gold_answers)

PARTIAL_PATH = "benchmarks/results/gemini_partial.json"

def load_partial():
    if os.path.exists(PARTIAL_PATH):
        with open(PARTIAL_PATH) as f:
            return json.load(f)
    return {"completed": [], "baseline_correct": 0, "compressed_correct": 0, "tokens_saved": []}

def save_partial(state):
    os.makedirs("benchmarks/results", exist_ok=True)
    with open(PARTIAL_PATH, "w") as f:
        json.dump(state, f, indent=2)

print("Loading SQuAD 2.0 (50 samples for Gemini eval)...")
dataset = load_dataset("rajpurkar/squad_v2", split="validation[:50]")
answerable = [item for item in dataset if len(item["answers"]["text"]) > 0][:10]

state = load_partial()
completed_indices = set(state["completed"])
baseline_correct = state["baseline_correct"]
compressed_correct = state["compressed_correct"]
tokens_saved = state["tokens_saved"]

remaining = len(answerable) - len(completed_indices)
print(f"Running Gemini eval on {len(answerable)} questions ({len(completed_indices)} already done, {remaining} remaining)...\n")

for i, item in enumerate(answerable):
    if i in completed_indices:
        print(f"[{i+1}/{len(answerable)}] Skipping (already completed)")
        continue

    context = item["context"]
    question = item["question"]
    answers = item["answers"]["text"]

    baseline_answer = ask_gemini(context, question)
    baseline_hit = answer_matches(baseline_answer, answers)
    if baseline_hit:
        baseline_correct += 1

    input_text = f"Question: {question}\n\nDocument: {context}"
    result = compress(input_text, ratio=0.5, protected=[], rag_mode=True, include_diff=False)
    compressed_answer = ask_gemini(result["output"], question)
    compressed_hit = answer_matches(compressed_answer, answers)
    if compressed_hit:
        compressed_correct += 1

    reduction = round((1 - result["compressed_tokens"] / result["original_tokens"]) * 100)
    tokens_saved.append(1 - result["compressed_tokens"] / result["original_tokens"])

    state["completed"].append(i)
    state["baseline_correct"] = baseline_correct
    state["compressed_correct"] = compressed_correct
    state["tokens_saved"] = tokens_saved
    save_partial(state)

    print(f"[{i+1}/{len(answerable)}] baseline={'✅' if baseline_hit else '❌'} compressed={'✅' if compressed_hit else '❌'} | reduction={reduction}%")
    time.sleep(5)

total = len(answerable)
baseline_acc = round(baseline_correct / total * 100, 1)
compressed_acc = round(compressed_correct / total * 100, 1)
avg_reduction = round(sum(tokens_saved) / len(tokens_saved) * 100, 1)
diff_pp = round(compressed_acc - baseline_acc, 1)

summary = {
    "model": GEMINI_MODEL,
    "samples": total,
    "baseline_accuracy_pct": baseline_acc,
    "compressed_accuracy_pct": compressed_acc,
    "accuracy_diff_pp": diff_pp,
    "avg_token_reduction_pct": avg_reduction
}

print(f"\n=== Gemini LLM Evaluation Results ===")
print(f"Baseline accuracy:    {baseline_acc}%")
print(f"Compressed accuracy:  {compressed_acc}%")
print(f"Difference:           {diff_pp:+}pp")
print(f"Avg token reduction:  {avg_reduction}%")

os.makedirs("benchmarks/results", exist_ok=True)
with open("benchmarks/results/gemini_eval.json", "w") as f:
    json.dump(summary, f, indent=2)

# Clean up partial file on success
if os.path.exists(PARTIAL_PATH):
    os.remove(PARTIAL_PATH)

print("\nSaved to benchmarks/results/gemini_eval.json")
