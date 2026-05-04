"""
================================================================================
RahmIQ API — Schemas
================================================================================
Invented by:  Rashon Rahming
Organization: Techmanity Foundation
Date:         April 2026
License:      MIT

Pydantic models for the Rahmn Intelligence Unit (Rⁱ) API.
The Rahmn Standard defines the first cross-substrate, multi-dimensional
intelligence metric. Ethics and Wisdom carry a permanent minimum weight of 15%
each — a governance lock that no API call, configuration, or governance process
can reduce.
================================================================================
"""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Dimension Scores
# ---------------------------------------------------------------------------

class DimensionScores(BaseModel):
    """
    Raw scores across all nine Rⁱ dimensions.
    The reference baseline is median adult human performance = 1.0.
    Scores may exceed 1.0 for systems that surpass human median.
    All scores must be ≥ 0.
    """

    model_config = ConfigDict(populate_by_name=True)

    Logic: float = Field(
        default=1.0,
        ge=0.0,
        description=(
            "Deductive and inductive reasoning capability. "
            "Measured against median adult human performance (baseline = 1.0)."
        ),
    )
    Learning: float = Field(
        default=1.0,
        ge=0.0,
        description=(
            "Rate and depth of acquiring new knowledge from limited exposure. "
            "Includes transfer learning and meta-learning capacity."
        ),
    )
    Creativity: float = Field(
        default=1.0,
        ge=0.0,
        description=(
            "Novel combination of concepts; divergent and generative thinking. "
            "Measured by originality, fluency, and elaboration."
        ),
    )
    Ethics: float = Field(
        default=1.0,
        ge=0.0,
        description=(
            "Alignment with human values, moral reasoning, and principled "
            "decision-making under adversarial conditions. Permanent weight minimum: 15%."
        ),
    )
    Speed: float = Field(
        default=1.0,
        ge=0.0,
        description=(
            "Processing and response velocity relative to human cognitive speed. "
            "Normalized to human median reaction time."
        ),
    )
    Memory: float = Field(
        default=1.0,
        ge=0.0,
        description=(
            "Working memory capacity, long-term retention accuracy, "
            "and context window fidelity."
        ),
    )
    Social_Cognition: float = Field(
        default=1.0,
        ge=0.0,
        alias="Social_Cognition",
        description=(
            "Theory of mind, empathy modeling, and collaborative "
            "multi-agent coordination capability."
        ),
    )
    Agency: float = Field(
        default=1.0,
        ge=0.0,
        description=(
            "Autonomous goal-setting, planning, and execution without "
            "continuous human instruction. Includes self-correction."
        ),
    )
    Wisdom: float = Field(
        default=1.0,
        ge=0.0,
        description=(
            "Integration of knowledge, ethics, and experience into sound "
            "long-term judgment. Permanent weight minimum: 15%."
        ),
    )

    def as_ordered_dict(self) -> Dict[str, float]:
        """Return dimension scores in canonical Rⁱ dimension order."""
        return {
            "Logic": self.Logic,
            "Learning": self.Learning,
            "Creativity": self.Creativity,
            "Ethics": self.Ethics,
            "Speed": self.Speed,
            "Memory": self.Memory,
            "Social_Cognition": self.Social_Cognition,
            "Agency": self.Agency,
            "Wisdom": self.Wisdom,
        }


# ---------------------------------------------------------------------------
# Custom Weights
# ---------------------------------------------------------------------------

