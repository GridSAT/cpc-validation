"""Fail-closed source/authorization identities for deterministic P4 artifacts."""
import json
from pathlib import Path
from src.dyadic_phase_p4_types import digest_bytes, fields
from src.dyadic_phase_p3_provenance import verify_manifest


def verify_source_seal(path, expected_sha256):
    path=Path(path);raw=path.read_bytes()
    if digest_bytes(raw)!=expected_sha256:raise ValueError('P4 source seal identity')
    seal=json.loads(raw)
    if seal.get('schema')!='cpc-shor-p4-source-seal/1' or not seal.get('sources'):
        raise ValueError('P4 source seal schema')
    for name,h in seal['sources'].items():
        if digest_bytes(Path(name).read_bytes())!=h:raise ValueError('sealed source changed: '+name)
    dep=Path(seal['dependency_manifest'])
    verify_manifest(dep,seal['dependency_manifest_sha256'])
    return seal


def verify_execution_authorization(path, *, acceptance_sha256, source_seal_sha256,
                                   dependency_manifest_sha256):
    if path is None or not Path(path).is_file():
        raise PermissionError('stochastic P4 execution is not authorized')
    receipt=json.loads(Path(path).read_text())
    fields(receipt,(
        'schema',
        'explicit_human_execution_GO',
        'acceptance_sha256',
        'source_seal_sha256',
        'dependency_manifest_sha256',
        'review_reference',
    ))
    if (receipt['schema']!='cpc-shor-p4-execution-authorization/2'
            or receipt['explicit_human_execution_GO'] is not True):
        raise PermissionError('explicit later human execution GO required')
    if (receipt['acceptance_sha256']!=acceptance_sha256
            or receipt['source_seal_sha256']!=source_seal_sha256
            or receipt['dependency_manifest_sha256']!=dependency_manifest_sha256
            or not isinstance(receipt['review_reference'],str)
            or not receipt['review_reference'].strip()):
        raise PermissionError('authorization does not bind frozen P4 execution')
    return receipt
