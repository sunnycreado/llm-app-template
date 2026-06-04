# Prompt Versioning

## How it works

Each prompt version is a folder under `backend/app/prompts/`:

```
prompts/
└── base/
    ├── system.txt       ← the system prompt
    ├── few_shot.json    ← few-shot examples array
    └── meta.json        ← version metadata + eval score
```

## Adding a version

1. Copy `base/` → `v2/`
2. Edit `system.txt` and `few_shot.json`
3. Update `meta.json`
4. Set `PROMPT_VERSION=v2` in `.env`
5. Run `make eval` → record score in `CHANGELOG.md`

## Loading in code

```python
from app.prompts.registry import build_messages

messages = build_messages(name="base", version="latest", user_text="Hello")
```

## Rules

- Never edit an existing version folder
- Always create a new version
- Always run evals before promoting a version to production
- Record the eval score in `meta.json` and `CHANGELOG.md`
