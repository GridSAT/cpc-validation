"""Sole-author metadata, DOI separation and sponsorship negative controls."""
from pathlib import Path
import json
import pytest
import yaml
from verify_authorship_metadata import PERSON, ORCID, audit


@pytest.fixture
def metadata(tmp_path):
    cff = {"authors": [dict(PERSON)], "version": "0.7.0",
           "doi": "10.5281/zenodo.23652408"}
    zen = {"creators": [{"name": "Daghbouche, Karim", "orcid": ORCID,
                        "affiliation": "GridSAT Stiftung"}],
           "contributors": [{"name": "GridSAT Stiftung", "type": "Sponsor"}]}
    (tmp_path / "CITATION.cff").write_text(yaml.safe_dump(cff))
    (tmp_path / ".zenodo.json").write_text(json.dumps(zen))
    assert audit(tmp_path) == []
    return tmp_path


def test_actual_project():
    assert audit(Path(__file__).resolve().parents[1]) == []


@pytest.mark.parametrize("change", ["org", "extra_org", "no_orcid", "bad_orcid", "old_doi", "concept"])
def test_reject_cff_tampering(metadata, change):
    p = metadata / "CITATION.cff"
    x = yaml.safe_load(p.read_text())
    if change == "org":
        x["authors"] = [{"name": "GridSAT Stiftung"}]
    elif change == "extra_org":
        x["authors"].append({"name": "GridSAT Stiftung"})
    elif change == "no_orcid":
        del x["authors"][0]["orcid"]
    elif change == "bad_orcid":
        x["authors"][0]["orcid"] = "https://orcid.org/0000-0000-0000-0000"
    elif change == "old_doi":
        x["doi"] = "10.5281/zenodo.22045319"
    else:
        x["doi"] = "10.5281/zenodo.22045318"
    p.write_text(yaml.safe_dump(x))
    assert audit(metadata)


@pytest.mark.parametrize("change", ["org", "extra_org", "no_orcid", "role", "doi", "version"])
def test_reject_zenodo_tampering(metadata, change):
    p = metadata / ".zenodo.json"
    x = json.loads(p.read_text())
    if change == "org":
        x["creators"] = [{"name": "GridSAT Stiftung"}]
    elif change == "extra_org":
        x["creators"].append({"name": "GridSAT Stiftung"})
    elif change == "no_orcid":
        del x["creators"][0]["orcid"]
    elif change == "role":
        x["contributors"][0]["type"] = "Author"
    else:
        x[change] = "10.5281/zenodo.23652408" if change == "doi" else "0.7.0"
    p.write_text(json.dumps(x))
    assert audit(metadata)


@pytest.mark.parametrize("name", ["GridSAT", "GridSAT Stiftung", "GridSAT Foundation"])
def test_reject_codemeta_organization(metadata, name):
    (metadata / "codemeta.json").write_text(json.dumps({"author": [{"name": name}]}))
    assert audit(metadata)


def test_allow_contributor_copyright_and_third_party_reference(metadata):
    (metadata / "LICENSE").write_text("Copyright GridSAT Stiftung and contributors")
    (metadata / "references.bib").write_text("@misc{other, author={GridSAT Stiftung}}")
    (metadata / "codemeta.json").write_text(json.dumps({
        "author": [{"@type": "Person", "name": "Karim Daghbouche"}],
        "contributor": [{"@type": "Organization", "name": "GridSAT Stiftung"}]}))
    assert audit(metadata) == []
