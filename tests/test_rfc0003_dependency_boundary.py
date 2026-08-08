from __future__ import annotations

import ast
from pathlib import Path

import pytest


CANONICAL_BACKEND_MODULES = (
    Path("src/backend.py"),
    Path("src/compile_backend.py"),
    Path("src/backends/rc_ccir.py"),
    Path("src/backends/rc_prepare.py"),
)

FORBIDDEN_DEPENDENCIES = frozenset(
    {
        "src.ir",
        "src.ir_compiler",
        "src.compiler",
        "src.generic_reference",
        "src.ccir_reference",
        "src.cnf_semantics",
    }
)


def _imports(path: Path) -> tuple[str, ...]:
    tree = ast.parse(
        path.read_text(encoding="utf-8"),
        filename=str(path),
    )

    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                imports.append(
                    node.module
                )

    return tuple(imports)


def _matches_forbidden_dependency(
    imported: str,
    forbidden: str,
) -> bool:
    return (
        imported == forbidden
        or imported.startswith(
            forbidden + "."
        )
    )


@pytest.mark.parametrize(
    "path",
    CANONICAL_BACKEND_MODULES,
    ids=lambda path: str(path),
)
def test_canonical_backend_modules_do_not_import_forbidden_dependencies(
    path: Path,
) -> None:
    imported_modules = _imports(
        path
    )

    violations = sorted(
        {
            imported
            for imported in imported_modules
            for forbidden in FORBIDDEN_DEPENDENCIES
            if _matches_forbidden_dependency(
                imported,
                forbidden,
            )
        }
    )

    assert violations == []


def test_compile_backend_imports_only_canonical_ccir_backend_contract() -> None:
    imports = set(
        _imports(
            Path(
                "src/compile_backend.py"
            )
        )
    )

    assert "src.backend" in imports
    assert "src.ccir" in imports

    assert "src.ir" not in imports
    assert "src.ir_compiler" not in imports
    assert "src.compiler" not in imports


def test_native_rc_compiler_has_no_reference_evaluator_dependency() -> None:
    imports = set(
        _imports(
            Path(
                "src/backends/rc_ccir.py"
            )
        )
    )

    assert "src.generic_reference" not in imports
    assert "src.ccir_reference" not in imports
    assert "src.cnf_semantics" not in imports


def test_rc_preparation_has_no_reference_evaluator_dependency() -> None:
    imports = set(
        _imports(
            Path(
                "src/backends/rc_prepare.py"
            )
        )
    )

    assert "src.generic_reference" not in imports
    assert "src.ccir_reference" not in imports
    assert "src.cnf_semantics" not in imports


def test_rc_preparation_does_not_depend_on_source_language_model() -> None:
    imports = set(
        _imports(
            Path(
                "src/backends/rc_prepare.py"
            )
        )
    )

    assert "src.compiler" not in imports
    assert "src.ir" not in imports
    assert "src.ir_compiler" not in imports
