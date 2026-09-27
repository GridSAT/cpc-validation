from __future__ import annotations

from dataclasses import dataclass

from src.open_system_conformance import (
    RFC0010_REQUIREMENTS,
)


N0_RFC0010_MAPPING_SCHEMA = (
    "cpc.shor.n0.rfc0010-mapping.v1"
)

N0_SCOPE_STATUSES = (
    "DEFERRED_FULL_SEMANTIC_DYNAMICS",
    "IN_SCOPE",
    "NOT_APPLICABLE_N0",
)

N0_EVIDENCE_STATUSES = (
    "NOT_EXERCISED",
    "SYNTHETICALLY_EXERCISED",
)


RFC0010_TITLES = {
    "OS-1": "Stabilization/problem-generator separation",
    "OS-2": "Protected-manifold identity",
    "OS-3": "Uniform instance-dependent generator synthesis",
    "OS-4": "Answer-independent generator construction",
    "OS-5": "Protected correction-family declaration",
    "OS-6": "Terminal-silence evidence",
    "OS-7": "Dark-vector-sector evidence when claimed",
    "OS-8": "Fixed-point-set evidence for Level-II claims",
    "DC-1": "Declared semantic penalty observable",
    "DC-2": "Positive penalty-scale evidence when used",
    "DC-3": "Penalty-Lyapunov evidence when claimed",
    "DC-4": "Convergence-rate evidence",
    "DC-5": "Leakage accounting",
    "DC-6": "Runtime and resource accounting",
    "RR-1": "External-reference identity when required",
    "RR-2": "Reference calibration record",
    "RR-3": "Calibration-neighborhood specification",
    "RR-4": "Referenced measurement model",
    "RR-5": "Decision-region specification",
    "RR-6": "Fixed decoder",
    "RR-7": "Robust separation evidence",
    "RR-8": "Declared measurement-error bound",
    "OV-1": "ObservableExecution contains only admitted observations",
    "OV-2": "Semantic validation remains outside backend dependency graph",
    "OV-3": "Physical evidence remains distinct from semantic correctness",
    "OV-4": "Exact versus approximate realization status is explicit",
}


@dataclass(frozen=True)
class N0RFC0010RequirementMapping:
    requirement_id: str
    title: str

    n0_scope: str
    current_evidence_status: str

    physical_evidence_required_for_physical_claim: bool

    rationale: str

    def __post_init__(self) -> None:
        if self.requirement_id not in RFC0010_REQUIREMENTS:
            raise ValueError(
                "unknown RFC-0010 requirement"
            )

        expected_title = RFC0010_TITLES[
            self.requirement_id
        ]

        if self.title != expected_title:
            raise ValueError(
                "requirement title does not match RFC-0010"
            )

        if self.n0_scope not in N0_SCOPE_STATUSES:
            raise ValueError(
                "unknown N0 scope status"
            )

        if (
            self.current_evidence_status
            not in N0_EVIDENCE_STATUSES
        ):
            raise ValueError(
                "unknown N0 evidence status"
            )

        if (
            self.n0_scope == "NOT_APPLICABLE_N0"
            and self.current_evidence_status
            != "NOT_EXERCISED"
        ):
            raise ValueError(
                "not-applicable requirement cannot be "
                "reported as exercised"
            )

        if (
            self.n0_scope
            == "DEFERRED_FULL_SEMANTIC_DYNAMICS"
            and self.current_evidence_status
            != "NOT_EXERCISED"
        ):
            raise ValueError(
                "deferred semantic requirement cannot be "
                "reported as exercised by restricted N0"
            )

        if not isinstance(
            self.physical_evidence_required_for_physical_claim,
            bool,
        ):
            raise ValueError(
                "physical evidence flag must be boolean"
            )

        if (
            not isinstance(self.rationale, str)
            or not self.rationale
        ):
            raise ValueError(
                "rationale must be non-empty"
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "requirement_id": self.requirement_id,
            "title": self.title,
            "n0_scope": self.n0_scope,
            "current_evidence_status": (
                self.current_evidence_status
            ),
            "physical_evidence_required_for_physical_claim": (
                self.physical_evidence_required_for_physical_claim
            ),
            "rationale": self.rationale,
        }


def _entry(
    requirement_id: str,
    *,
    n0_scope: str,
    evidence: str,
    physical: bool,
    rationale: str,
) -> N0RFC0010RequirementMapping:
    return N0RFC0010RequirementMapping(
        requirement_id=requirement_id,
        title=RFC0010_TITLES[
            requirement_id
        ],
        n0_scope=n0_scope,
        current_evidence_status=evidence,
        physical_evidence_required_for_physical_claim=physical,
        rationale=rationale,
    )


