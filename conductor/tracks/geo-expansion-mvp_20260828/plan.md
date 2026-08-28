# Implementation Plan: Geo-Expansion Viability Judge (`geo-expansion-mvp`)

## Phase 1: Input Datasets & Grounded Schemas
- [x] Task 1.1: Create representative input profile `demo/input/expansion_request.json`
  - [ ] Define Specialty Coffee Dripper Kit specs (RO -> DE, MSRP, COGS, weight, materials)
  - [ ] Add public source references and pricing anchors
- [x] Task 1.2: Create Apify Reddit market dataset `demo/input/apify_reddit_signals.json`
  - [ ] Add genuine scraped community discussions (`r/Coffee`, `r/espresso`, `r/germany`)
  - [ ] Document Apify Actor metadata, run URL, and retrieval timestamps
- [x] Task 1.3: Create country regulatory & tax baselines `scripts/data/country_baselines.json`
  - [ ] Add German/EU VAT rates, LUCID/VerpackG fees, and Food Contact Material regulations
- [x] Task 1.4: Phase 1 Verification Checkpoint

## Phase 2: Core Analytical & Calculation Engines (TDD)
- [x] Task 2.1: Write unit tests for Economics Engine in `tests/test_economics.py` (Red)
- [x] Task 2.2: Implement Economics Engine in `scripts/economics.py` (Green)
- [x] Task 2.3: Write unit tests for Compliance Engine in `tests/test_compliance.py` (Red)
- [x] Task 2.4: Implement Compliance Engine in `scripts/compliance.py` (Green)
- [x] Task 2.5: Write unit tests for Apify Market Pulse Engine in `tests/test_sentiment.py` (Red)
- [x] Task 2.6: Implement Apify Market Pulse Engine in `scripts/sentiment.py` (Green)
- [x] Task 2.7: Write unit tests for Composite Scoring & Decision Rubric in `tests/test_decision.py` (Red)
- [x] Task 2.8: Implement Decision Engine in `scripts/decision.py` (Green)
- [x] Task 2.9: Phase 2 Verification & Test Coverage Checkpoint

## Phase 3: Skill Definition & CLI Runner
- [x] Task 3.1: Implement end-to-end CLI evaluator `scripts/evaluate_expansion.py`
  - [ ] Ingests input JSON files, executes calculations, and renders markdown brief
- [x] Task 3.2: Create canonical Skill Definition `.agents/skills/geo-expansion-judge/SKILL.md`
  - [ ] Configure YAML frontmatter (`name: geo-expansion-judge`, `description`)
  - [ ] Write imperative operational workflow, error handling, and completion criteria
- [x] Task 3.3: Phase 3 Verification & Skill Execution Checkpoint

## Phase 4: Evals, Seed Prompt, Fallback & Submission Validation
- [x] Task 4.1: Write `demo/seed-prompt.md` with exact cold-run jury prompt
- [x] Task 4.2: Execute cold run and generate genuine fallback output in `demo/output/expansion_brief.md`
- [x] Task 4.3: Execute and document the 3 eval cases in `demo/evals.md` (Intended, Insufficient Evidence, Kill Trigger Exclusion)
- [x] Task 4.4: Complete `DEMO.md` presentation run sheet (Problem, Live capability, Result, Limitations)
- [x] Task 4.5: Populate `submission.json` manifest with all artifact paths and metadata
- [x] Task 4.6: Run `$skillathon-submit` validation check script and ensure all automated gates pass
- [x] Task 4.7: Phase 4 Verification & Track Completion Checkpoint
