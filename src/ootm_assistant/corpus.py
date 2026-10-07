"""Split source documents into citable passages."""
from __future__ import annotations

import re
from pathlib import Path

from .models import Passage

HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


def split_markdown(source: str, text: str) -> list[Passage]:
    """One passage per paragraph, cited by its heading path and paragraph number."""
    passages: list[Passage] = []
    headings: list[str] = []
    para: list[str] = []
    counter = 0

    def flush() -> None:
        nonlocal counter
        body = " ".join(line.strip() for line in para).strip()
        para.clear()
        if not body:
            return
        counter += 1
        path = " > ".join([source, *headings, str(counter)])
        passages.append(Passage(id=path, source=source, text=body))

    for line in text.splitlines():
        m = HEADING.match(line)
        if m:
            flush()
            level = len(m.group(1))
            headings[:] = headings[: level - 1] + [m.group(2).strip()]
            counter = 0
        elif not line.strip():
            flush()
        else:
            para.append(line)
    flush()
    return passages


def load_corpus(directory: Path) -> list[Passage]:
    passages: list[Passage] = []
    for path in sorted(directory.glob("*")):
        if path.suffix in {".md", ".txt"}:
            passages += split_markdown(path.stem, path.read_text(encoding="utf-8"))
    return passages