def build_n0_rfc0010_mapping(
) -> tuple[
    N0RFC0010RequirementMapping,
    ...
]:
    """
    Restricted N0 measurement-profile mapping.

    This mapping deliberately does not claim complete RFC-0010 Level-II
    semantic CPC conformance.
    """

    entries = (
        _entry(
            "OS-1",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "N0 keeps stabilization dynamics distinct from the "
                "measurement/probe dynamics; physical realization remains "
                "unverified."
            ),
        ),
        _entry(
            "OS-2",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "The simulated cat protected manifold is explicitly "
                "declared and leakage is diagnosed."
            ),
        ),
        _entry(
            "OS-3",
            n0_scope="DEFERRED_FULL_SEMANTIC_DYNAMICS",
            evidence="NOT_EXERCISED",
            physical=True,
            rationale=(
                "Uniform instance-dependent semantic generator synthesis "
                "belongs to full L_prob realization, not restricted N0 "
                "measurement validation."
            ),
        ),
        _entry(
            "OS-4",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "The N0 probe, calibration, decoder and acquisition APIs "
                "exclude expected answers and truth inputs."
            ),
        ),
        _entry(
            "OS-5",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "The simulated protected bosonic carrier and stabilization "
                "family are declared, but no physical correction-family "
                "evidence exists."
            ),
        ),
        _entry(
            "OS-6",
            n0_scope="NOT_APPLICABLE_N0",
            evidence="NOT_EXERCISED",
            physical=False,
            rationale=(
                "Restricted N0 phase measurement does not claim a semantic "
                "terminal-silence property."
            ),
        ),
        _entry(
            "OS-7",
            n0_scope="NOT_APPLICABLE_N0",
            evidence="NOT_EXERCISED",
            physical=False,
            rationale=(
                "N0 makes no dark-vector-sector claim."
            ),
        ),
        _entry(
            "OS-8",
            n0_scope="DEFERRED_FULL_SEMANTIC_DYNAMICS",
            evidence="NOT_EXERCISED",
            physical=True,
            rationale=(
                "Fixed-point-set evidence is required for the stronger "
                "Level-II semantic claim and is not established by N0."
            ),
        ),
        _entry(
            "DC-1",
            n0_scope="NOT_APPLICABLE_N0",
            evidence="NOT_EXERCISED",
            physical=False,
            rationale=(
                "N0 does not define a semantic penalty observable."
            ),
        ),
        _entry(
            "DC-2",
            n0_scope="NOT_APPLICABLE_N0",
            evidence="NOT_EXERCISED",
            physical=False,
            rationale=(
                "No N0 semantic penalty scale is claimed."
            ),
        ),
        _entry(
            "DC-3",
            n0_scope="NOT_APPLICABLE_N0",
            evidence="NOT_EXERCISED",
            physical=False,
            rationale=(
                "No N0 penalty-Lyapunov semantic convergence claim is made."
            ),
        ),
        _entry(
            "DC-4",
            n0_scope="DEFERRED_FULL_SEMANTIC_DYNAMICS",
            evidence="NOT_EXERCISED",
            physical=True,
            rationale=(
                "Semantic convergence-rate evidence belongs to the stronger "
                "full driven-dissipative computation profile."
            ),
        ),
        _entry(
            "DC-5",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "Protected-manifold leakage is explicitly computed in the "
                "finite bosonic model; physical leakage remains unmeasured."
            ),
        ),
        _entry(
            "DC-6",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "Simulation runtime/sample accounting is available; "
                "physical runtime and apparatus resources remain absent."
            ),
        ),
        _entry(
            "RR-1",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "The N0 record carries an explicit external-reference "
                "identity."
            ),
        ),
        _entry(
            "RR-2",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "A simulated reference calibration object exists; "
                "physical calibration evidence is still required."
            ),
        ),
        _entry(
            "RR-3",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "Calibration structure and uncertainty fields exist, but "
                "physical numeric neighborhoods remain unresolved."
            ),
        ),
        _entry(
            "RR-4",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "A referenced stochastic measurement model and common raw "
                "record schema are implemented synthetically."
            ),
        ),
        _entry(
            "RR-5",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "Decision/inference behavior is fixed in software before "
                "truth reveal; physical decision regions remain to be "
                "preregistered."
            ),
        ),
        _entry(
            "RR-6",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "The reducer identity and truth-blind inference API are "
                "fixed."
            ),
        ),
        _entry(
            "RR-7",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "Synthetic perturbation/fault sensitivity is exercised, "
                "but no physical robust-separation bound is claimed."
            ),
        ),
        _entry(
            "RR-8",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "The statistical contract supports an error bound, but the "
                "physical bound is intentionally unresolved."
            ),
        ),
        _entry(
            "OV-1",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "N0RawRecord contains admitted signal/reference and quality "
                "fields and explicitly excludes truth fields."
            ),
        ),
        _entry(
            "OV-2",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "Truth is revealed only after blind reduction and is not "
                "part of the reducer dependency graph."
            ),
        ),
        _entry(
            "OV-3",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "Simulation result, semantic comparison and physical "
                "evidence status are represented separately."
            ),
        ),
        _entry(
            "OV-4",
            n0_scope="IN_SCOPE",
            evidence="SYNTHETICALLY_EXERCISED",
            physical=True,
            rationale=(
                "The profile is hard-coded to realization_status=simulated "
                "and cannot promote itself to a physical status."
            ),
        ),
    )

    by_id = {
        item.requirement_id:
        item
        for item in entries
    }

    if set(by_id) != set(
        RFC0010_REQUIREMENTS
    ):
        raise RuntimeError(
            "N0 RFC-0010 mapping is incomplete"
        )

    if len(entries) != len(
        RFC0010_REQUIREMENTS
    ):
        raise RuntimeError(
            "N0 RFC-0010 mapping contains duplicate requirements"
        )

    return tuple(
        sorted(
            entries,
            key=lambda item: item.requirement_id,
        )
    )
