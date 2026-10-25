"""Preserve frozen Markdown bytes and narrowly scope hard-break whitespace policy."""
from pathlib import Path
import hashlib
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
PINS = {'docs/DYADIC-PHASE-MS-DP-P-E1A-BOUND.md': ('ac5f924e3532022216523571fbb83b3dda983433976ed3fc9b90c6927a79de61', 5), 'docs/DYADIC-PHASE-MS-DP-P-E2.md': ('9b8b6850c64cdb8a502201b1fde7174ef80e85369e17052c2ca43acfe66fec87', 5), 'docs/DYADIC-PHASE-MS-DP-P-E3-CALIBRATION-AMENDMENT-V2.md': ('ef1d0e08155789894a848bd16c80d53ffdc5419841aefc712fd5b77127e39753', 5), 'docs/DYADIC-PHASE-MS-DP-P-E3-DESIGN.md': ('2ea4e318e73d2722af38772078cf9c06fdcccad24615e99119a32097a3739b8c', 7), 'docs/DYADIC-PHASE-MS-DP-P-E3-IA.md': ('5e649929604e7cf761c557fc499826df30280ecc87eefdc812b4eb0dca402d9f', 3), 'docs/DYADIC-PHASE-MS-DP-P-E3-IB.md': ('4df557a9aaa7d3f2c6653f0a2a60e0824c2a4e0a3926c639b26808edf793301d', 4), 'docs/DYADIC-PHASE-MS-DP-P-FROZEN-SPEC.md': ('6661974d58f2a0959ad4d8185c925e993f2d9619bac830b414fef96533ffb88b', 5)}
BASE_ATTRIBUTES = '# Immutable public evidence retains exact bytes on every checkout.\nevidence/shor/up5k-physical-v6/** -text\n# Captured CRLF streams are byte artifacts rather than editable prose.\nevidence/shor/up5k-physical-v6/transcripts/*.txt -diff\n'
EXPECTED_ATTRIBUTES = BASE_ATTRIBUTES + "\n# Preserve reviewed hard breaks in these SHA-pinned frozen documents only.\n" + "".join(
    path + " whitespace=-blank-at-eol\n" for path in PINS
)


def hard_break_count(data):
    trailing = [line for line in data.splitlines() if line.rstrip(b" \t") != line]
    assert all(line.endswith(b"  ") and not line.endswith(b"   ")
               and line[:-2].rstrip(b" \t") == line[:-2]
               and line[:-2] for line in trailing), "Non-hard-break trailing whitespace"
    return len(trailing)


def verify_frozen_policy(root):
    attributes = sorted(p.relative_to(root).as_posix()
                        for p in root.rglob(".gitattributes")
                        if ".git" not in p.relative_to(root).parts
                        and ".venv" not in p.relative_to(root).parts)
    assert attributes == [".gitattributes"], "Unexpected nested attribute policy"
    assert (root / ".gitattributes").read_bytes() == EXPECTED_ATTRIBUTES.encode(), "Broadened or altered exemption"
    for path, (digest, count) in PINS.items():
        data = (root / path).read_bytes()
        assert hard_break_count(data) == count, "Hard-break count changed"
        assert hashlib.sha256(data).hexdigest() == digest, "Frozen document changed"
    assert sum(count for _, count in PINS.values()) == 34


def test_frozen_document_hashes_and_scoped_policy():
    verify_frozen_policy(ROOT)


def test_git_effective_whitespace_attributes():
    paths = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    result = subprocess.check_output(
        ["git", "check-attr", "-z", "--stdin", "whitespace"], cwd=ROOT, input=paths
    ).decode().split("\0")[:-1]
    assert len(result) % 3 == 0
    for path, attribute, value in zip(result[::3], result[1::3], result[2::3]):
        assert attribute == "whitespace"
        assert value == ("-blank-at-eol" if path in PINS else "unspecified")


@pytest.fixture
def snapshot(tmp_path):
    (tmp_path / ".gitattributes").write_text(EXPECTED_ATTRIBUTES)
    for path in PINS:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / path).read_bytes())
    verify_frozen_policy(tmp_path)
    return tmp_path


@pytest.mark.parametrize("rule", [
    "*.md whitespace=-blank-at-eol",
    "docs/** whitespace=-blank-at-eol",
    "docs/DYADIC-PHASE* whitespace=-blank-at-eol",
    "* -whitespace",
    "* whitespace=-blank-at-eol,-space-before-tab",
    "README.md whitespace=-blank-at-eol",
])
def test_reject_added_broad_or_unrelated_exemption(snapshot, rule):
    with (snapshot / ".gitattributes").open("a") as stream:
        stream.write(rule + "\n")
    with pytest.raises(AssertionError, match="exemption"):
        verify_frozen_policy(snapshot)


@pytest.mark.parametrize("replacement", ["-whitespace", "whitespace=-blank-at-eol,-space-before-tab", "whitespace", "!whitespace"])
def test_reject_weaker_exact_path_rules(snapshot, replacement):
    path = snapshot / ".gitattributes"
    path.write_text(path.read_text().replace("whitespace=-blank-at-eol", replacement, 1))
    with pytest.raises(AssertionError, match="exemption"):
        verify_frozen_policy(snapshot)


def test_reject_nested_override(snapshot):
    (snapshot / "docs/.gitattributes").write_text("* -whitespace\n")
    with pytest.raises(AssertionError, match="nested"):
        verify_frozen_policy(snapshot)


@pytest.mark.parametrize("path", list(PINS))
def test_reject_frozen_content_tampering(snapshot, path):
    target = snapshot / path
    target.write_bytes(target.read_bytes() + b"tampered\n")
    with pytest.raises(AssertionError, match="Frozen document changed"):
        verify_frozen_policy(snapshot)


@pytest.mark.parametrize("change", ["remove", "add", "three_spaces", "tab"])
def test_reject_hard_break_tampering(snapshot, change):
    target = snapshot / next(iter(PINS))
    data = target.read_bytes()
    if change == "remove":
        data = data.replace(b"  \n", b"\n", 1)
    elif change == "add":
        data += b"new hard break  \n"
    elif change == "three_spaces":
        data = data.replace(b"  \n", b"   \n", 1)
    else:
        data = data.replace(b"  \n", b"\t\n", 1)
    target.write_bytes(data)
    with pytest.raises(AssertionError):
        verify_frozen_policy(snapshot)


@pytest.mark.parametrize("path, content, expected", [
    (next(iter(PINS)), b"valid hard break  \n", 0),
    ("unrelated.md", b"unrelated trailing spaces  \n", 2),
    (next(iter(PINS)), b" \tspace before tab\n", 2),
    (next(iter(PINS)), b"extra blank line\n\n", 2),
])
def test_git_enforces_remaining_whitespace_checks(tmp_path, path, content, expected):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitattributes").write_text(EXPECTED_ATTRIBUTES)
    target = tmp_path / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    result = subprocess.run(
        ["git", "-c", "core.whitespace=blank-at-eol,blank-at-eof,space-before-tab",
         "diff", "--cached", "--check"],
        cwd=tmp_path, capture_output=True,
    )
    assert result.returncode == expected, result.stdout + result.stderr
