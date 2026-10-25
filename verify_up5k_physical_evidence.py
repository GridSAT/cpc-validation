"""Read-only audit of the documented public UP5K physical transcript excerpts.
Python standard library only; no hardware, network, subprocess or file writes.
Pure frame checks retained from the sealed auditor (see PROVENANCE.json).
Host-recorded provenance remains an explicit trust boundary.
"""
import hashlib
import json
from pathlib import Path
import re
import sys
ROOT = Path(__file__).resolve().parent / 'evidence/shor/up5k-physical-v6'
ORACLE = 'e501eb80a0e2b13fdd59da9bfe8c3db5fcfbf225aa20776ba25a66e5c68eb889'
MATRIX = '619cf5f93dc939452266198a7519fb2b1b9eecd246ed070d33979eaa728f779c'
UF2 = 'edb273e1b85b27ee2a51a911fc618052e39007e716b2a4d5b0faf79a62a6ba45'
FPGA = 'a9b5b1208915082cfe499b5f45ed570a6e2c886053d6f7bdfeb2e63774c04ab0'
SEQS = {2: (1, 2), 68: (3, 4), 194: (5, 6)}

def req(c, m):
    if not c:
        raise ValueError(m)

def sha(b):
    return hashlib.sha256(b).hexdigest()

def crc(words):
    c = 65535
    for w in words:
        for bit in range(15, -1, -1):
            p = c >> 15 ^ w >> bit & 1
            c = c << 1 & 65535
            if p:
                c ^= 4129
    return c

def fnv(words):
    h = 2166136261
    for w in words:
        for b in (w & 255, w >> 8 & 255):
            h = (h ^ b) * 16777619 & 4294967295
    return h

def words_of(s):
    return [int(w, 16) for w in s.split(',')]

def normalize_fixture(n, raw):
    f = json.loads(raw)
    if n == 2:
        return {x: {'command': f[x]['command'], 'request': f[x]['request'], 'response': f[x]['response']} for x in ('SEED', 'PROB')}
    req(f.get('oracle_sha256') == ORACLE and f.get('source_matrix_sha256') == MATRIX, 'FROZEN_FIXTURE_SOURCE_' + str(n))
    return {'SEED': {'command': f['seed_command'], 'request': f['seed_request_words'], 'response': f['seed_response_words']}, 'PROB': {'command': f['prob_command'], 'request': f['prob_request_words'], 'response': f['prob_response_words']}}

def audit_frame(kind, raw, expected, observed, raw_rows, snaps, post, seq):
    er = [int(x, 16) for x in expected['request']]
    ep = [int(x, 16) for x in expected['response']]
    req(len(er) == (10 if kind == 'SEED' else 28), 'ORACLE_REQUEST_LENGTH')
    req(len(ep) == (6 if kind == 'SEED' else 38), 'ORACLE_RESPONSE_LENGTH')
    req(crc(er[:-1]) == er[-1] and crc(ep[:-1]) == ep[-1], 'ORACLE_REFERENCE_CRC_' + kind)
    req(er == observed['request'] and ep == observed['response'], 'ORACLE_EXACT_MISMATCH_' + kind)
    req(er[3] == ep[3] == seq, 'SEQUENCE_BAD_' + kind)
    req(observed['ready_samples'] == ['1'] * len(er), 'TX_ACCEPTANCE_BAD_' + kind)
    req(observed['turnaround'] == ('2', '0' if kind == 'SEED' else '3', '2', '0'), 'TURNAROUND_BAD_' + kind)
    req(len(raw_rows) == len(ep), 'RAW_AUDIT_COUNT_' + kind)
    for i, (j, ph, word, shadow) in enumerate(raw_rows):
        req(int(j) == i and int(ph) in (1, 2) and (int(word, 16) == int(shadow, 16) == ep[i]), 'RAW_SHADOW_MISMATCH_' + kind + '_' + str(i))
    req(len(snaps) == 3 and len(post) == 1, 'SNAPSHOT_COUNT_' + kind)
    for slot, count, a, b, mismatch in snaps:
        count = int(count)
        req(int(slot) in (0, 1, 2) and 0 <= count <= len(ep) and (int(a, 16) == int(b, 16) == fnv(ep[:count])) and (mismatch == '0'), 'SNAPSHOT_FNV_' + kind + '_' + slot)
    a, b, mismatch = post[0]
    req(int(a, 16) == int(b, 16) == fnv(ep) and mismatch == '0', 'POSTPRINT_FNV_' + kind)
    return {'request_crc': f'{er[-1]:04X}', 'response_crc': f'{ep[-1]:04X}', 'request_words': len(er), 'response_words': len(ep), 'raw_verified': len(ep), 'last_snapshot_fnv': f'{fnv(ep):08X}', 'response_sha256': sha(bytes((x for w in ep for x in (w & 255, w >> 8))))}

