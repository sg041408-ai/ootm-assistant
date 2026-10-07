from datetime import date

from ootm_assistant.corpus import split_markdown
from ootm_assistant.models import Judgement, Route, Urgency
from ootm_assistant.pipeline import Assistant
from ootm_assistant.retrieve import BM25Index
from ootm_assistant.urgency import urgency_for

# Made-up sample text for tests, not real problem wording.
SAMPLE = """# Sample Problem
## Limitations
The team must build a vehicle that carries a driver.

The cost limit for the solution is $145 USD.

## Scoring
The vehicle completing the course scores 1 to 20 points.
"""


def passages():
    return split_markdown("sample", SAMPLE)


def test_split_cites_heading_path():
    ids = [p.id for p in passages()]
    assert ids == [
        "sample > Sample Problem > Limitations > 1",
        "sample > Sample Problem > Limitations > 2",
        "sample > Sample Problem > Scoring > 1",
    ]


def test_search_finds_cost_limit():
    hits = BM25Index(passages()).search("what is the cost limit?", k=1)
    assert hits[0].id.endswith("Limitations > 2")


def test_urgency_from_calendar():
    today = date(2027, 2, 1)
    assert urgency_for(date(2027, 2, 5), today) is Urgency.IMMEDIATE
    assert urgency_for(date(2027, 2, 15), today) is Urgency.WITHIN_48H
    assert urgency_for(date(2027, 4, 1), today) is Urgency.LATER
    assert urgency_for(None, today) is Urgency.LATER


class FakeDecider:
    def __init__(self, p_solution=0.0, judgement=None):
        self.p_solution = p_solution
        self.judgement = judgement

    def solution_seeking(self, q):
        return self.p_solution

    def categorize(self, q):
        return "long-term problem"

    def judge(self, q, ps):
        return self.judgement

    def draft(self, q, ps):
        return "Drafted answer [x]."


def assistant(**kw):
    return Assistant(BM25Index(passages()), FakeDecider(**kw))


def test_refuses_solution_ideas():
    a = assistant(p_solution=0.9).ask("what should our vehicle look like?")
    assert a.route is Route.REFUSE


def test_quotes_rule_verbatim():
    pid = "sample > Sample Problem > Limitations > 2"
    a = assistant(judgement=Judgement(Route.QUOTE, 0.95, [pid])).ask("cost limit?")
    assert a.route is Route.QUOTE
    assert "$145 USD" in a.text and pid in a.text


def test_drafts_when_confident():
    a = assistant(judgement=Judgement(Route.DRAFT, 0.9, [])).ask("can the driver push?")
    assert a.route is Route.DRAFT and "unofficial" in a.text


def test_routes_low_confidence_to_human():
    a = assistant(judgement=Judgement(Route.DRAFT, 0.6, [])).ask("can the vehicle fly?")
    assert a.route is Route.HUMAN
