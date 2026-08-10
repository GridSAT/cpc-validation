from __future__ import annotations

from generate_p1_synthesis_evidence import (
    SCHEMA,
    build_report,
    content_hash,
)


def test_report_has_explicit_schema() -> None:
    report = build_report()

    assert report["schema"] == (
        "cpc.p1-synthesis-matrix.v1"
    )

    assert report["schema"] == SCHEMA


def test_report_contains_complete_boundary_matrix() -> None:
    report = build_report()

    assert report["case_count"] == 4

    cases = report["cases"]

    assert [
        case["case_id"]
        for case in cases
    ] == [
        "p1-00",
        "p1-01",
        "p1-10",
        "p1-11",
    ]

    assert [
        case["boundary_values"]
        for case in cases
    ] == [
        {"0": 0, "3": 0},
        {"0": 0, "3": 1},
        {"0": 1, "3": 0},
        {"0": 1, "3": 1},
    ]


def test_report_binds_icebreaker_target() -> None:
    target = build_report()["target"]

    assert target["target_id"] == (
        "icebreaker-up5k-sg48.v1"
    )

    assert target["backend_id"] == "fpga"
    assert target["backend_version"] == "1"
    assert target["device_family"] == "ice40up5k"
    assert target["device_part"] == "up5k-sg48"


def test_each_case_contains_synthesis_bindings() -> None:
    for case in build_report()["cases"]:
        assert case[
            "prepared_execution_hash"
        ].startswith(
            "sha256:"
        )

        assert case[
            "synthesis_source_sha256"
        ].startswith(
            "sha256:"
        )

        synthesis = case["synthesis"]

        assert synthesis["tool"] == "yosys"

        assert synthesis[
            "tool_version"
        ].startswith(
            "Yosys "
        )

        assert synthesis[
            "json_sha256"
        ].startswith(
            "sha256:"
        )

        assert synthesis["json_size"] > 0


def test_report_makes_no_later_physical_claim() -> None:
    report = build_report()

    assert report["claims"] == {
        "synthesis_complete": True,
        "place_route_complete": False,
        "bitstream_complete": False,
        "physical_programming": False,
        "physical_execution": False,
    }

    for case in report["cases"]:
        assert case["later_stages"] == {
            "place_route_complete": False,
            "bitstream_complete": False,
            "physical_programming": False,
            "physical_execution": False,
        }


def test_evidence_hash_covers_report_content() -> None:
    report = build_report()

    evidence_hash = report.pop(
        "evidence_hash"
    )

    assert evidence_hash == (
        content_hash(
            report
        )
    )


def test_report_is_deterministic() -> None:
    first = build_report()
    second = build_report()

    assert first == second
