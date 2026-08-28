# Expansion Viability Decision Brief: Carpathian Craft Coffee Lab

**Product:** Carpathian Artisan Ceramic Pour-Over Coffee Kit  
**Expansion Corridor:** `RO` (Romania) -> `BR` (Brazil)  
**Evaluation Timestamp:** 2026-08-28 19:10:28 UTC  
**Execution Engine:** `$geo-expansion-judge` (Codex Native Runtime)

---

## 1. Executive Summary & Verdict

**`[ NO_GO ]`** — **Viability Score: 30/100** (Confidence: **HIGH (Kill Trigger Active)**)

**Executive Rationale:** Expansion aborted due to critical risk: Landed gross margin (-33.8%) is below the minimum viable 20.0% threshold.

| Evaluation Dimension | Weight | Pillar Score | Status |
| :--- | :---: | :---: | :--- |
| **Unit Economics & Margin Cushion** | 40% | **0/100** | 🔴 Risk Alert |
| **Regulatory & Cross-Border Compliance** | 35% | **95/100** | 🟢 Clear Pathway |
| **Apify Community Sentiment & Demand Pulse** | 25% | **0/100** | 🟡 Moderate Pulse |

> [!CAUTION]
> **CRITICAL KILL TRIGGER ACTIVATED**
> • Landed gross margin (-33.8%) is below the minimum viable 20.0% threshold.<br>• Severe consumer sentiment hostility detected in target community (68.0% negative reactions).


---

## 2. Unit Economics & Price Benchmark Breakdown

| Parameter | Value (EUR) | Notes / Percentage of MSRP |
| :--- | :---: | :--- |
| **Target Retail MSRP (Gross)** | **€69.00** | Destination price paid by Brazil consumers |
| Destination VAT (3306% Brazil VAT/Import Tax) | -€33.06 | 19% via EU One-Stop Shop (OSS) |
| **Net Realized Revenue** | **€35.94** | Revenue net of destination sales tax |
| Unit Manufacturing COGS | -€14.50 | Ex-factory production cost (Romania) |
| Intra-EU Tracked Freight (DPD/DHL) | -€42.50 | Standard parcel rate (<1kg RO -> DE) |
| Export Packaging & Cushioning | -€2.10 | High-durability kraft & cellulose |
| VerpackG (LUCID) Packaging Fee | -€0.15 | Brazil packaging compliance per-unit licensing |
| **Total Landed Cost** | **€92.31** | Total landed cost burden |
| **Net Gross Profit** | **€-23.31** | **Landed Margin: -33.8%** |

### Local Competitive Positioning
- **Brazil Competitor Median Price:** **€38.50**
- **Price Index vs. Local Market:** **179.0%** of competitor median (Priced at a competitive ~€3.50 discount to market median).

---

## 3. Regulatory & Import Compliance Matrix

### Mandatory Compliance Frameworks:
- **PNRS (National Solid Waste Policy)** (SINIR / IBAMA): [Official Documentation](https://sinir.gov.br/)
- **ANVISA RDC 88/2016 & INMETRO Portaria 398/2021** (BfR (Federal Institute for Risk Assessment)): [Official Documentation](https://www.gov.br/anvisa/pt-br)

### Action Checklist Before First Dispatch:
- [ ] **Register with SINIR / IBAMA**: Mandatory registration under PNRS (National Solid Waste Policy) before shipping physical packages to BR. *(Est. cost: €120.00)* — [Reference](https://sinir.gov.br/)


---

## 4. Apify Real-World Market Pulse & Community Signals

*Extracted via Apify Reddit Fast Scraper (`trudax/reddit-scraper-lite`) from `r/Coffee`, `r/espresso`, `r/germany`.*

- **Total Signals Analyzed:** 222 community posts and comments
- **Community Sentiment Ratio:** **18.0% Positive** (Net Score: +-50.0)
- **Willingness to Pay Anchor:** Median **€40.00** (Target price of €69.00 falls within willingness to pay band).

### Key Purchase Drivers:
- Local domestic roasters support

### Critical Market Friction Points & Recommendations:
- Taxa das blusinhas / 60% import tax renders international purchases prohibitive
- Curitiba customs clearance takes 3-6 weeks with frequent package seizures
- Refusal to buy without local Pix / Boleto Bancario payments
- **Required Localization:** Provide Brazil localized user manual and integrate PayPal/Klarna on checkout.

---

## 5. Decision Rules & Kill Triggers

| Rule / Trigger | Threshold | Observed Status | Triggered? |
| :--- | :--- | :--- | :---: |
| **Minimum Landed Gross Margin** | Margin >= 20.0% | **-33.8%** | No |
| **Material Safety & FCM Certification** | No toxic/lead materials; DoC available | **Compliant** (Ceramic + Borosilicate) | No |
| **Negative Sentiment Spike** | Negative discussions < 60% | **68.0%** | No |
| **Overall Recommendation** | Viability Score >= 75 | **30/100** | **APPROVED (GO)** |

---

## 6. Citations & Grounded Evidentiary Trail

| Source | Target Entity / Law | URL | Retrieval Date |
| :--- | :--- | :--- | :--- |
| Competitor Price Benchmark | Hario V60 Ceramic 02 (Mercado Livre Brasil) | https://www.mercadolivre.com.br/hario-v60 | 2026-08-28 |
| Competitor Price Benchmark | Pressca Cafeteira Portatil Brasil | https://www.pressca.com.br/ | 2026-08-28 |
| Regulatory / Market Authority | Receita Federal do Brasil - Programa Remessa Conforme | https://www.gov.br/receitafederal/pt-br/assuntos/aduana-e-comercio-exterior/importacao/remessa-conforme | 2026-08-28 |
| Regulatory / Market Authority | INMETRO Kitchenware and Ceramic Testing Standards | http://www.inmetro.gov.br/legislacao/rtac/pdf/RTAC002773.pdf | 2026-08-28 |
| Apify Reddit Fast Scraper | Subreddit sentiment (trudax/reddit-scraper-lite) |  | 2026-08-28T18:00:00Z |

