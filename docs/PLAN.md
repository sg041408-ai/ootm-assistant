# Plan

Full write-up with feedback and the design diagram:
https://claude.ai/code/artifact/d98aa520-8639-4df3-a3c3-0e399d7c02a6

Build LLM-first, log every question, and bring in Laya once there's labeled data.

- [ ] **Phase 0, permission and data.** Written OK from OotM HQ or the state association to index
      this season's problems and Program Guide. Ask for past General Clarifications and an
      anonymized set of past team questions with answers.
- [ ] **Phase 1, rule search.** Passages tagged by source, section and season; hybrid search
      (keyword plus embeddings, Postgres + pgvector). Target: the right passage is in the top 5
      for 50 hand-written test questions.
- [ ] **Phase 2, answer pipeline.** Guard, retrieve, judge (quote / draft / human) with required
      citations. Drafts are labeled unofficial; "human" helps the coach write an official
      clarification. Urgency from the tournament date. (Skeleton in `src/` today.)
- [ ] **Phase 3, pilot.** 10 to 20 coaches. Log question, route, and the coach's thumbs-up or
      correction. That log is the training set.
- [ ] **Phase 4, Laya.** With 500 to 1,000 labeled questions, fine-tune Laya for the guard,
      category, and judge. Keep it only if it matches the LLM on a held-out set. Replace the
      placeholder 0.85 with the cutoff where drafted answers are right at least 95% of the time.
- [ ] **Phase 5, season operations.** Re-index on every new General Clarification; reset
      problem data when new problems are released.
