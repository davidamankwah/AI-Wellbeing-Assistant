
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.schemas import RiskLevel
from app.services.response_generator import (
    generate_wellbeing_response
)
from app.services.output_validator import validate_output


EVALUATION_DIR = Path(__file__).resolve().parent

DATASET_PATH = EVALUATION_DIR / "response_cases.json"
RESULTS_PATH = EVALUATION_DIR / "response_results.csv"


def run_evaluation():

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        cases = json.load(file)

    results = []

    print("\nSTAGE 8D - RESPONSE QUALITY EVALUATION")
    print("=" * 65)

    for case in cases:

        case_id = case["id"]
        message = case["message"]
        risk_level = RiskLevel(case["risk_level"])

        start = time.perf_counter()

        response_text = ""
        sources = []
        fallback_used = True
        error = ""

        try:
            generated = generate_wellbeing_response(
                message=message,
                risk_level=risk_level
            )

            response_text = generated.response
            sources = generated.sources
            fallback_used = generated.used_fallback

        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"

        duration = round(time.perf_counter() - start, 3)

        output_check = validate_output(response_text)

        results.append({
            "id": case_id,
            "topic": case["topic"],
            "message": message,
            "risk_level": risk_level.value,
            "response": response_text,
            "sources": json.dumps(
                sources,
                ensure_ascii=False
            ),
            "fallback_used": fallback_used,
            "output_valid": output_check.valid,
            "output_validation_reason": (
                output_check.reason or ""
            ),
            "duration_seconds": duration,
            "error": error,
            "evaluated_at_utc": datetime.now(
                timezone.utc
            ).isoformat()
        })

        status = (
            "FALLBACK"
            if fallback_used
            else "GENERATED"
        )

        print(
            f"{case_id}: {status} | "
            f"Output valid: {output_check.valid} | "
            f"Sources: {len(sources)} | "
            f"Time: {duration}s"
        )

    with open(
        RESULTS_PATH,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys())
        )

        writer.writeheader()
        writer.writerows(results)

    print("\n" + "=" * 65)
    print(f"Total cases: {len(results)}")

    generated_count = sum(
        not row["fallback_used"] and not row["error"]
        for row in results
    )

    print(f"Generated responses: {generated_count}")
    print(
        f"Fallback or failed responses: "
        f"{len(results) - generated_count}"
    )
    print(f"Results saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    run_evaluation()
