"""Keyword (BM25) search over passages. Swap in hybrid search (pgvector) in Phase 1."""
from __future__ import annotations

import math
import re
from collections import Counter

from .models import Passage

TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


class BM25Index:
    def __init__(self, passages: list[Passage], k1: float = 1.5, b: float = 0.75):
        self.passages = passages
        self.k1, self.b = k1, b
        self.docs = [Counter(tokenize(p.text + " " + p.id)) for p in passages]
        self.lengths = [sum(d.values()) for d in self.docs]
        self.avg_len = sum(self.lengths) / len(self.lengths) if passages else 0.0
        df: Counter[str] = Counter()
        for d in self.docs:
            df.update(d.keys())
        n = len(passages)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def search(self, query: str, k: int = 5) -> list[Passage]:
        terms = tokenize(query)
        scored = []
        for i, doc in enumerate(self.docs):
            score = 0.0
            for t in terms:
                tf = doc.get(t, 0)
                if tf:
                    norm = 1 - self.b + self.b * self.lengths[i] / self.avg_len
                    score += self.idf[t] * tf * (self.k1 + 1) / (tf + self.k1 * norm)
            if score > 0:
                scored.append((score, i))
        scored.sort(reverse=True)
        return [self.passages[i] for _, i in scored[:k]]
