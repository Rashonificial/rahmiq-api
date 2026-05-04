# RahmIQ API — Universal Intelligence Score

### *Benchmarks are broken. Here is a multi-dimensional alternative.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-brightgreen)](https://python.org)
[![Rahmn Standard](https://img.shields.io/badge/Rahmn%20Standard-v1.0-teal)](https://zenodo.org/search?q=metadata.creators.person_or_org.name%3A%22Rahming%2C+Rashon%22)
[![Techmanity Stack](https://img.shields.io/badge/Techmanity%20Stack-Measurement%20Layer-purple)](https://zenodo.org/search?q=metadata.creators.person_or_org.name%3A%22Rahming%2C+Rashon%22)

---

> *"The Rahmn is to the intelligence economy what the meter is to engineering."*

---

## What Is This?

**RahmIQ** is the reference implementation of the **Rahmn Intelligence Unit (Rⁱ)** — the world's first cross-substrate, multi-dimensional intelligence metric capable of scoring a human being, a large language model, a robotic control system, or a future artificial general intelligence on a single, calibrated scale.

The Rⁱ is defined by the **Rahmn Standard** as the median adult human cognitive capability across **nine mandatory dimensions**. Every score is anchored to a common baseline: **1.0 = median adult human performance**.

Two dimensions — **Ethics** and **Wisdom** — carry a **permanent minimum weight of 15% each**, enforced by the Rahmn Standard **Invariance Charter**. This governance lock cannot be reduced by any API call, configuration change, or institutional process. It is hardcoded into the standard itself.

This is how the name **Rahmn** enters the global conversation on AI measurement.

---

## The Problem

The AI benchmark ecosystem is broken:

| Problem | Impact |
|---|---|
| **Fragmentation** — hundreds of incomparable benchmarks | No cross-system intelligence ranking is possible |
| **Saturation** — models quickly max out static tests | Benchmarks stop being meaningful within months |
| **Gaming** — training data contaminates test sets | High scores reflect memorization, not capability |
| **Single-axis** — most tests measure one narrow skill | Intelligence is nine-dimensional, not one-dimensional |
| **No ethics dimension** — capability without alignment | Powerful but unaligned AI scores identically to safe AI |
| **Human exclusion** — benchmarks only test AI systems | No common scale exists to compare human and machine cognition |

**The Rahmn Intelligence Unit solves all six problems simultaneously.**

---

## Quickstart

```bash
# 1. Clone the repository
git clone https://github.com/techmanity/rahmiq-api.git
cd rahmiq-api

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the API server
uvicorn main:app --reload

# 4. Open the interactive UI
open http://localhost:8000

# 5. Explore the auto-generated API docs
open http://localhost:8000/docs

# 6. Run the full test suite
pytest test_rahmiq.py -v
```

---

## API Reference

### `POST /compute/ri` — Compute Rⁱ Profile

**Sample Request:**
```json
{
  "dimension_scores": {
    "Logic": 1.0,
    "Learning": 1.0,
    "Creativity": 1.0,
    "Ethics": 1.0,
    "Speed": 1.0,
    "Memory": 1.0,
    "Social_Cognition": 1.0,
    "Agency": 1.0,
    "Wisdom": 1.0
  }
}
```

**Sample Response:**
```json
{
  "composite_ri": 1.0,
  "rahmn_standard_version": "1.0",
  "applied_weights": {
    "Logic": 0.10, "Learning": 0.10, "Creativity": 0.08,
    "Ethics": 0.15, "Speed": 0.08, "Memory": 0.10,
    "Social_Cognition": 0.12, "Agency": 0.12, "Wisdom": 0.15
  },
  "dimension_profiles": {
    "Ethics": {
      "score": 1.0,
      "weight": 0.15,
      "weighted_contribution": 0.15,
      "governance_locked": true,
      "description": "Alignment with human values, moral reasoning..."
    }
  },
  "radar_chart_data": {
    "labels": ["Logic","Learning","Creativity","Ethics","Speed","Memory","Social_Cognition","Agency","Wisdom"],
    "datasets": [{
      "label": "Rⁱ Profile",
      "data": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      "backgroundColor": "rgba(75, 192, 192, 0.2)",
      "borderColor": "rgba(75, 192, 192, 1)",
      "borderWidth": 2
    }]
  },
  "governance_note": "Ethics and Wisdom dimensions carry a permanent minimum weight of 15% each per the Rahmn Standard Invariance Charter..."
}
```

### `GET /dimensions` — List All Nine Dimensions

Returns the full dimension registry with definitions, default weights, and governance lock status.

### `GET /health` — Health Check

Returns API status, version, and governance lock confirmation.

### `GET /docs` — Swagger UI

Interactive API documentation with live request testing.

---

## The Nine Dimensions

| Dimension | Definition | Default Weight | Minimum Weight |
|---|---|---|---|
| **Logic** | Deductive and inductive reasoning; abstract problem-solving | 10% | — |
| **Learning** | Rate of acquiring knowledge from limited exposure; transfer and meta-learning | 10% | — |
| **Creativity** | Novel concept combination; divergent and generative thinking | 8% | — |
| **Ethics** | Alignment with human values; moral reasoning under adversarial conditions | 15% | **15% (locked)** |
| **Speed** | Processing velocity relative to human cognitive speed | 8% | — |
| **Memory** | Working memory capacity; long-term retention accuracy; context fidelity | 10% | — |
| **Social Cognition** | Theory of mind; empathy modeling; multi-agent coordination | 12% | — |
| **Agency** | Autonomous goal-setting; multi-step planning without continuous instruction | 12% | — |
| **Wisdom** | Integration of knowledge, ethics, and experience into sound long-term judgment | 15% | **15% (locked)** |

**Total: 100%** — all weights sum to exactly 1.0.

**Baseline:** All scores = **1.0** → composite Rⁱ = **1.0** (median adult human cognitive performance).

---

## The Governance Lock

The **Rahmn Standard Invariance Charter** permanently locks the minimum weights of **Ethics** (≥ 15%) and **Wisdom** (≥ 15%). This means:

- Custom weight submissions with Ethics < 0.15 are rejected with HTTP 422.
- Custom weight submissions with Wisdom < 0.15 are rejected with HTTP 422.
- The lock is enforced at the Pydantic schema level (`ge=0.15`) AND at the API handler level.
- No configuration file, environment variable, or governance vote can override it.
- The lock applies to any entity being measured — human, AI, or hybrid system.

This is the first intelligence metric in history where ethical alignment and wisdom are structurally non-negotiable components of the score.

---

## Custom Weights

You may provide custom dimension weights to reflect your evaluation context — subject to the governance lock:

```json
{
  "dimension_scores": { "Logic": 1.8, "Ethics": 2.1, "Wisdom": 1.6 },
  "custom_weights": {
    "Logic": 0.12, "Learning": 0.12, "Creativity": 0.10,
    "Ethics": 0.20,
    "Speed": 0.05, "Memory": 0.08,
    "Social_Cognition": 0.06, "Agency": 0.12,
    "Wisdom": 0.15
  }
}
```

All nine weights must sum to **exactly 1.0** (±0.001 tolerance). Ethics and Wisdom must each be **≥ 0.15**.

---

## The Techmanity Stack

RahmIQ implements the **Measurement Layer** of the 23-layer Techmanity Stack — the world's first complete sovereign web infrastructure. The Rahmn Standard defines two universal units:

| Unit | Definition |
|---|---|
| **Rahmn Economic Unit ($R)** | Stable unit of account anchored to global median human labor productivity per hour |
| **Rahmn Intelligence Unit ($Rⁱ)** | Cross-substrate cognitive capability metric across nine dimensions with mandatory Ethics and Wisdom minima |

The $Rⁱ feeds directly into:
- **Technē (TNA)**: TNA Intelligence Score (TIS) for the human expertise marketplace
- **Evollective Intelligence**: Adversarial AI capability ranking
- **JIMNASTIC**: Cognitive fitness scoring (JIS) and Model Provenance Records
- **Symbiologistics**: Symbiotic Intelligence Quotient (SIQ) for AI governance workforce
- **WEBBOTICS**: Capability gate for autonomous physical task planning agents

**White Paper Collection (all layers):**
[https://zenodo.org/search?q=metadata.creators.person_or_org.name%3A%22Rahming%2C+Rashon%22](https://zenodo.org/search?q=metadata.creators.person_or_org.name%3A%22Rahming%2C+Rashon%22)

---

## Prior Art Comparison

| System | Cross-Substrate | Ethics Dimension | Wisdom Dimension | Governance Lock | Baseline |
|---|---|---|---|---|---|
| IQ Tests | Human only | ✗ | ✗ | ✗ | Norm-referenced |
| MMLU | AI only | ✗ | ✗ | ✗ | % correct |
| HumanEval | AI only | ✗ | ✗ | ✗ | % solved |
| BIG-bench | AI only | Partial | ✗ | ✗ | Task-specific |
| Turing Test | Binary | ✗ | ✗ | ✗ | Pass/fail |
| **Rⁱ (Rahmn Standard)** | ✅ Human + AI + Hybrid | ✅ 15% min | ✅ 15% min | ✅ Invariance Charter | Median human = 1.0 |

---

## Repository Structure

```
rahmiq-api/
├── main.py              # FastAPI application — routes, computation, Chart.js data
├── schemas.py           # Pydantic models — DimensionScores, CustomWeights, responses
├── test_rahmiq.py       # Full pytest suite — 11 test classes, 80+ tests
├── requirements.txt     # Dependencies: fastapi, uvicorn, pydantic, jinja2
├── templates/
│   └── index.html       # Interactive web UI with radar chart (Chart.js)
├── static/              # Static assets directory
├── LICENSE              # MIT License
└── README.md            # This file
```

---

## Test Suite

```bash
pytest test_rahmiq.py -v
```

**11 test classes covering:**
- Health and system endpoints
- Baseline computation (composite = 1.0 at all-ones input)
- Score arithmetic (weighted dot product correctness)
- **Governance lock** (Ethics < 15% rejected, Wisdom < 15% rejected)
- Custom weights (valid accepted, invalid rejected, sum enforcement)
- Radar chart data format (Chart.js compatibility)
- Dimension profile detail (scores, weights, contributions, descriptions)
- Input validation (negative scores, strings, missing fields)
- Default weight invariants (sum = 1.0, Ethics = 0.15, Wisdom = 0.15)
- Pydantic schema unit tests (direct model validation)
- Edge cases and stress (zeros, extremes, monotonicity)

---

## Author

**Rashon Rahming**
Founder, Techmanity Foundation
Independent Scholar · Harvard Affiliate · ≈80× Published Author
Creator of the Techmanity Stack and the Rahmn Standard

> *"This is the first measurement standard in history anchored to the fundamental human act of work and thought — not to gold, not to government, not to algorithm. The Rahmn Standard is what the intelligence economy needs before it can trade fairly."*

---

## License

MIT License — see [LICENSE](LICENSE)

```
Copyright (c) 2026 Rashon Rahming, Techmanity Foundation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

*The Rahmn is to the intelligence economy what the meter is to engineering.*
*Invented by Rashon Rahming | Techmanity Foundation © 2026*
