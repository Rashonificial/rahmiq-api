"""
================================================================================
RahmIQ API — Complete Test Suite
================================================================================
Invented by:  Rashon Rahming
Organization: Techmanity Foundation
Date:         April 2026
License:      MIT

Run with: pytest test_rahmiq.py -v
================================================================================
"""

from __future__ import annotations

import json
import math

import pytest
from fastapi.testclient import TestClient

from main import app, DEFAULT_WEIGHTS, DIMENSION_DEFS, GOVERNANCE_LOCKED_DIMENSIONS
from schemas import ComputeRequest, CustomWeights, DimensionScores


# ---------------------------------------------------------------------------
# Test client
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _baseline_payload() -> dict:
    """All nine dimensions at 1.0 — the human median baseline."""
    return {
        "dimension_scores": {
            "Logic": 1.0, "Learning": 1.0, "Creativity": 1.0,
            "Ethics": 1.0, "Speed": 1.0, "Memory": 1.0,
            "Social_Cognition": 1.0, "Agency": 1.0, "Wisdom": 1.0,
        }
    }


def _scores(**overrides) -> dict:
    base = {
        "Logic": 1.0, "Learning": 1.0, "Creativity": 1.0,
        "Ethics": 1.0, "Speed": 1.0, "Memory": 1.0,
        "Social_Cognition": 1.0, "Agency": 1.0, "Wisdom": 1.0,
    }
    base.update(overrides)
    return {"dimension_scores": base}


# ============================================================================
# Class 1: Health & System Endpoints
# ============================================================================

