# Technology Stack: Geo-Expansion Viability Judge

## 1. Core Runtime & Host Environment
- **Target Host:** Codex Desktop App (Jury Execution Environment).
- **Core Runtimes:** Python 3 (standard library: `urllib.request`, `json`, `math`, `datetime`, `re`) & Node.js 24.
- **Zero-Dependency Mandate:** No pip installs or external npm packages required during the 60s cold-run window.
- **Version Control:** Git.

## 2. Skill Architecture & Components
- **Entry Skill Definition:** `.agents/skills/geo-expansion-judge/SKILL.md`
  - Canonical agent skill with YAML frontmatter (`name: geo-expansion-judge`, `description`).
  - Imperative validation, data ingestion, economic analysis, compliance checks, and brief generation.
- **Reference & Data Models:**
  - Input: `demo/input/expansion_request.json`
  - Output: `demo/output/expansion_brief.md`
  - Country Market / Regulatory Baselines (e.g. EU/UK/DE/JP tariffs, VAT, LUCID/EPR rules).
- **Evaluation & Verification Engine:**
  - `demo/evals.md`: 3 test scenarios (Intended run, Insufficient evidence, Exclusion/Failure case).
  - `demo/seed-prompt.md`: Exact prompt for jury execution.

## 3. Tooling & Linting
- **Validation:** Python `unittest` / standard script assertions for calculation rules.
- **Style:** Markdownlint standards, PEP 8 for Python helper scripts.