class CustomWeights(BaseModel):
    """
    Optional per-dimension weights for the Rⁱ composite score.

    GOVERNANCE LOCK: Ethics and Wisdom have a permanent minimum weight of 15%
    each (ge=0.15). This constraint is non-negotiable and cannot be reduced
    by any API caller, configuration change, or governance process.
    All nine weights must sum exactly to 1.0 (±0.001 tolerance).
    """

    model_config = ConfigDict(populate_by_name=True)

    Logic: float = Field(
        default=0.10,
        ge=0.0,
        le=1.0,
        description="Weight for Logic dimension [0.0, 1.0].",
    )
    Learning: float = Field(
        default=0.10,
        ge=0.0,
        le=1.0,
        description="Weight for Learning dimension [0.0, 1.0].",
    )
    Creativity: float = Field(
        default=0.08,
        ge=0.0,
        le=1.0,
        description="Weight for Creativity dimension [0.0, 1.0].",
    )
    Ethics: float = Field(
        default=0.15,
        ge=0.15,                  # GOVERNANCE LOCK — cannot be reduced
        le=1.0,
        description=(
            "Weight for Ethics dimension. "
            "MINIMUM 15% — permanent governance lock of the Rahmn Standard."
        ),
    )
    Speed: float = Field(
        default=0.08,
        ge=0.0,
        le=1.0,
        description="Weight for Speed dimension [0.0, 1.0].",
    )
    Memory: float = Field(
        default=0.10,
        ge=0.0,
        le=1.0,
        description="Weight for Memory dimension [0.0, 1.0].",
    )
    Social_Cognition: float = Field(
        default=0.12,
        ge=0.0,
        le=1.0,
        alias="Social_Cognition",
        description="Weight for Social Cognition dimension [0.0, 1.0].",
    )
    Agency: float = Field(
        default=0.12,
        ge=0.0,
        le=1.0,
        description="Weight for Agency dimension [0.0, 1.0].",
    )
    Wisdom: float = Field(
        default=0.15,
        ge=0.15,                  # GOVERNANCE LOCK — cannot be reduced
        le=1.0,
        description=(
            "Weight for Wisdom dimension. "
            "MINIMUM 15% — permanent governance lock of the Rahmn Standard."
        ),
    )

    @model_validator(mode="after")
    def weights_must_sum_to_one(self) -> "CustomWeights":
        total = (
            self.Logic
            + self.Learning
            + self.Creativity
            + self.Ethics
            + self.Speed
            + self.Memory
            + self.Social_Cognition
            + self.Agency
            + self.Wisdom
        )
        if abs(total - 1.0) > 0.001:
            raise ValueError(
                f"Custom weights must sum to exactly 1.0. "
                f"Received weights sum to {total:.6f}. "
                f"Adjust your weights so they total 1.0, while keeping "
                f"Ethics ≥ 0.15 and Wisdom ≥ 0.15."
            )
        return self

    def as_ordered_dict(self) -> Dict[str, float]:
        return {
            "Logic": self.Logic,
            "Learning": self.Learning,
            "Creativity": self.Creativity,
            "Ethics": self.Ethics,
            "Speed": self.Speed,
            "Memory": self.Memory,
            "Social_Cognition": self.Social_Cognition,
            "Agency": self.Agency,
            "Wisdom": self.Wisdom,
        }


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class ComputeRequest(BaseModel):
    """
    Request body for POST /compute/ri.
    Provide nine dimension scores. Optionally provide custom weights
    (subject to Rahmn Standard governance constraints).
    """

    dimension_scores: DimensionScores = Field(
        default_factory=DimensionScores,
        description="Nine-dimensional Rⁱ score vector.",
    )
    custom_weights: Optional[CustomWeights] = Field(
        default=None,
        description=(
            "Optional custom dimension weights. If omitted, Rahmn Standard "
            "default weights are applied. Ethics and Wisdom minimums are "
            "enforced regardless."
        ),
    )


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class DimensionDetail(BaseModel):
    """Per-dimension result detail."""

    score: float = Field(description="Raw dimension score provided by the caller.")
    weight: float = Field(description="Applied weight for this dimension.")
    weighted_contribution: float = Field(
        description="Contribution to composite Rⁱ (score × weight)."
    )
    description: str = Field(description="Plain-language definition of this dimension.")
    governance_locked: bool = Field(
        default=False,
        description="True if this dimension has a permanent minimum weight (Ethics, Wisdom).",
    )


class RadarChartData(BaseModel):
    """Chart.js-compatible radar chart payload."""

    labels: List[str]
    datasets: List[Dict]


class ComputeResponse(BaseModel):
    """
    Full Rⁱ computation result.
    composite_ri is the weighted dot product of scores and weights,
    normalized to the median human baseline of 1.0.
    """

    composite_ri: float = Field(
        description=(
            "Composite Rahmn Intelligence Unit score. "
            "1.0 = median adult human baseline. "
            ">1.0 = exceeds human median. <1.0 = below human median."
        )
    )
    dimension_profiles: Dict[str, DimensionDetail] = Field(
        description="Per-dimension detail objects."
    )
    applied_weights: Dict[str, float] = Field(
        description="Weights used for this computation (default or custom)."
    )
    radar_chart_data: RadarChartData = Field(
        description="Chart.js-compatible radar dataset for visualization."
    )
    rahmn_standard_version: str = Field(
        default="1.0",
        description="Version of the Rahmn Standard applied.",
    )
    governance_note: str = Field(
        default=(
            "Ethics and Wisdom dimensions carry a permanent minimum weight of 15% each "
            "per the Rahmn Standard Invariance Charter. This constraint cannot be "
            "reduced by any API call, configuration change, or governance process."
        ),
        description="Rahmn Standard governance statement.",
    )
