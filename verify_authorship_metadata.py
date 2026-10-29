"""Check own-project creator roles without changing third-party bibliographies."""
from pathlib import Path
import ast
import json
import re
import sys
import tomllib
import yaml

PERSON = {"family-names": "Daghbouche", "given-names": "Karim",
          "affiliation": "GridSAT Stiftung",
          "orcid": "https://orcid.org/0000-0002-4351-2861"}
ORCID = "0000-0002-4351-2861"
CONCEPT = "10.5281/zenodo.22045318"
DOIS = {"0.6.0": "10.5281/zenodo.22045319", "0.7.0": "10.5281/zenodo.23652408"}


def organization(item):
    if isinstance(item, dict):
        if item.get("@type", item.get("type")) == "Organization":
            return True
        item = item.get("name", "")
    return re.sub("[^a-z0-9]", "", str(item).lower()) in {
        "gridsat", "gridsatstiftung", "gridsatfoundation"}


def audit(root):
    root = Path(root)
    errors = []
    cff = yaml.safe_load((root / "CITATION.cff").read_text())
    if cff.get("authors") != [PERSON]:
        errors.append("CFF sole-author/ORCID policy")
    version = str(cff.get("version", "")).removeprefix("v")
    doi = cff.get("doi")
    if version in DOIS and doi != DOIS[version]:
        errors.append("Wrong version-specific DOI")
    if doi == CONCEPT or (doi in DOIS.values() and doi != DOIS.get(version)):
        errors.append("Concept/foreign version DOI used as version DOI")
    if any(x.get("type") == "doi" and x.get("value") != CONCEPT
           for x in cff.get("identifiers", [])):
        errors.append("Wrong series DOI")
    zen = json.loads((root / ".zenodo.json").read_text())
    expected = [{"name": "Daghbouche, Karim", "orcid": ORCID,
                 "affiliation": "GridSAT Stiftung"}]
    if zen.get("creators") != expected:
        errors.append("Zenodo individual creator/ORCID policy")
    if zen.get("contributors") != [{"name": "GridSAT Stiftung", "type": "Sponsor"}]:
        errors.append("Zenodo Sponsor policy")
    if any(key in zen for key in ("doi", "version", "publication_date")):
        errors.append("Do not pin future releases to old identifiers/dates")
    # Only the project's own metadata surfaces are author declarations.
    # Copyright, affiliation, sponsor fields and bibliographies are not.
    p = root / "codemeta.json"
    if p.exists():
        data = json.loads(p.read_text())
        for key in ("author", "creator"):
            entries = data.get(key, [])
            if not isinstance(entries, list):
                entries = [entries]
            if any(organization(x) for x in entries):
                errors.append("Organization in codemeta author/creator")
    p = root / "pyproject.toml"
    if p.exists():
        data = tomllib.loads(p.read_text()).get("project", {})
        if any(organization(x) for x in data.get("authors", [])):
            errors.append("Organization in pyproject authors")
    p = root / "setup.py"
    if p.exists():
        for n in ast.walk(ast.parse(p.read_text())):
            if isinstance(n, ast.keyword) and n.arg == "author":
                if isinstance(n.value, ast.Constant) and organization(n.value.value):
                    errors.append("Organization in setup author")
    return errors


if __name__ == "__main__":
    errors = audit(Path(__file__).resolve().parent)
    print(json.dumps({"passed": not errors, "errors": errors}, indent=2))
    sys.exit(bool(errors))
