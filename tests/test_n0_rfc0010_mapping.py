from src.n0_rfc0010_mapping import (
    build_n0_rfc0010_mapping,
)
from src.open_system_conformance import (
    RFC0010_REQUIREMENTS,
)


def test_mapping_covers_every_rfc0010_requirement_once():
    mapping = build_n0_rfc0010_mapping()

    ids = tuple(
        item.requirement_id
        for item in mapping
    )

    assert len(
        ids
    ) == len(
        RFC0010_REQUIREMENTS
    )

    assert set(
        ids
    ) == set(
        RFC0010_REQUIREMENTS
    )

    assert len(
        set(
            ids
        )
    ) == len(
        ids
    )


def test_full_semantic_generator_synthesis_is_deferred():
    mapping = {
        item.requirement_id:
        item
        for item
        in build_n0_rfc0010_mapping()
    }

    assert (
        mapping["OS-3"].n0_scope
        == "DEFERRED_FULL_SEMANTIC_DYNAMICS"
    )

    assert (
        mapping["OS-8"].n0_scope
        == "DEFERRED_FULL_SEMANTIC_DYNAMICS"
    )

    assert (
        mapping["DC-4"].n0_scope
        == "DEFERRED_FULL_SEMANTIC_DYNAMICS"
    )


def test_semantic_penalty_requirements_are_not_claimed_by_n0():
    mapping = {
        item.requirement_id:
        item
        for item
        in build_n0_rfc0010_mapping()
    }

    for requirement_id in (
        "DC-1",
        "DC-2",
        "DC-3",
    ):
        assert (
            mapping[
                requirement_id
            ].n0_scope
            == "NOT_APPLICABLE_N0"
        )

        assert (
            mapping[
                requirement_id
            ].current_evidence_status
            == "NOT_EXERCISED"
        )


def test_readout_requirements_are_in_scope_but_synthetic():
    mapping = {
        item.requirement_id:
        item
        for item
        in build_n0_rfc0010_mapping()
    }

    for number in range(
        1,
        9,
    ):
        requirement_id = (
            f"RR-{number}"
        )

        assert (
            mapping[
                requirement_id
            ].n0_scope
            == "IN_SCOPE"
        )

        assert (
            mapping[
                requirement_id
            ].current_evidence_status
            == "SYNTHETICALLY_EXERCISED"
        )

        assert (
            mapping[
                requirement_id
            ].physical_evidence_required_for_physical_claim
            is True
        )


def test_observation_validation_boundary_is_in_scope():
    mapping = {
        item.requirement_id:
        item
        for item
        in build_n0_rfc0010_mapping()
    }

    for number in range(
        1,
        5,
    ):
        requirement_id = (
            f"OV-{number}"
        )

        assert (
            mapping[
                requirement_id
            ].n0_scope
            == "IN_SCOPE"
        )
