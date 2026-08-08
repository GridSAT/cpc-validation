"""
Execution backends for CPC intermediate-representation programs.
"""

from src.backends.rc import (
    RCBackendResult,
    compile_ir_to_rc,
)

__all__ = [
    "RCBackendResult",
    "compile_ir_to_rc",
]
