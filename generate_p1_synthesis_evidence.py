from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.physical_fpga_synthesis_matrix import (
    synthesize_p1_matrix,
)
from src.physical_icebreaker_target import (
    ICEBREAKER_TARGET,
)


SCHEMA = "cpc.p1-synthesis-matrix.v1"

OUTPUT = Path(
    "evidence/p1/p1-synthesis-matrix.json"
)


def canonical_json(
    value: object,
) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    )


def content_hash(
    value: object,
) -> str:
    digest = hashlib.sha256(
        canonical_json(value).encode(
            "utf-8"
        )
    ).hexdigest()

    return f"sha256:{digest}"


def case_to_dict(
    case: object,
) -> dict[str, object]:
    return {
        "case_id": case.case_id,
        "boundary_values": {
            str(key): value
            for key, value in case.boundary_values
        },
        "prepared_execution_hash": (
            case.prepared_execution_hash
        ),
        "projection_id": (
            case.projection_id
        ),
        "synthesis_source_sha256": (
            case.synthesis_source_sha256
        ),
        "synthesis": {
            "tool": case.synthesis_tool,
            "tool_version": (
                case.synthesis_tool_version
            ),
            "json_sha256": (
                case.synthesized_json_sha256
            ),
            "json_size": (
                case.synthesized_json_size
            ),
        },
        "later_stages": {
            "place_route_complete": (
                case.place_route_complete
            ),
            "bitstream_complete": (
                case.bitstream_complete
            ),
            "physical_programming": (
                case.physical_programming
            ),
            "physical_execution": (
                case.physical_execution
            ),
        },
    }


def build_report() -> dict[str, object]:
    matrix = synthesize_p1_matrix()

    report: dict[str, object] = {
        "schema": SCHEMA,
        "phase": "P1",
        "status": "pre-hardware-synthesis",
        "target": {
            "target_id": (
                ICEBREAKER_TARGET.target_id
            ),
            "physical_profile_id": (
                ICEBREAKER_TARGET.physical_profile_id
            ),
            "backend_id": (
                ICEBREAKER_TARGET.backend_id
            ),
            "backend_version": (
                ICEBREAKER_TARGET.backend_version
            ),
            "board_family": (
                ICEBREAKER_TARGET.board_family
            ),
            "device_family": (
                ICEBREAKER_TARGET.device_family
            ),
            "device_part": (
                ICEBREAKER_TARGET.device_part
            ),
        },
        "case_count": len(matrix),
        "cases": [
            case_to_dict(case)
            for case in matrix
        ],
        "claims": {
            "synthesis_complete": True,
            "place_route_complete": False,
            "bitstream_complete": False,
            "physical_programming": False,
            "physical_execution": False,
        },
    }

    report["evidence_hash"] = (
        content_hash(
            report
        )
    )

    return report


def main() -> None:
    report = build_report()

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(OUTPUT)
    print(report["evidence_hash"])


if __name__ == "__main__":
    main()