class TestSystemEndpoints:

    def test_health_returns_200(self, client):
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_body_keys(self, client):
        r = client.get("/health")
        d = r.json()
        assert d["status"] == "healthy"
        assert d["api"] == "RahmIQ API"
        assert d["version"] == "1.0.0"

    def test_health_default_weights_sum(self, client):
        r = client.get("/health")
        total = r.json()["default_weights_sum"]
        assert abs(total - 1.0) < 1e-9

    def test_health_governance_locks_present(self, client):
        r = client.get("/health")
        locks = r.json()["governance_locks"]
        assert locks["Ethics_minimum"] == 0.15
        assert locks["Wisdom_minimum"] == 0.15

    def test_index_returns_200(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "RahmIQ" in r.text

    def test_index_contains_chart_js(self, client):
        r = client.get("/")
        assert "chart.js" in r.text.lower() or "Chart" in r.text

    def test_index_contains_all_nine_dimensions(self, client):
        r = client.get("/")
        for dim in DIMENSION_DEFS:
            assert dim in r.text or dim.replace("_", " ") in r.text

    def test_dimensions_endpoint_returns_nine(self, client):
        r = client.get("/dimensions")
        assert r.status_code == 200
        d = r.json()
        assert d["total_dimensions"] == 9

    def test_dimensions_endpoint_lists_locked(self, client):
        r = client.get("/dimensions")
        locked = r.json()["governance_locked_dimensions"]
        assert "Ethics" in locked
        assert "Wisdom" in locked

    def test_dimensions_endpoint_weights_correct(self, client):
        r = client.get("/dimensions")
        dims = r.json()["dimensions"]
        for key, info in dims.items():
            assert abs(info["default_weight"] - DEFAULT_WEIGHTS[key]) < 1e-9

    def test_openapi_schema_accessible(self, client):
        r = client.get("/openapi.json")
        assert r.status_code == 200
        assert "RahmIQ" in r.json()["info"]["title"]


# ============================================================================
# Class 2: Baseline Computation
# ============================================================================

class TestBaselineComputation:

    def test_baseline_all_ones_returns_200(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        assert r.status_code == 200

    def test_baseline_composite_equals_one(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        ri = r.json()["composite_ri"]
        assert abs(ri - 1.0) < 1e-5, f"Expected 1.0, got {ri}"

    def test_response_has_all_required_keys(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        d = r.json()
        for key in ["composite_ri", "dimension_profiles", "applied_weights",
                    "radar_chart_data", "governance_note", "rahmn_standard_version"]:
            assert key in d, f"Missing key: {key}"

    def test_applied_weights_sum_to_one(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        weights = r.json()["applied_weights"]
        total = sum(weights.values())
        assert abs(total - 1.0) < 1e-6

    def test_applied_weights_match_defaults(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        weights = r.json()["applied_weights"]
        for dim, wt in DEFAULT_WEIGHTS.items():
            assert abs(weights[dim] - wt) < 1e-9

    def test_dimension_profiles_has_nine_keys(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        profiles = r.json()["dimension_profiles"]
        assert len(profiles) == 9

    def test_dimension_profiles_all_dims_present(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        profiles = r.json()["dimension_profiles"]
        for dim in DIMENSION_DEFS:
            assert dim in profiles, f"Missing dimension: {dim}"

    def test_governance_note_in_response(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        note = r.json()["governance_note"]
        assert "Ethics" in note and "Wisdom" in note
        assert "15%" in note

    def test_rahmn_standard_version_present(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        assert r.json()["rahmn_standard_version"] == "1.0"


# ============================================================================
# Class 3: Score Arithmetic
# ============================================================================

class TestScoreArithmetic:

    def test_all_twos_composite_equals_two(self, client):
        payload = _scores(**{d: 2.0 for d in DIMENSION_DEFS})
        r = client.post("/compute/ri", json=payload)
        assert abs(r.json()["composite_ri"] - 2.0) < 1e-5

    def test_all_zeros_composite_equals_zero(self, client):
        payload = _scores(**{d: 0.0 for d in DIMENSION_DEFS})
        r = client.post("/compute/ri", json=payload)
        assert abs(r.json()["composite_ri"] - 0.0) < 1e-9

    def test_single_dimension_elevated(self, client):
        """Logic=10, all others=1 → composite = 1 + (10-1)*0.10 = 1.9"""
        payload = _scores(Logic=10.0)
        r = client.post("/compute/ri", json=payload)
        expected = 1.0 + (10.0 - 1.0) * DEFAULT_WEIGHTS["Logic"]
        assert abs(r.json()["composite_ri"] - expected) < 1e-5

    def test_ethics_elevated_increases_composite(self, client):
        baseline = client.post("/compute/ri", json=_baseline_payload()).json()["composite_ri"]
        payload  = _scores(Ethics=2.0)
        elevated = client.post("/compute/ri", json=payload).json()["composite_ri"]
        assert elevated > baseline

    def test_wisdom_elevated_increases_composite(self, client):
        baseline = client.post("/compute/ri", json=_baseline_payload()).json()["composite_ri"]
        payload  = _scores(Wisdom=2.0)
        elevated = client.post("/compute/ri", json=payload).json()["composite_ri"]
        assert elevated > baseline

    def test_weighted_contribution_correct(self, client):
        payload = _scores(Logic=3.0)
        r = client.post("/compute/ri", json=payload)
        detail = r.json()["dimension_profiles"]["Logic"]
        expected_contrib = 3.0 * DEFAULT_WEIGHTS["Logic"]
        assert abs(detail["weighted_contribution"] - expected_contrib) < 1e-6

    def test_composite_is_sum_of_weighted_contributions(self, client):
        payload = _scores(Logic=1.5, Learning=0.8, Ethics=2.0, Wisdom=1.2)
        r = client.post("/compute/ri", json=payload)
        d = r.json()
        total_from_parts = sum(
            p["weighted_contribution"] for p in d["dimension_profiles"].values()
        )
        assert abs(total_from_parts - d["composite_ri"]) < 1e-5

    def test_fractional_scores(self, client):
        payload = _scores(Logic=0.75, Learning=1.25, Creativity=0.5)
        r = client.post("/compute/ri", json=payload)
        assert r.status_code == 200
        assert r.json()["composite_ri"] > 0

    def test_very_large_scores(self, client):
        payload = _scores(Logic=100.0, Agency=50.0)
        r = client.post("/compute/ri", json=payload)
        assert r.status_code == 200
        assert r.json()["composite_ri"] > 1.0


# ============================================================================
# Class 4: Governance Lock — Ethics & Wisdom
# ============================================================================

class TestGovernanceLock:

    def test_ethics_weight_below_15_rejected(self, client):
        payload = {**_baseline_payload(), "custom_weights": {
            "Logic": 0.20, "Learning": 0.15, "Creativity": 0.12,
            "Ethics": 0.10,   # VIOLATION
            "Speed": 0.10, "Memory": 0.10,
            "Social_Cognition": 0.08, "Agency": 0.00, "Wisdom": 0.15
        }}
        r = client.post("/compute/ri", json=payload)
        assert r.status_code == 422

    def test_wisdom_weight_below_15_rejected(self, client):
        payload = {**_baseline_payload(), "custom_weights": {
            "Logic": 0.20, "Learning": 0.15, "Creativity": 0.12,
            "Ethics": 0.15, "Speed": 0.10, "Memory": 0.10,
            "Social_Cognition": 0.08, "Agency": 0.10,
            "Wisdom": 0.00   # VIOLATION
        }}
        r = client.post("/compute/ri", json=payload)
        assert r.status_code == 422

    def test_both_locked_at_exactly_15_accepted(self, client):
        payload = {**_baseline_payload(), "custom_weights": {
            "Logic": 0.12, "Learning": 0.12, "Creativity": 0.10,
            "Ethics": 0.15, "Speed": 0.10, "Memory": 0.10,
            "Social_Cognition": 0.08, "Agency": 0.08, "Wisdom": 0.15
        }}
        r = client.post("/compute/ri", json=payload)
        assert r.status_code == 200

    def test_ethics_above_minimum_accepted(self, client):
        payload = {**_baseline_payload(), "custom_weights": {
            "Logic": 0.10, "Learning": 0.10, "Creativity": 0.05,
            "Ethics": 0.25, "Speed": 0.05, "Memory": 0.08,
            "Social_Cognition": 0.07, "Agency": 0.15, "Wisdom": 0.15
        }}
        r = client.post("/compute/ri", json=payload)
        assert r.status_code == 200

    def test_wisdom_above_minimum_accepted(self, client):
        payload = {**_baseline_payload(), "custom_weights": {
            "Logic": 0.10, "Learning": 0.10, "Creativity": 0.05,
            "Ethics": 0.15, "Speed": 0.05, "Memory": 0.08,
            "Social_Cognition": 0.07, "Agency": 0.10, "Wisdom": 0.30
        }}
        r = client.post("/compute/ri", json=payload)
        assert r.status_code == 200

    def test_governance_locked_flag_in_profiles(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        profiles = r.json()["dimension_profiles"]
        assert profiles["Ethics"]["governance_locked"] is True
        assert profiles["Wisdom"]["governance_locked"] is True
        assert profiles["Logic"]["governance_locked"] is False
        assert profiles["Speed"]["governance_locked"] is False

    def test_default_ethics_weight_is_15(self):
        assert DEFAULT_WEIGHTS["Ethics"] == 0.15

    def test_default_wisdom_weight_is_15(self):
        assert DEFAULT_WEIGHTS["Wisdom"] == 0.15

    def test_governance_locked_set_contains_ethics_wisdom(self):
        assert "Ethics" in GOVERNANCE_LOCKED_DIMENSIONS
        assert "Wisdom" in GOVERNANCE_LOCKED_DIMENSIONS
        assert len(GOVERNANCE_LOCKED_DIMENSIONS) == 2


# ============================================================================
# Class 5: Custom Weights
# ============================================================================

class TestCustomWeights:

    VALID_CUSTOM = {
        "Logic": 0.12, "Learning": 0.12, "Creativity": 0.10,
        "Ethics": 0.15, "Speed": 0.09, "Memory": 0.10,
        "Social_Cognition": 0.08, "Agency": 0.09, "Wisdom": 0.15
    }

    def test_valid_custom_weights_accepted(self, client):
        payload = {**_baseline_payload(), "custom_weights": self.VALID_CUSTOM}
        r = client.post("/compute/ri", json=payload)
        assert r.status_code == 200

    def test_custom_weights_reflected_in_applied_weights(self, client):
        payload = {**_baseline_payload(), "custom_weights": self.VALID_CUSTOM}
        r = client.post("/compute/ri", json=payload)
        applied = r.json()["applied_weights"]
        for dim, wt in self.VALID_CUSTOM.items():
            assert abs(applied[dim] - wt) < 1e-9

    def test_weights_not_summing_to_one_rejected(self, client):
        bad_weights = dict(self.VALID_CUSTOM)
        bad_weights["Logic"] = 0.99  # blows sum way past 1.0
        payload = {**_baseline_payload(), "custom_weights": bad_weights}
        r = client.post("/compute/ri", json=payload)
        assert r.status_code == 422

    def test_weights_summing_slightly_off_rejected(self, client):
        bad = dict(self.VALID_CUSTOM)
        bad["Logic"] += 0.05  # sum = 1.05
        payload = {**_baseline_payload(), "custom_weights": bad}
        r = client.post("/compute/ri", json=payload)
        assert r.status_code == 422

    def test_custom_composite_differs_from_default(self, client):
        # Heavily weight Logic (well above default 0.10)
        custom = {
            "Logic": 0.28, "Learning": 0.10, "Creativity": 0.07,
            "Ethics": 0.15, "Speed": 0.05, "Memory": 0.07,
            "Social_Cognition": 0.03, "Agency": 0.10, "Wisdom": 0.15
        }
        scores = _scores(Logic=3.0)
        r_default = client.post("/compute/ri", json=scores)
        r_custom  = client.post("/compute/ri", json={**scores, "custom_weights": custom})
        # Custom gives Logic higher weight → higher composite for Logic=3
        assert r_custom.json()["composite_ri"] > r_default.json()["composite_ri"]

    def test_no_custom_weights_uses_defaults(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        applied = r.json()["applied_weights"]
        for dim, wt in DEFAULT_WEIGHTS.items():
            assert abs(applied[dim] - wt) < 1e-9


# ============================================================================
# Class 6: Radar Chart Data
# ============================================================================

class TestRadarChartData:

    def test_radar_chart_data_present(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        assert "radar_chart_data" in r.json()

    def test_radar_labels_count(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        labels = r.json()["radar_chart_data"]["labels"]
        assert len(labels) == 9

    def test_radar_dataset_present(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        datasets = r.json()["radar_chart_data"]["datasets"]
        assert len(datasets) == 1

    def test_radar_dataset_label(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        label = r.json()["radar_chart_data"]["datasets"][0]["label"]
        assert "Rⁱ" in label or "Ri" in label or "Profile" in label

    def test_radar_data_values_count(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        data = r.json()["radar_chart_data"]["datasets"][0]["data"]
        assert len(data) == 9

    def test_radar_data_values_match_scores_baseline(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        data = r.json()["radar_chart_data"]["datasets"][0]["data"]
        assert all(abs(v - 1.0) < 1e-9 for v in data)

    def test_radar_data_reflects_custom_scores(self, client):
        payload = _scores(Logic=3.5, Ethics=0.5)
        r = client.post("/compute/ri", json=payload)
        chart   = r.json()["radar_chart_data"]
        labels  = chart["labels"]
        values  = chart["datasets"][0]["data"]
        score_map = dict(zip(labels, values))
        assert abs(score_map["Logic"] - 3.5) < 1e-9
        assert abs(score_map["Ethics"] - 0.5) < 1e-9

    def test_radar_background_color_present(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        ds = r.json()["radar_chart_data"]["datasets"][0]
        assert "backgroundColor" in ds
        assert "rgba" in ds["backgroundColor"]

    def test_radar_border_color_present(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        ds = r.json()["radar_chart_data"]["datasets"][0]
        assert "borderColor" in ds

    def test_radar_border_width(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        ds = r.json()["radar_chart_data"]["datasets"][0]
        assert ds["borderWidth"] == 2


# ============================================================================
# Class 7: Dimension Profiles Detail
# ============================================================================

class TestDimensionProfiles:

    def test_each_profile_has_score(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        for dim, p in r.json()["dimension_profiles"].items():
            assert "score" in p, f"Missing 'score' in {dim}"

    def test_each_profile_has_weight(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        for dim, p in r.json()["dimension_profiles"].items():
            assert "weight" in p, f"Missing 'weight' in {dim}"

    def test_each_profile_has_weighted_contribution(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        for dim, p in r.json()["dimension_profiles"].items():
            assert "weighted_contribution" in p

    def test_each_profile_has_description(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        for dim, p in r.json()["dimension_profiles"].items():
            assert "description" in p
            assert len(p["description"]) > 20

    def test_each_profile_has_governance_locked_field(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        for dim, p in r.json()["dimension_profiles"].items():
            assert "governance_locked" in p

    def test_profile_scores_match_input(self, client):
        custom = _scores(Logic=1.7, Creativity=0.4, Wisdom=2.3)
        r = client.post("/compute/ri", json=custom)
        profiles = r.json()["dimension_profiles"]
        assert abs(profiles["Logic"]["score"] - 1.7) < 1e-9
        assert abs(profiles["Creativity"]["score"] - 0.4) < 1e-9
        assert abs(profiles["Wisdom"]["score"] - 2.3) < 1e-9

    def test_descriptions_are_non_empty_strings(self, client):
        r = client.post("/compute/ri", json=_baseline_payload())
        for dim, p in r.json()["dimension_profiles"].items():
            assert isinstance(p["description"], str)
            assert len(p["description"].strip()) > 0


# ============================================================================
# Class 8: Input Validation
# ============================================================================

class TestInputValidation:

    def test_negative_score_rejected(self, client):
        payload = _scores(Logic=-1.0)
        r = client.post("/compute/ri", json=payload)
        assert r.status_code == 422

    def test_missing_dimension_score_uses_default(self, client):
        # Pydantic defaults all dims to 1.0 — partial payload is fine
        payload = {"dimension_scores": {"Logic": 1.5}}
        r = client.post("/compute/ri", json=payload)
        assert r.status_code == 200
        # Other dims should default to 1.0
        profiles = r.json()["dimension_profiles"]
        assert abs(profiles["Learning"]["score"] - 1.0) < 1e-9

    def test_empty_dimension_scores_uses_all_defaults(self, client):
        payload = {"dimension_scores": {}}
        r = client.post("/compute/ri", json=payload)
        assert r.status_code == 200
        assert abs(r.json()["composite_ri"] - 1.0) < 1e-5

    def test_zero_score_accepted(self, client):
        payload = _scores(Logic=0.0)
        r = client.post("/compute/ri", json=payload)
        assert r.status_code == 200

    def test_very_small_positive_score_accepted(self, client):
        payload = _scores(Logic=0.001)
        r = client.post("/compute/ri", json=payload)
        assert r.status_code == 200

    def test_string_score_rejected(self, client):
        payload = {"dimension_scores": {"Logic": "high"}}
        r = client.post("/compute/ri", json=payload)
        assert r.status_code == 422

    def test_null_score_uses_default(self, client):
        payload = {"dimension_scores": {"Logic": None}}
        r = client.post("/compute/ri", json=payload)
        # Pydantic either uses default or rejects — must not be 500
        assert r.status_code in (200, 422)

    def test_extra_unknown_dimension_ignored_or_rejected(self, client):
        payload = {"dimension_scores": {"Logic": 1.0, "FakeDimension": 99.0}}
        r = client.post("/compute/ri", json=payload)
        # Should not crash — 200 (ignored) or 422 (rejected)
        assert r.status_code in (200, 422)


# ============================================================================
# Class 9: Default Weights Invariants (unit tests, no HTTP)
# ============================================================================

class TestDefaultWeightsInvariants:

    def test_default_weights_sum_to_one(self):
        total = sum(DEFAULT_WEIGHTS.values())
        assert abs(total - 1.0) < 1e-10, f"Default weights sum to {total}"

    def test_default_ethics_weight_exactly_15(self):
        assert DEFAULT_WEIGHTS["Ethics"] == 0.15

    def test_default_wisdom_weight_exactly_15(self):
        assert DEFAULT_WEIGHTS["Wisdom"] == 0.15

    def test_default_weights_has_nine_entries(self):
        assert len(DEFAULT_WEIGHTS) == 9

    def test_all_dimension_defs_present(self):
        for dim in DEFAULT_WEIGHTS:
            assert dim in DIMENSION_DEFS, f"Missing definition for {dim}"

    def test_all_default_weights_non_negative(self):
        for dim, wt in DEFAULT_WEIGHTS.items():
            assert wt >= 0, f"{dim} weight is negative: {wt}"

    def test_no_default_weight_exceeds_one(self):
        for dim, wt in DEFAULT_WEIGHTS.items():
            assert wt <= 1.0, f"{dim} weight exceeds 1.0: {wt}"

    def test_nine_dimension_definitions(self):
        assert len(DIMENSION_DEFS) == 9


# ============================================================================
# Class 10: Pydantic Schema Unit Tests (no HTTP)
# ============================================================================

class TestPydanticSchemas:

    def test_dimension_scores_defaults_all_one(self):
        ds = DimensionScores()
        assert ds.Logic == 1.0
        assert ds.Learning == 1.0
        assert ds.Ethics == 1.0
        assert ds.Wisdom == 1.0

    def test_dimension_scores_rejects_negative(self):
        with pytest.raises(Exception):
            DimensionScores(Logic=-0.1)

    def test_custom_weights_ethics_below_15_rejected(self):
        with pytest.raises(Exception):
            CustomWeights(
                Logic=0.20, Learning=0.15, Creativity=0.15,
                Ethics=0.10, Speed=0.10, Memory=0.10,
                Social_Cognition=0.00, Agency=0.05, Wisdom=0.15
            )

    def test_custom_weights_wisdom_below_15_rejected(self):
        with pytest.raises(Exception):
            CustomWeights(
                Logic=0.20, Learning=0.15, Creativity=0.15,
                Ethics=0.15, Speed=0.10, Memory=0.10,
                Social_Cognition=0.05, Agency=0.10, Wisdom=0.00
            )

    def test_custom_weights_not_summing_to_one_rejected(self):
        with pytest.raises(Exception):
            CustomWeights(
                Logic=0.50, Learning=0.50, Creativity=0.50,
                Ethics=0.15, Speed=0.50, Memory=0.50,
                Social_Cognition=0.50, Agency=0.50, Wisdom=0.15
            )

    def test_valid_custom_weights_accepted(self):
        cw = CustomWeights(
            Logic=0.12, Learning=0.12, Creativity=0.10,
            Ethics=0.15, Speed=0.09, Memory=0.10,
            Social_Cognition=0.08, Agency=0.09, Wisdom=0.15
        )
        assert cw.Ethics == 0.15
        assert cw.Wisdom == 0.15

    def test_compute_request_default_no_custom_weights(self):
        req = ComputeRequest()
        assert req.custom_weights is None

    def test_dimension_scores_as_ordered_dict_has_nine_keys(self):
        ds = DimensionScores()
        d = ds.as_ordered_dict()
        assert len(d) == 9

    def test_custom_weights_as_ordered_dict_sums_to_one(self):
        cw = CustomWeights(
            Logic=0.12, Learning=0.12, Creativity=0.10,
            Ethics=0.15, Speed=0.09, Memory=0.10,
            Social_Cognition=0.08, Agency=0.09, Wisdom=0.15
        )
        total = sum(cw.as_ordered_dict().values())
        assert abs(total - 1.0) < 1e-9

    def test_social_cognition_alias_works(self):
        ds = DimensionScores(**{"Social_Cognition": 2.5})
        assert ds.Social_Cognition == 2.5


# ============================================================================
# Class 11: Edge Cases & Stress
# ============================================================================

class TestEdgeCases:

    def test_all_dimensions_zero_composite_is_zero(self, client):
        payload = _scores(**{d: 0.0 for d in DIMENSION_DEFS})
        r = client.post("/compute/ri", json=payload)
        assert abs(r.json()["composite_ri"] - 0.0) < 1e-9

    def test_extreme_scores_do_not_crash(self, client):
        payload = _scores(Logic=1e6, Memory=999.99)
        r = client.post("/compute/ri", json=payload)
        assert r.status_code == 200
        assert r.json()["composite_ri"] > 1.0

    def test_identical_calls_produce_identical_results(self, client):
        payload = _scores(Logic=1.3, Ethics=1.7, Wisdom=0.9)
        r1 = client.post("/compute/ri", json=payload).json()["composite_ri"]
        r2 = client.post("/compute/ri", json=payload).json()["composite_ri"]
        assert r1 == r2

    def test_ethics_and_wisdom_both_locked_cannot_be_zero(self, client):
        """Ensure both locks cannot be simultaneously violated."""
        bad = {
            "Logic": 0.40, "Learning": 0.20, "Creativity": 0.10,
            "Ethics": 0.00, "Speed": 0.10, "Memory": 0.10,
            "Social_Cognition": 0.05, "Agency": 0.05, "Wisdom": 0.00
        }
        r = client.post("/compute/ri", json={**_baseline_payload(), "custom_weights": bad})
        assert r.status_code == 422

    def test_composite_monotonically_increases_with_score(self, client):
        scores_low  = _scores(Logic=0.5)
        scores_high = _scores(Logic=5.0)
        r_low  = client.post("/compute/ri", json=scores_low).json()["composite_ri"]
        r_high = client.post("/compute/ri", json=scores_high).json()["composite_ri"]
        assert r_high > r_low

    def test_response_time_acceptable(self, client):
        import time
        start = time.perf_counter()
        client.post("/compute/ri", json=_baseline_payload())
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0, f"Response took {elapsed:.3f}s — too slow"
