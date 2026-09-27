import dataclasses
import math

import pytest

from src.n0_physical_profile import (
    N0_FORBIDDEN_TRUTH_FIELDS,
    N0_REALIZATION_STATUS,
    N0PhysicalProfile,
    build_default_n0_physical_profile,
    canonical_json_value,
)


def test_default_profile_is_simulation_only():
    profile = build_default_n0_physical_profile()

    assert profile.realization_status == "simulated"
    assert profile.realization_status == N0_REALIZATION_STATUS
    assert profile.carrier_family == "stabilized-cat-bosonic"
    assert profile.permitted_command_phases_rad == (
        0.0,
        math.pi / 2.0,
    )


@pytest.mark.parametrize(
    "status",
    (
        "physical_approximate",
        "physical_exact",
        "native",
    ),
)
def test_profile_rejects_physical_or_native_status(status):
    profile = build_default_n0_physical_profile()

    values = profile.to_dict()
    values.pop("schema")
    values["realization_status"] = status

    with pytest.raises(
        ValueError,
        match="simulation-only",
    ):
        N0PhysicalProfile(**values)


def test_forbidden_truth_fields_cannot_be_weakened():
    profile = build_default_n0_physical_profile()

    values = profile.to_dict()
    values.pop("schema")
    values["forbidden_truth_fields"] = (
        "semantic_answer",
    )

    with pytest.raises(
        ValueError,
        match="cannot be weakened",
    ):
        N0PhysicalProfile(**values)


def test_forbidden_truth_fields_are_explicit():
    profile = build_default_n0_physical_profile()

    assert (
        profile.forbidden_truth_fields
        == N0_FORBIDDEN_TRUTH_FIELDS
    )

    assert "truth_phase" in profile.forbidden_truth_fields
    assert "expected_order" in profile.forbidden_truth_fields


def test_profile_is_immutable():
    profile = build_default_n0_physical_profile()

    with pytest.raises(
        dataclasses.FrozenInstanceError
    ):
        profile.profile_id = "mutated"


def test_profile_hash_is_deterministic():
    first = build_default_n0_physical_profile()
    second = build_default_n0_physical_profile()

    assert first.profile_hash == second.profile_hash
    assert first.canonical_json == second.canonical_json


def test_canonical_json_normalizes_tuple_list_representation():
    tuple_form = {
        "a": (1, 2, 3),
        "nested": {
            "b": ("x", "y"),
        },
    }

    list_form = {
        "a": [1, 2, 3],
        "nested": {
            "b": ["x", "y"],
        },
    }

    assert (
        canonical_json_value(tuple_form)
        == canonical_json_value(list_form)
    )
