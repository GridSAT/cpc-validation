"""E3 calibrated bounded-error wrapper over the frozen P4 POINT reconstruction."""
from __future__ import annotations

from src.dyadic_phase_p4 import reconstruct
from src.dyadic_phase_p4_types import identity, parse_phase


def build_e3_registry(plan, *, calibration_primary_sha256,
                      calibration_independent_sha256,
                      ledger_sha256, authorization_sha256):
    registry = {
        "schema": "cpc-shor-ms-dp-p-e3-calibrated-registry/1",
        "run_identity": plan["run_identity"],
        "decoder": "POINT",
        "k": 4,
        "fixtures": [
            {"fixture_id": f["fixture_id"], "N": f["N"], "a": f["a"]}
            for f in plan["fixtures"]
        ],
        "phase_classes": plan["calibration"]["phase_classes"],
        "per_phase_class_n": 1024,
        "per_phase_class_max_errors": 0,
        "local_error_boundary": [1, 140],
        "conditional_beta": [[1, 20]] * 4,
        "exception": {
            "event": "false admission of at least one phase-class calibration cell",
            "bound": [1, 100],
        },
        "wrong_acceptance_bound": [21, 100],
        "risk_type":
            "unconditional_wrong_acceptance_per_bundle_over_calibration_and_evaluation",
        "conditioning_event":
            "all eight preregistered phase-class calibration cells pass in primary and independent reductions",
        "assumptions": [
            "sealed finite DP-S equality-in-law simulator and matched-reference estimator",
            "within-phase-class iid diagnostic acquisitions",
            "same exact local phase implies same local finite instrument under the sealed ideal model",
            "fresh operational preparations and innovations independent of calibration",
            "operational local phase laws are among the eight calibrated phase classes",
            "seven-channel union allocation p_local<=1/140",
            "four fresh phase estimates per bundle",
            "correct frozen POINT arithmetic and provenance",
            "no data-selected estimator, schedule, threshold, retry, replacement, or reseeding",
        ],
        "calibration_primary_sha256": calibration_primary_sha256,
        "calibration_independent_sha256": calibration_independent_sha256,
        "ledger_sha256": ledger_sha256,
        "authorization_sha256": authorization_sha256,
        "calibration_amendment_sha256":
            plan["parents"]["calibration_amendment_sha256"],
    }
    registry["identity"] = identity("ms-dp-p-e3-calibrated-registry", registry)
    return registry


def validate_e3_registry(registry, expected_identity, *, N, a,
                         acquisition_id, trials):
    unsigned = {k: v for k, v in registry.items() if k != "identity"}
    if (registry.get("identity") != expected_identity or
            identity("ms-dp-p-e3-calibrated-registry", unsigned) != expected_identity):
        raise ValueError("E3 calibrated registry identity")
    if registry.get("schema") != "cpc-shor-ms-dp-p-e3-calibrated-registry/1":
        raise ValueError("E3 calibrated registry schema")
    if registry.get("decoder") != "POINT" or registry.get("k") != 4 or trials != 4:
        raise ValueError("E3 calibrated registry domain")
    if registry.get("conditional_beta") != [[1, 20]] * 4:
        raise ValueError("E3 conditional beta")
    if registry.get("wrong_acceptance_bound") != [21, 100]:
        raise ValueError("E3 wrong-acceptance bound")
    if registry.get("exception") != {
        "event": "false admission of at least one phase-class calibration cell",
        "bound": [1, 100],
    }:
        raise ValueError("E3 calibration exception")
    admitted = [
        f for f in registry["fixtures"]
        if (f["N"], f["a"]) == (N, a)
        and acquisition_id == registry["run_identity"] + "/" + f["fixture_id"]
    ]
    if len(admitted) != 1:
        raise ValueError("E3 calibrated population mismatch")
    return registry


def reconstruct_calibrated_e3(N, a, payloads, *, policy, input_binding,
                              expected_binding_identity, registry,
                              expected_registry_identity):
    result = reconstruct(
        N, a, payloads,
        decoder="POINT",
        claim_type="P4-BE",
        policy=policy,
        input_binding=input_binding,
        expected_binding_identity=expected_binding_identity,
        error_contract=None,
        expected_contract_identity=None,
        proof_registry=None,
        expected_registry_identity=None,
    )
    if result.get("status") != "UNVERIFIED_CANDIDATE" or registry is None:
        return result

    views = [parse_phase(p, policy) for p in payloads]
    validate_e3_registry(
        registry, expected_registry_identity,
        N=N, a=a, acquisition_id=views[0].acquisition_id,
        trials=len(views),
    )
    R = result.get("candidate_R")
    if type(R) is not int or not 1 <= R < N or pow(a, R, N) != 1:
        return result

    result = dict(result)
    result.pop("identity", None)
    result.pop("reason", None)
    result.update(
        status="CERTIFIED_BOUNDED_ERROR_ORDER",
        accepted=True,
        risk_type=registry["risk_type"],
        wrong_acceptance_bound=registry["wrong_acceptance_bound"],
        calibrated_registry_identity=expected_registry_identity,
        conditional_beta=registry["conditional_beta"],
        calibration_exception=registry["exception"],
        conditioning_event=registry["conditioning_event"],
        validity_assumptions=registry["assumptions"],
        conditional_accepted_output_error_bound=None,
        modular_residue=1,
        factorization_required=False,
    )
    result["identity"] = identity("reconstruction-result", result)
    return result
