from __future__ import annotations

from datetime import date

from .deciders import Decider
from .models import Answer, Route
from .retrieve import BM25Index
from .urgency import urgency_for

DISCLAIMER = (
    "This is unofficial guidance, not an Odyssey of the Mind clarification. "
    "For a ruling you can rely on at a tournament, submit an official clarification "
    "through the membership portal."
)
REFUSAL = (
    "I can't help with ideas for your team's solution. Under the outside assistance rule, "
    "the solution has to come from the team. I can help with what the rules allow."
)
HUMAN = (
    "The rules don't settle this clearly, so it needs an official clarification. "
    "Here are the closest passages to reference when you submit it."
)


class Assistant:
    def __init__(
        self,
        index: BM25Index,
        decider: Decider,
        guard_threshold: float = 0.5,
        quote_threshold: float = 0.85,
        draft_threshold: float = 0.85,  # placeholder: set from pilot data (Phase 4)
        top_k: int = 5,
    ):
        self.index = index
        self.decider = decider
        self.guard_threshold = guard_threshold
        self.quote_threshold = quote_threshold
        self.draft_threshold = draft_threshold
        self.top_k = top_k

    def ask(self, question: str, tournament: date | None = None, today: date | None = None) -> Answer:
        urgency = urgency_for(tournament, today or date.today())
        category = self.decider.categorize(question)

        p_solution = self.decider.solution_seeking(question)
        if p_solution >= self.guard_threshold:
            return Answer(Route.REFUSE, REFUSAL, category, urgency, p_solution)

        passages = self.index.search(question, k=self.top_k)
        if not passages:
            return Answer(Route.HUMAN, HUMAN, category, urgency, 0.0)

        j = self.decider.judge(question, passages)
        by_id = {p.id: p for p in passages}
        cited = [by_id[i] for i in j.passage_ids if i in by_id]

        if j.route is Route.QUOTE and j.confidence >= self.quote_threshold and cited:
            quote = cited[0]
            text = f'"{quote.text}"\n\n({quote.id})\n\n{DISCLAIMER}'
            return Answer(Route.QUOTE, text, category, urgency, j.confidence, [quote])

        if j.route in (Route.QUOTE, Route.DRAFT) and j.confidence >= self.draft_threshold:
            text = self.decider.draft(question, cited or passages) + "\n\n" + DISCLAIMER
            return Answer(Route.DRAFT, text, category, urgency, j.confidence, cited or passages)

        return Answer(Route.HUMAN, HUMAN, category, urgency, j.confidence, cited or passages)
