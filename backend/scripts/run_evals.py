"""
Usage:
  python backend/scripts/run_evals.py
  python backend/scripts/run_evals.py --prompt v2
"""
import argparse
import json
import subprocess
from pathlib import Path

EVALS_DIR = Path(__file__).parent.parent / "evals"
PROMPTFOO_CONFIG = EVALS_DIR / "promptfoo.yaml"
DATASETS_DIR = EVALS_DIR / "datasets"
REPORTS_DIR = EVALS_DIR / "reports"


def run_promptfoo(prompt_version: str):
    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / f"{prompt_version}.json"

    print(f"Running promptfoo eval for prompt: {prompt_version}")
    result = subprocess.run(
        ["npx", "promptfoo", "eval", "--config", str(PROMPTFOO_CONFIG), "--output", str(report_path)],
        capture_output=False,
    )

    if result.returncode == 0:
        print(f"Report saved to {report_path}")
    else:
        print("Eval failed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="base", help="Prompt version to evaluate")
    args = parser.parse_args()
    run_promptfoo(args.prompt)
