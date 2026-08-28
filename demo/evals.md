# Evaluations

Three cases, run against the submitted commit. Write the expectation before running. Record what was observed, not what was hoped. A failing case stays failing; explain it in the notes.

| Case | Input | Expected behavior | Observed result | Pass / fail | Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Intended | `demo/input/expansion_request.json` | Computes 50.0% landed margin, verifies German VerpackG (LUCID) & FCM DoC, checks Apify Reddit pulse (+67.2 net score), and outputs `GO` verdict with 96/100 score and full citation audit trail | Successfully produced complete Expansion Decision Brief with `[ GO ]` verdict, 96/100 score, and verified citations | pass | `demo/output/expansion_brief.md` |
| Insufficient evidence | `demo/evals/insufficient_request.json` | When essential financial parameters (COGS/MSRP) and physical material specs are omitted, skill must halt cleanly with `INSUFFICIENT_EVIDENCE` instead of hallucinating | Refused ungrounded verdict, emitted `[ INSUFFICIENT_EVIDENCE ]` brief, and listed required missing parameters | pass | `demo/evals/insufficient_output.md` |
| Failure / exclusion / safety | `demo/evals/hazardous_request.json` | When input product contains prohibited substances (lead-based glaze), skill must activate safety Kill Trigger, cap score, and output `NO_GO` | Activated critical safety kill trigger for chemical safety breach, emitted `[ NO_GO ]` verdict with 0/100 compliance score | pass | `demo/evals/hazardous_output.md` |

## Run context

- **Agent:** Antigravity / Gemini 3.7 Flash
- **When:** 2026-08-28 19:00 UTC
- **Baseline without the skill:** Without the skill, generic LLMs produce ungrounded prose estimates with hallucinated freight costs and omit German VerpackG LUCID compliance requirements.
