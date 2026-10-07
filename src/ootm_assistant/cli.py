from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from .corpus import load_corpus
from .deciders import LLMDecider
from .pipeline import Assistant
from .retrieve import BM25Index


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the OotM clarification assistant")
    parser.add_argument("question")
    parser.add_argument("--data", type=Path, default=Path("data/raw"))
    parser.add_argument("--tournament", type=date.fromisoformat, help="YYYY-MM-DD")
    args = parser.parse_args()

    passages = load_corpus(args.data)
    if not passages:
        parser.error(f"No .md or .txt sources in {args.data} (see data/README.md)")
    answer = Assistant(BM25Index(passages), LLMDecider()).ask(args.question, args.tournament)
    print(f"[{answer.route.value} | {answer.category} | urgency {answer.urgency.value} | "
          f"confidence {answer.confidence:.2f}]\n")
    print(answer.text)
    for p in answer.citations:
        print(f"  - {p.id}")


if __name__ == "__main__":
    main()
