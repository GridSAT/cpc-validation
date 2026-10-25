"""Tampering checks for the public, read-only transcript verifier."""
import json
import shutil

import pytest

import verify_up5k_physical_evidence as audit


def transcript(record=2):
    return (audit.ROOT / f"transcripts/record-{record}.txt").read_bytes()


def fixture(record=2):
    return (audit.ROOT / f"fixtures/record-{record}.json").read_bytes()


def test_published_subset():
    result = audit.verify_all()
    assert result["verified_response_words"] == 132
    assert result["verified_snapshot_hashes"] == 18
    assert result["quantum_qualification"] == "NOT_ESTABLISHED"


@pytest.mark.parametrize("record", [2, 68, 194])
def test_exact_oracle_frames(record):
    result = audit.verify_transcript(record, transcript(record), fixture(record))
    assert result["PROB"]["response_words"] == 38


@pytest.mark.parametrize(("before", "after"), [
    (b"0000,C658", b"0000,C659"),                 # response CRC
    (b"61C8,DE34", b"61C8,DE35"),                 # request CRC
    (b"raw=00005A01", b"raw=00005A00"),           # FIFO acquisition
    (b"shadow=5A01", b"shadow=5A00"),             # independent shadow
    (b"slot=0 count=4", b"slot=1 count=4"),       # duplicate snapshot slot
    (b"response_fnv=290571C2", b"response_fnv=290571C3"),
    (b"protocol=0", b"protocol=3"),
    (b"error_pin=0", b"error_pin=1"),
    (b"OK PROB sequence=2", b"OK PROB sequence=3"),
    (b"session_consumed=1", b"session_consumed=0"),
    (b"data_dir=input", b"data_dir=output"),
    (b"pico_oe=0", b"pico_oe=1"),
    (b"overflow=0", b"overflow=1"),
    (b"phase=1", b"phase=0"),
])
def test_rejects_corruption(before, after):
    raw = transcript()
    assert before in raw
    with pytest.raises(ValueError):
        audit.verify_transcript(2, raw.replace(before, after, 1), fixture())


@pytest.mark.parametrize("mutation", [
    lambda raw: b"\n".join(raw.splitlines()[:-1]),
    lambda raw: raw + b"unexpected private metadata\n",
    lambda raw: raw.replace(b"OK SEED sequence=1", b"OK SEED sequence=1\nOK SEED sequence=1", 1),
])
def test_rejects_missing_duplicate_or_unexpected_lines(mutation):
    with pytest.raises((ValueError, IndexError)):
        audit.verify_transcript(2, mutation(transcript()), fixture())


def test_fixture_crc_is_independently_checked():
    data = json.loads(fixture())
    data["SEED"]["request"][-1] = "0000"
    with pytest.raises(ValueError, match="ORACLE_REFERENCE_CRC"):
        audit.verify_transcript(2, transcript(), json.dumps(data).encode())


@pytest.mark.parametrize("case", ["changed", "extra", "missing"])
def test_manifest_rejects_file_changes(tmp_path, case):
    dest = tmp_path / "evidence"
    shutil.copytree(audit.ROOT, dest)
    target = dest / "transcripts/record-2.txt"
    if case == "changed":
        target.write_bytes(target.read_bytes() + b"\n")
    elif case == "extra":
        (dest / "unexpected.txt").write_text("extra")
    else:
        target.unlink()
    with pytest.raises(ValueError, match="MANIFEST"):
        audit.verify_all(dest)
