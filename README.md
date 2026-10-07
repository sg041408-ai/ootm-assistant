# OotM Clarification Assistant

An unofficial helper for Odyssey of the Mind coaches. Ask a rules question and it either quotes
the rule that answers it, drafts a cited answer labeled unofficial, or tells you it needs an
official clarification and shows the closest rules to reference. It refuses questions that ask
for solution ideas, since that would be outside assistance.

It is not affiliated with Odyssey of the Mind, and its answers are not official clarifications.

## How it works

```
question -> outside-assistance guard -> rule search (top 5) -> judge -> quote | draft | human
                                                     category tag + urgency from tournament date
```

The guard, category and judge decisions run on an LLM today. Once the pilot has produced
500 to 1,000 labeled questions, they can move to a fine-tuned [Laya](https://pypi.org/project/laya/)
model. See [docs/PLAN.md](docs/PLAN.md).

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[llm,dev]"
pytest

# add licensed source files to data/raw/ first (see data/README.md)
export ANTHROPIC_API_KEY=...
ootm-ask "Does the cost limit include the driver's costume?" --tournament 2027-03-14
```

## Layout

| Path | What it does |
| --- | --- |
| `src/ootm_assistant/corpus.py` | Splits sources into passages cited by heading path |
| `src/ootm_assistant/retrieve.py` | BM25 keyword search (Phase 1 adds embeddings) |
| `src/ootm_assistant/deciders.py` | Guard, category, judge and draft decisions (LLM now, Laya later) |
| `src/ootm_assistant/pipeline.py` | Routes each question to quote, draft, human or refuse |
| `src/ootm_assistant/urgency.py` | Urgency from days until the team's tournament |
