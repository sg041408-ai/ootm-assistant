"""The decisions the pipeline needs. Start with the LLM; swap in fine-tuned Laya in Phase 4."""
from __future__ import annotations

import json
from typing import Protocol

from .models import CATEGORIES, Judgement, Passage, Route


class Decider(Protocol):
    def solution_seeking(self, question: str) -> float:
        """Probability the question asks for solution ideas (outside assistance)."""

    def categorize(self, question: str) -> str: ...

    def judge(self, question: str, passages: list[Passage]) -> Judgement:
        """QUOTE if a passage answers it directly, DRAFT if partly, HUMAN otherwise."""

    def draft(self, question: str, passages: list[Passage]) -> str: ...


def _format(passages: list[Passage]) -> str:
    return "\n\n".join(f"[{p.id}]\n{p.text}" for p in passages)


SYSTEM = """You help Odyssey of the Mind coaches understand the official rules.
You are NOT Odyssey of the Mind headquarters and your answers are not official clarifications.
Use only the rule passages provided. Never suggest ideas for a team's solution."""


class LLMDecider:
    def __init__(self, model: str = "claude-sonnet-5-5", client=None):
        if client is None:
            import anthropic

            client = anthropic.Anthropic()
        self.client = client
        self.model = model

    def _json(self, prompt: str) -> dict:
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=400,
            system=SYSTEM + "\nReply with a single JSON object and nothing else.",
            messages=[{"role": "user", "content": prompt}],
        )
        return json.loads(msg.content[0].text)

    def solution_seeking(self, question: str) -> float:
        out = self._json(
            "Does this question ask for ideas, designs or creative choices for the team's solution, "
            "rather than what the rules allow? "
            f'Return {{"probability": <0..1>}}.\n\nQuestion: {question}'
        )
        return float(out["probability"])

    def categorize(self, question: str) -> str:
        out = self._json(
            f"Pick one category from {CATEGORIES} for this question. "
            f'Return {{"category": "..."}}.\n\nQuestion: {question}'
        )
        return out["category"] if out.get("category") in CATEGORIES else "other"

    def judge(self, question: str, passages: list[Passage]) -> Judgement:
        out = self._json(
            "Decide how well these rule passages answer the question.\n"
            '"quote": one passage answers it directly and explicitly.\n'
            '"draft": the passages cover it partly and a careful reading answers it.\n'
            '"human": not covered, ambiguous, or needs a headquarters ruling.\n'
            'Return {"route": "quote"|"draft"|"human", "confidence": <0..1>, '
            '"passage_ids": [ids you relied on]}.\n\n'
            f"Question: {question}\n\nPassages:\n{_format(passages)}"
        )
        return Judgement(Route(out["route"]), float(out["confidence"]), list(out.get("passage_ids", [])))

    def draft(self, question: str, passages: list[Passage]) -> str:
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=600,
            system=SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Answer the coach's question in 2 to 4 sentences using only these passages. "
                        "Cite passage ids in square brackets. If the passages don't settle it, say so.\n\n"
                        f"Question: {question}\n\nPassages:\n{_format(passages)}"
                    ),
                }
            ],
        )
        return msg.content[0].text


class LayaDecider:
    """Phase 4: fine-tuned Laya checkpoints for the guard, category and judge decisions.

    Needs roughly 500 to 1,000 labeled questions from the pilot log first. Zero-shot Laya is
    close to random on typed decisions, so don't use it before fine-tuning. Drafting stays with
    the LLM because Laya scores options and never writes text.
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Fine-tune Laya on pilot data first (see docs/PLAN.md, Phase 4)")
