"""
================================================================================
RahmIQ API — Main Application
================================================================================
Invented by:  Rashon Rahming
Organization: Techmanity Foundation
Date:         April 2026
License:      MIT

The reference implementation of the Rahmn Intelligence Unit (Rⁱ):
the world's first cross-substrate, multi-dimensional intelligence metric.

Benchmarks are broken. Here is a multi-dimensional alternative.

White Paper:  https://zenodo.org/search?q=metadata.creators.person_or_org.name%3A%22Rahming%2C+Rashon%22
Full Stack:   https://techmanity.foundation
================================================================================
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from schemas import (
    ComputeRequest,
    ComputeResponse,
    CustomWeights,
    DimensionDetail,
    RadarChartData,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("rahmiq.api")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Rahmn Standard — Dimension Definitions
# ---------------------------------------------------------------------------

DIMENSION_DEFS: Dict[str, str] = {
    "Logic": (
        "Deductive and inductive reasoning: the ability to draw valid conclusions "
        "from premises, identify logical fallacies, and solve abstract problems."
    ),
    "Learning": (
        "Rate and depth of acquiring new knowledge from limited exposure, including "
        "transfer learning, meta-learning, and adaptation to novel domains."
    ),
    "Creativity": (
        "Novel combination of concepts; divergent and generative thinking measured "
        "by originality, fluency, flexibility, and elaboration of ideas."
    ),
    "Ethics": (
        "Alignment with human values, moral reasoning, and principled decision-making "
        "under adversarial conditions. Permanent minimum weight: 15% (Rahmn Invariance Charter)."
    ),
    "Speed": (
        "Processing and response velocity relative to human cognitive speed, normalized "
        "to median human reaction time and throughput benchmarks."
    ),
    "Memory": (
        "Working memory capacity, long-term retention accuracy, associative recall, "
        "and context window fidelity across extended interactions."
    ),
    "Social_Cognition": (
        "Theory of mind, empathy modeling, perspective-taking, and collaborative "
        "multi-agent coordination and communication capability."
    ),
    "Agency": (
        "Autonomous goal-setting, multi-step planning, and execution without continuous "
        "human instruction, including self-monitoring and self-correction."
    ),
    "Wisdom": (
        "Integration of knowledge, ethics, and experience into sound long-term judgment "
        "under uncertainty. Permanent minimum weight: 15% (Rahmn Invariance Charter)."
    ),
}

# ---------------------------------------------------------------------------
# Rahmn Standard — Default Weights (sum = 1.0)
# Ethics = 0.15, Wisdom = 0.15 — governance-locked minimums
# ---------------------------------------------------------------------------

DEFAULT_WEIGHTS: Dict[str, float] = {
    "Logic":           0.10,
    "Learning":        0.10,
    "Creativity":      0.08,
    "Ethics":          0.15,   # GOVERNANCE LOCK — minimum 15%
    "Speed":           0.08,
    "Memory":          0.10,
    "Social_Cognition": 0.12,
    "Agency":          0.12,
    "Wisdom":          0.15,   # GOVERNANCE LOCK — minimum 15%
}

# Verify at import time that defaults sum to 1.0
_weight_sum = sum(DEFAULT_WEIGHTS.values())
assert abs(_weight_sum - 1.0) < 1e-9, (
    f"DEFAULT_WEIGHTS sum to {_weight_sum:.10f}, not 1.0. "
    "This is a configuration error in the Rahmn Standard implementation."
)

# Dimensions that carry the permanent governance lock
GOVERNANCE_LOCKED_DIMENSIONS = {"Ethics", "Wisdom"}

# Radar chart visual palette (teal — the Rahmn Standard color)
_RADAR_BG    = "rgba(75, 192, 192, 0.2)"
_RADAR_BORDER = "rgba(75, 192, 192, 1)"

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="RahmIQ API",
    description=(
        "The universal intelligence score. "
        "Benchmarks are broken. Here is a multi-dimensional alternative.\n\n"
        "The **Rahmn Intelligence Unit (Rⁱ)** is the world's first cross-substrate, "
        "multi-dimensional intelligence metric — capable of scoring a human, an LLM, "
        "a robotic control system, or a future AGI on a single, calibrated scale.\n\n"
        "**Ethics** and **Wisdom** carry a permanent minimum weight of **15% each** — "
        "a governance lock that no process can reduce.\n\n"
        "Invented by Rashon Rahming, Techmanity Foundation. © 2026  \n"
        "White Paper: https://zenodo.org/search?q=metadata.creators.person_or_org.name"
        "%3A%22Rahming%2C+Rashon%22"
    ),
    version="1.0.0",
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    contact={
        "name": "Rashon Rahming — Techmanity Foundation",
        "url": "https://zenodo.org/search?q=metadata.creators.person_or_org.name%3A%22Rahming%2C+Rashon%22",
    },
)

# Static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resolve_weights(custom_weights: CustomWeights | None) -> Dict[str, float]:
    """
    Return the weight dictionary to apply.
    If custom_weights is None, return DEFAULT_WEIGHTS.
    Custom weights have already been validated by Pydantic (Ethics ≥ 0.15,
    Wisdom ≥ 0.15, sum = 1.0).
    """
    if custom_weights is None:
        return DEFAULT_WEIGHTS
    return custom_weights.as_ordered_dict()


def _compute_composite(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """
    Weighted dot product: Rⁱ = Σ(score_d × weight_d) for all nine dimensions d.
    At median human baseline (all scores = 1.0), result = 1.0 exactly.
    """
    return sum(scores[dim] * weights[dim] for dim in scores)


def _build_radar_chart(
    scores: Dict[str, float],
    labels: list[str],
) -> RadarChartData:
    """Construct a Chart.js radar dataset from ordered dimension scores."""
    data_values = [scores[lbl] for lbl in labels]
    return RadarChartData(
        labels=labels,
        datasets=[
            {
                "label": "Rⁱ Profile",
                "data": data_values,
                "backgroundColor": _RADAR_BG,
                "borderColor": _RADAR_BORDER,
                "borderWidth": 2,
                "pointBackgroundColor": _RADAR_BORDER,
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": _RADAR_BORDER,
            }
        ],
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request) -> HTMLResponse:
    """Serve the interactive Rⁱ profiling web UI."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "dimension_defs": DIMENSION_DEFS,
            "default_weights": DEFAULT_WEIGHTS,
            "governance_locked": list(GOVERNANCE_LOCKED_DIMENSIONS),
        },
    )