def verify_transcript(record, raw, fixture):
    """Check exact ordered blocks; telemetry remains software-reported."""
    lines = raw.decode('ascii', 'strict').splitlines()
    req(len(lines) == 67, 'TRANSCRIPT_LINE_COUNT')
    pos = 0

    def take(pattern):
        nonlocal pos
        req(pos < len(lines), 'INCOMPLETE_TRANSCRIPT')
        m = re.fullmatch(pattern, lines[pos])
        req(m is not None, 'TRANSCRIPT_ORDER_OR_CONTENT_' + str(pos))
        pos += 1
        return m.groups()
    fx = normalize_fixture(record, fixture)
    summary = {}
    for kind, seq in zip(('SEED', 'PROB'), SEQS[record]):
        nreq, rq = take('CPTRANS kind=REQUEST count=(\\d+) words=([0-9A-F,]+)')
        count, samples = take('CPTRANS kind=TXTRACE count=(\\d+) samples=([0-3,]+)')
        turn = take('CPTRANS kind=TURNAROUND tx_guard=(\\d+) stall=(\\d+) rx_guard=(\\d+) pico_oe=(\\d+)')
        nrsp, overflow = take('RXAUDIT_V1 count=(\\d+) overflow=(\\d+)')
        req(overflow == '0' and count == nreq, 'AUDIT_OVERFLOW_OR_TX_COUNT')
        req(int(nrsp) == (6 if kind == 'SEED' else 38), 'RESPONSE_LENGTH')
        snaps = [take('RXAUDIT_SNAP slot=(\\d+) count=(\\d+) response_fnv=([0-9A-F]{8}) shadow_fnv=([0-9A-F]{8}) mismatch=(\\d+)') for _ in range(3)]
        req([s[0] for s in snaps] == ['0', '1', '2'], 'SNAPSHOT_SLOT_ORDER')
        req([int(s[1]) for s in snaps] == [4, int(nrsp), int(nrsp)], 'SNAPSHOT_COUNTS')
        rows = [take('RXAUDIT_WORD index=(\\d+) phase=(\\d+) raw=([0-9A-F]{8}) shadow=([0-9A-F]{4})') for _ in range(int(nrsp))]
        req([int(row[1]) for row in rows] == [1] * 4 + [2] * (int(nrsp) - 4), 'HEADER_BODY_PHASE')
        count_rsp, rsp = take('CPTRANS kind=RESPONSE count=(\\d+) words=([0-9A-F,]+)')
        req(count_rsp == nrsp, 'RESPONSE_COUNT')
        post = [take('RXAUDIT_POSTPRINT response_fnv=([0-9A-F]{8}) shadow_fnv=([0-9A-F]{8}) mismatch=(\\d+)')]
        result_seq, protocol, meta, error = take('CPTRANS kind=RESULT sequence=(\\d+) protocol=(\\d+) meta=([0-9A-F]{4}) error_pin=(\\d+)')
        req((result_seq, protocol, meta, error) == (str(seq), '0', '1800' if kind == 'SEED' else '1900', '0'), 'PROTOCOL_RESULT')
        take('OK ' + kind + ' sequence=' + str(seq))
        observed = {'request': words_of(rq), 'response': words_of(rsp), 'ready_samples': samples.split(','), 'turnaround': turn}
        req(len(observed['request']) == int(nreq) and len(observed['response']) == int(nrsp), 'WIRE_LENGTH')
        summary[kind] = audit_frame(kind, raw, fx[kind], observed, rows, snaps, post, seq)
    status = lines[pos]
    req(status.startswith('OK STATUS '), 'FINAL_STATUS')
    fields = dict((token.split('=', 1) for token in status.split()[2:]))
    required = {'fw': 'CPC-PICO-RX-DEFERRED-ACK-v6', 'build': 'CPC-PICO-RX-DEFERRED-ACK-v6-FWQUAL-v1', 'reset': '1', 'valid': '0', 'write': '1', 'data_dir': 'input', 'session_consumed': '1', 'active': '0', 'transaction': '0', 'done': '2', 'limit': '2', 'release_idle_consumed': '0', 'release_idle_success': '0', 'reset_released': '0', 'release_code': 'DENIED', 'ready': '1', 'error': '0'}
    req(fields == required and len(status.split()) == len(required) + 2, 'FINAL_SOFTWARE_STATUS')
    req(pos + 1 == len(lines), 'TRAILING_CONTENT')
    return summary

def verify_all(root=ROOT):
    root = Path(root)
    manifest = json.loads((root / 'MANIFEST-SHA256.json').read_text())
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.name != 'MANIFEST-SHA256.json'}
    req(set(manifest) == actual, 'MANIFEST_FILE_SET')
    for name, expected in manifest.items():
        req(sha((root / name).read_bytes()) == expected, 'MANIFEST_HASH_' + name)
    pins = json.loads((root / 'SOURCE-PINS.json').read_text())
    req((pins['oracle_sha256'], pins['matrix_sha256'], pins['firmware_uf2_sha256'], pins['fpga_bitstream_file_sha256']) == (ORACLE, MATRIX, UF2, FPGA), 'SOURCE_IDENTITIES')
    provenance = json.loads((root / 'PROVENANCE.json').read_text())
    pairs = {}
    for n in SEQS:
        pin = pins['reports'][str(n)]
        fixture = (root / pin['fixture']).read_bytes()
        req(sha(fixture) == pin['fixture_sha256'], 'FROZEN_FIXTURE_HASH')
        raw = (root / provenance['records'][str(n)]['transcript']).read_bytes()
        pairs[str(n)] = verify_transcript(n, raw, fixture)
    return {'classification': 'PUBLIC_EXCERPT_THREE_RECORD_AUDIT_PASS', 'physical_prob_records': list(SEQS), 'verified_response_words': 132, 'verified_request_crc': 6, 'verified_response_crc': 6, 'verified_snapshot_hashes': 18, 'pairs': pairs, 'physical_provenance': 'RETAINED_HOST_LOGS_NOT_INDEPENDENT_SENSOR_ATTESTATION', 'final_state': 'SOFTWARE_REPORTED_NOT_ELECTRICALLY_MEASURED', 'quantum_qualification': 'NOT_ESTABLISHED', 'no_hardware_operations': True}
if __name__ == '__main__':
    try:
        print(json.dumps(verify_all(), indent=2, sort_keys=True))
    except (ValueError, KeyError, OSError, UnicodeError, IndexError) as exc:
        print('UP5K_EVIDENCE_VERIFY_FAIL:', exc, file=sys.stderr)
        sys.exit(2)
