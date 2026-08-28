# Product Definition: Geo-Expansion Viability Judge (`geo-expansion-judge`)

## Initial Concept
A specialized Go-To-Market (GTM) Agent Skill built for the GTM Skillathon that solves a real go-to-market problem with verifiable real-world web data, executes cleanly in Codex, and provides concrete evidence and fallback paths.

## Vision & Purpose
Empower physical e-commerce brand founders and growth leads to make data-backed, de-risked decisions on whether to expand their physical product line into new geographic markets. It delivers a fast, transparent, and evidence-grounded Go/Caution/No-Go verdict in under 60 seconds without requiring external paid APIs or private credentials.

## Target User & Persona
- **Role:** D2C E-commerce Founder, VP of Growth, or Head of International Expansion selling physical consumer products (e.g. specialty beverage/coffee, ergonomic hardware, premium apparel, wellness/cosmetics).
- **Core Pain Point:** Expanding cross-border blindly leads to trapped inventory, unexpected import duties/compliance fines (e.g., EU Packaging Acts, CE marks, local VAT), and poor margins against entrenched domestic competitors.

## Scope Sentence
> "Given an e-commerce physical product profile and target country (`expansion_request.json`), `$geo-expansion-judge` produces an **Expansion Viability Decision Brief** with cited local price benchmarks, regulatory friction points, and Go/No-Go verdict while never making unverified margin claims or skipping local compliance flags."

## The 3 Core Evaluation Pillars
1. **Local Competitor & Price Ceiling Benchmark:**
   - Evaluates target market price bands and incumbent domestic alternatives.
   - Computes landed-cost margin viability (MSRP vs. local competitive median).
2. **Regulatory & Category Barriers:**
   - Detects mandatory market compliance requirements (e.g., EU EPR/LUCID packaging laws, CE/UKCA marking, food/cosmetics ingredient notifications).
   - Identifies customs/VAT threshold frictions.
3. **Consumer Resonance & Channel Fit:**
   - Maps dominant local retail/marketplace channels (e.g., Amazon DE vs. Otto vs. localized Shopify).
   - Assesses localized payment preferences and category cultural nuances.

## Input / Output Contracts
- **Input (`demo/input/expansion_request.json`):**
  - Product specs (category, retail price USD/EUR, dimensions/weight, materials/ingredients, value proposition).
  - Target Country (ISO code, e.g. DE, GB, JP, FR).
  - Current home market economics (COGS, domestic retail price).
- **Output Artifact (`Expansion Viability Decision Brief`):**
  - **Verdict:** `GO` | `CONDITIONAL_GO` | `NO_GO`
  - **Viability Index:** 0–100 score across Economics, Compliance, and Demand.
  - **Unit Economics Stress-Test:** Landed cost estimation vs. local price tolerance.
  - **Compliance Checklist & Red Flags:** Critical regulatory prerequisites before shipping.
  - **Kill Triggers:** Explicit operational thresholds that mandate halting expansion.
  - **Audit Trail:** Grounded citations with source URLs, retrieval dates, and confidence ratings.

## Boundaries & Non-Goals
- Does NOT provide formal legal/tax counsel; flags regulatory hurdles with public government references.
- Never invents competitor pricing or market shares without citations.
- Halts with `INSUFFICIENT_EVIDENCE` if essential product specifications or country data cannot be verified.
