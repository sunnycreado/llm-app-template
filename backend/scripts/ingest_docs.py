"""
Usage: python backend/scripts/ingest_docs.py --path ./docs/
"""
import argparse
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.ingestion import ingest_file


async def main(folder: Path):
    files = list(folder.glob("**/*.txt")) + list(folder.glob("**/*.md"))
    if not files:
        print(f"No .txt or .md files found in {folder}")
        return
    for file in files:
        await ingest_file(file)
    print(f"\nDone. Ingested {len(files)} file(s).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=Path("./docs"))
    args = parser.parse_args()
    asyncio.run(main(args.path))
