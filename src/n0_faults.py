from __future__ import annotations

from dataclasses import replace
import math

from src.n0_raw_record import (
    N0RawRecord,
    synthetic_sample_payload_hash,
)


N0_FAULT_SCHEMA = "cpc.shor.n0.faults.v1"

RECORD_FAULTS = (
    "CLIPPING",
    "DROPPED_SAMPLE",
    "PROBE_DISABLED",
    "REFERENCE_DRIFT",
    "REFERENCE_PHASE_ERROR",
    "RESET_FAILURE",
    "SIGNAL_LABEL_SWAP",
    "TIMESTAMP_DISCONTINUITY",
)


def _rehash(
    record: N0RawRecord,
    *,
    signal_i: tuple[float, ...] | None = None,
    signal_q: tuple[float, ...] | None = None,
    reference_i: tuple[float, ...] | None = None,
    reference_q: tuple[float, ...] | None = None,
) -> N0RawRecord:
    si = (
        record.signal_i
        if signal_i is None
        else signal_i
    )

    sq = (
        record.signal_q
        if signal_q is None
        else signal_q
    )

    ri = (
        record.reference_i
        if reference_i is None
        else reference_i
    )

    rq = (
        record.reference_q
        if reference_q is None
        else reference_q
    )

    return replace(
        record,
        signal_i=si,
        signal_q=sq,
        reference_i=ri,
        reference_q=rq,
        original_bytes_sha256=(
            synthetic_sample_payload_hash(
                signal_i=si,
                signal_q=sq,
                reference_i=ri,
                reference_q=rq,
            )
        ),
    )


def inject_probe_disabled(
    record: N0RawRecord,
) -> N0RawRecord:
    zeros = (
        0.0,
    ) * record.sample_count

    return _rehash(
        record,
        signal_i=zeros,
        signal_q=zeros,
    )


def inject_reference_phase_error(
    record: N0RawRecord,
    *,
    phase_error_rad: float,
) -> N0RawRecord:
    if (
        not isinstance(
            phase_error_rad,
            (int, float),
        )
        or isinstance(
            phase_error_rad,
            bool,
        )
        or not math.isfinite(
            phase_error_rad
        )
    ):
        raise ValueError(
            "phase_error_rad must be finite"
        )

    cosine = math.cos(
        phase_error_rad
    )

    sine = math.sin(
        phase_error_rad
    )

    rotated_i = tuple(
        cosine * i
        - sine * q
        for i, q in zip(
            record.reference_i,
            record.reference_q,
        )
    )

    rotated_q = tuple(
        sine * i
        + cosine * q
        for i, q in zip(
            record.reference_i,
            record.reference_q,
        )
    )

    return _rehash(
        record,
        reference_i=rotated_i,
        reference_q=rotated_q,
    )


def inject_reference_drift(
    record: N0RawRecord,
    *,
    additive_drift: float,
) -> N0RawRecord:
    if (
        not isinstance(
            additive_drift,
            (int, float),
        )
        or isinstance(
            additive_drift,
            bool,
        )
        or not math.isfinite(
            additive_drift
        )
    ):
        raise ValueError(
            "additive_drift must be finite"
        )

    shifted = tuple(
        value
        + float(additive_drift)
        for value in record.reference_i
    )

    return _rehash(
        record,
        reference_i=shifted,
    )


def inject_clipping(
    record: N0RawRecord,
    *,
    index: int = 0,
) -> N0RawRecord:
    if not (
        0
        <= index
        < record.sample_count
    ):
        raise ValueError(
            "index out of range"
        )

    flags = list(
        record.clipping_flags
    )

    flags[index] = True

    return replace(
        record,
        clipping_flags=tuple(
            flags
        ),
    )


def inject_dropped_sample(
    record: N0RawRecord,
    *,
    index: int = 0,
) -> N0RawRecord:
    if not (
        0
        <= index
        < record.sample_count
    ):
        raise ValueError(
            "index out of range"
        )

    flags = list(
        record.dropped_sample_flags
    )

    flags[index] = True

    return replace(
        record,
        dropped_sample_flags=tuple(
            flags
        ),
    )


def inject_timestamp_discontinuity(
    record: N0RawRecord,
    *,
    index: int = 0,
) -> N0RawRecord:
    if not (
        0
        <= index
        < record.sample_count
    ):
        raise ValueError(
            "index out of range"
        )

    flags = list(
        record.timestamp_discontinuity_flags
    )

    flags[index] = True

    return replace(
        record,
        timestamp_discontinuity_flags=tuple(
            flags
        ),
    )


def inject_reset_failure(
    record: N0RawRecord,
) -> N0RawRecord:
    return replace(
        record,
        reset_status="failed",
    )


def inject_signal_label_swap(
    first: N0RawRecord,
    second: N0RawRecord,
) -> tuple[N0RawRecord, N0RawRecord]:
    """
    Swap the admitted signal payloads while preserving trial/command metadata.

    This is a synthetic label-corruption negative control.
    """
    first_new = _rehash(
        first,
        signal_i=second.signal_i,
        signal_q=second.signal_q,
    )

    second_new = _rehash(
        second,
        signal_i=first.signal_i,
        signal_q=first.signal_q,
    )

    return (
        first_new,
        second_new,
    )


def fault_record(
    record: N0RawRecord,
    *,
    fault: str,
) -> N0RawRecord:
    if fault not in RECORD_FAULTS:
        raise ValueError(
            "unknown record fault"
        )

    if fault == "CLIPPING":
        return inject_clipping(
            record
        )

    if fault == "DROPPED_SAMPLE":
        return inject_dropped_sample(
            record
        )

    if fault == "PROBE_DISABLED":
        return inject_probe_disabled(
            record
        )

    if fault == "REFERENCE_DRIFT":
        return inject_reference_drift(
            record,
            additive_drift=0.25,
        )

    if fault == "REFERENCE_PHASE_ERROR":
        return inject_reference_phase_error(
            record,
            phase_error_rad=math.pi / 4.0,
        )

    if fault == "RESET_FAILURE":
        return inject_reset_failure(
            record
        )

    if fault == "TIMESTAMP_DISCONTINUITY":
        return inject_timestamp_discontinuity(
            record
        )

    if fault == "SIGNAL_LABEL_SWAP":
        raise ValueError(
            "SIGNAL_LABEL_SWAP requires two records"
        )

    raise AssertionError(
        "unreachable fault branch"
    )
