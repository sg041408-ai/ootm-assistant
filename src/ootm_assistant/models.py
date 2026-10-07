from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Route(str, Enum):
    REFUSE = "refuse"  # asks for solution ideas (outside assistance)
    QUOTE = "quote"  # a retrieved rule answers it directly
    DRAFT = "draft"  # partially covered; LLM drafts an unofficial answer
    HUMAN = "human"  # not covered or low confidence; help write an official clarification


class Urgency(str, Enum):
    IMMEDIATE = "immediate"
    WITHIN_48H = "48h"
    LATER = "later"


CATEGORIES = [
    "logistics",
    "long-term problem",
    "spontaneous",
    "style",
    "membership",
    "other",
]


@dataclass(frozen=True)
class Passage:
    id: str  # citation, e.g. "2026-27_problem-1 > Limitations > 3"
    source: str
    text: str


@dataclass
class Judgement:
    route: Route  # QUOTE, DRAFT or HUMAN
    confidence: float
    passage_ids: list[str] = field(default_factory=list)


@dataclass
class Answer:
    route: Route
    text: str
    category: str
    urgency: Urgency
    confidence: float
    citations: list[Passage] = field(default_factory=list)
