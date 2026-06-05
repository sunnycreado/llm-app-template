# Prompt Versioning

Prompts are plain text files — never Python strings. This makes them:
- Readable by non-engineers (PMs, domain experts)
- Diffable in git like any other file
- Versioned independently from code

---

## Structure

```
backend/app/prompts/
├── CHANGELOG.md          ← log every version change + eval score
└── base/                 ← default prompt version
    ├── system.txt        ← the system prompt
    ├── few_shot.json     ← few-shot examples (can be empty array)
    └── meta.json         ← version metadata
```

---

## Creating a new version

**Never edit an existing version. Always create a new folder.**

```bash
cp -r backend/app/prompts/base backend/app/prompts/v2
```

Edit `v2/system.txt` and `v2/few_shot.json`.

Update `v2/meta.json`:
```json
{
  "version": "v2",
  "model": "meta/llama-3.1-8b-instruct",
  "eval_score": null,
  "notes": "Added stricter null discipline rule.",
  "created": "2026-06-05"
}
```

Switch to the new version in `.env`:
```env
PROMPT_VERSION=v2
```

Run evals and record the score:
```bash
make eval
```

Add an entry to `CHANGELOG.md`:
```md
## v2 — 2026-06-05
- Added stricter null discipline rule
- eval_score: 0.91
- model: meta/llama-3.1-8b-instruct
```

---

## few_shot.json format

```json
[
  {
    "role": "user",
    "content": "Example user message"
  },
  {
    "role": "assistant",
    "content": "Example ideal response"
  }
]
```

Each user/assistant pair is one example. Add as many as needed.
The LLM sees these before the real conversation starts.

---

## Loading in code

```python
from app.prompts.registry import load, build_messages

# Load prompt data
prompt = load(name="base", version="latest")
print(prompt["system"])     # system prompt string
print(prompt["few_shot"])   # list of message dicts
print(prompt["meta"])       # metadata dict

# Build full messages array for NIM
messages = build_messages(name="base", version="v2", user_text="Hello")
```

---

## Rules

1. Never edit an existing version folder
2. Always create a new version
3. Always run `make eval` before promoting to production
4. Record eval score in `meta.json` and `CHANGELOG.md`
5. `PROMPT_VERSION=latest` always resolves to the `base/` folder
