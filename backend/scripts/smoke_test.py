"""
Usage: python backend/scripts/smoke_test.py
Hits every endpoint and prints pass/fail.
"""
import httpx

BASE = "http://localhost:4000"

tests = [
    ("GET",  "/health",           None),
    ("POST", "/api/completions",  {"prompt": "Say hello", "max_tokens": 20}),
    ("POST", "/api/chat",         {"messages": [{"role": "user", "content": "Hello"}]}),
]


def run():
    passed, failed = 0, 0
    with httpx.Client(timeout=60) as client:
        for method, path, body in tests:
            try:
                if method == "GET":
                    r = client.get(f"{BASE}{path}")
                else:
                    r = client.post(f"{BASE}{path}", json=body)

                status = "PASS" if r.status_code < 400 else "FAIL"
                print(f"[{status}] {method} {path} → {r.status_code}")
                if status == "PASS":
                    passed += 1
                else:
                    failed += 1
                    print(f"       {r.text[:200]}")
            except Exception as e:
                print(f"[FAIL] {method} {path} → {e}")
                failed += 1

    print(f"\n{passed} passed / {failed} failed")


if __name__ == "__main__":
    run()
