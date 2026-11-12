
import json
import time
import urllib.request


OLLAMA_URL = "http://localhost:11434/api/generate"

PROMPT = (
    "In one short sentence, explain a simple "
    "way a university student can manage exam stress."
)


def run_test(number):
    payload = {
        "model": "qwen2.5:3b",
        "prompt": PROMPT,
        "stream": False,
        "keep_alive": "30m",
        "options": {
            "num_predict": 80,
            "temperature": 0
        }
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    start = time.perf_counter()

    with urllib.request.urlopen(
        request,
        timeout=300
    ) as response:
        result = json.load(response)

    elapsed = time.perf_counter() - start

    def seconds(field):
        return result.get(field, 0) / 1_000_000_000

    print(f"\nTest {number}")
    print(f"Total wall time: {elapsed:.2f}s")
    print(
        f"Model loading: "
        f"{seconds('load_duration'):.2f}s"
    )
    print(
        f"Prompt evaluation: "
        f"{seconds('prompt_eval_duration'):.2f}s"
    )
    print(
        f"Generation: "
        f"{seconds('eval_duration'):.2f}s"
    )
    print(
        "Prompt tokens:",
        result.get("prompt_eval_count", 0)
    )
    print(
        "Generated tokens:",
        result.get("eval_count", 0)
    )


if __name__ == "__main__":
    print("STAGE 9C.2 - OLLAMA PERFORMANCE DIAGNOSTIC")
    print("=" * 60)

    run_test(1)
    run_test(2)