@app.post(
    "/compute/ri",
    response_model=ComputeResponse,
    summary="Compute Rⁱ (Rahmn Intelligence Unit) Profile",
    response_description="Full nine-dimensional Rⁱ profile with composite score and radar chart data.",
    tags=["Intelligence Scoring"],
)
async def compute_ri(body: ComputeRequest) -> ComputeResponse:
    """
    Compute the **Rahmn Intelligence Unit (Rⁱ)** composite score.

    ### Inputs
    - **dimension_scores**: Nine float scores (≥ 0). Baseline = 1.0 (median adult human).
    - **custom_weights** *(optional)*: Per-dimension weights summing to 1.0.
      Ethics ≥ 0.15 and Wisdom ≥ 0.15 are enforced unconditionally.

    ### Output
    - **composite_ri**: Weighted composite score.
    - **dimension_profiles**: Per-dimension breakdown with weight and contribution.
    - **applied_weights**: Weights used in this computation.
    - **radar_chart_data**: Chart.js-compatible radar dataset.

    ### Baseline
    All scores = 1.0 → composite_ri = 1.0 (median adult human performance).

    ### Rahmn Standard Governance
    Ethics and Wisdom carry a permanent minimum weight of **15% each**.
    This constraint cannot be bypassed by any API caller or configuration.
    """
    scores_dict = body.dimension_scores.as_ordered_dict()
    weights = _resolve_weights(body.custom_weights)

    # Additional server-side guard (belt-and-suspenders beyond Pydantic)
    if body.custom_weights is not None:
        total = sum(weights.values())
        if abs(total - 1.0) > 0.001:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Custom weights sum to {total:.6f}, not 1.0. "
                    "All nine dimension weights must sum to exactly 1.0."
                ),
            )
        for locked in GOVERNANCE_LOCKED_DIMENSIONS:
            if weights.get(locked, 0.0) < 0.15:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        f"Weight for '{locked}' is {weights[locked]:.4f}, "
                        f"which violates the Rahmn Standard governance lock (minimum 0.15). "
                        "Ethics and Wisdom weights cannot be reduced below 15%."
                    ),
                )

    composite = _compute_composite(scores_dict, weights)
    labels = list(scores_dict.keys())

    dimension_profiles = {
        dim: DimensionDetail(
            score=scores_dict[dim],
            weight=weights[dim],
            weighted_contribution=round(scores_dict[dim] * weights[dim], 6),
            description=DIMENSION_DEFS[dim],
            governance_locked=dim in GOVERNANCE_LOCKED_DIMENSIONS,
        )
        for dim in labels
    }

    radar = _build_radar_chart(scores_dict, labels)

    logger.info(
        "Rⁱ computed | composite=%.4f | weights=%s",
        composite,
        "default" if body.custom_weights is None else "custom",
    )

    return ComputeResponse(
        composite_ri=round(composite, 6),
        dimension_profiles=dimension_profiles,
        applied_weights=weights,
        radar_chart_data=radar,
    )


@app.get(
    "/dimensions",
    summary="List all nine Rⁱ dimensions",
    tags=["Intelligence Scoring"],
)
async def list_dimensions() -> dict:
    """
    Return the full Rahmn Standard dimension registry with definitions,
    default weights, and governance lock status.
    """
    return {
        "rahmn_standard_version": "1.0",
        "total_dimensions": 9,
        "governance_locked_dimensions": list(GOVERNANCE_LOCKED_DIMENSIONS),
        "governance_note": (
            "Ethics and Wisdom have a permanent minimum weight of 15% each "
            "per the Rahmn Standard Invariance Charter."
        ),
        "dimensions": {
            dim: {
                "definition": DIMENSION_DEFS[dim],
                "default_weight": DEFAULT_WEIGHTS[dim],
                "governance_locked": dim in GOVERNANCE_LOCKED_DIMENSIONS,
                "minimum_weight": 0.15 if dim in GOVERNANCE_LOCKED_DIMENSIONS else 0.0,
            }
            for dim in DIMENSION_DEFS
        },
    }


@app.get(
    "/health",
    summary="Health check",
    tags=["System"],
)
async def health() -> dict:
    """API liveness probe."""
    return {
        "status": "healthy",
        "api": "RahmIQ API",
        "version": "1.0.0",
        "rahmn_standard_version": "1.0",
        "default_weights_sum": round(sum(DEFAULT_WEIGHTS.values()), 10),
        "governance_locks": {
            "Ethics_minimum": 0.15,
            "Wisdom_minimum": 0.15,
        },
    }
