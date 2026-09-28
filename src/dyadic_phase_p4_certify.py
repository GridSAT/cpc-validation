"""P4-EXACT certificate generation and independent bounded verification."""
from math import gcd, isqrt
from src.dyadic_phase_p4_types import integer, identity


def validate_instance(N, a, R, policy):
    integer(N, 2, policy.max_integer_bits); integer(a, 1, policy.max_integer_bits)
    integer(R, 1, policy.max_integer_bits)
    if a >= N or R >= N or gcd(N, a) != 1:
        raise ValueError('inadmissible instance/candidate')


def verify_order_certificate(N, a, candidate_R, certificate, policy):
    """Check complete product, primality and minimality without trusting generator."""
    validate_instance(N, a, candidate_R, policy)
    if type(certificate) is not tuple:
        raise ValueError('canonical factor certificate required')
    previous = 1; product = 1; divisions = 0; primes = []
    for row in certificate:
        if type(row) is not tuple or len(row) != 2:
            raise ValueError('certificate row')
        p, e = row
        integer(p, 2, policy.max_integer_bits); integer(e, 1, policy.max_integer_bits)
        if p <= previous or p > candidate_R or e > candidate_R.bit_length():
            return {'status': 'VERIFICATION_FAILURE', 'reason': 'factor structure', 'divisions': divisions}
        for divisor in range(2, isqrt(p)+1):
            if divisions >= policy.max_certificate_divisions:
                return {'status': 'CERTIFICATION_INCOMPLETE', 'reason': 'primality cap', 'divisions': divisions}
            divisions += 1
            if p % divisor == 0:
                return {'status': 'VERIFICATION_FAILURE', 'reason': 'composite factor', 'divisions': divisions}
        for _ in range(e):
            product *= p
            if product > candidate_R:
                return {'status': 'VERIFICATION_FAILURE', 'reason': 'product exceeds candidate', 'divisions': divisions}
        primes.append(p); previous = p
    if product != candidate_R or pow(a, candidate_R, N) != 1:
        return {'status': 'VERIFICATION_FAILURE', 'reason': 'product or modular test', 'divisions': divisions}
    residues = tuple((p, pow(a, candidate_R//p, N)) for p in primes)
    if any(v == 1 for _, v in residues):
        return {'status': 'VERIFICATION_FAILURE', 'reason': 'nonminimal multiple', 'divisions': divisions, 'residues': residues}
    return {'status': 'CERTIFIED_EXACT_ORDER', 'divisions': divisions, 'residues': residues,
            'certificate_identity': identity('exact-certificate', {'N': N, 'a': a, 'R': candidate_R, 'factors': certificate})}


def certify_order(N, a, candidate_R, policy):
    validate_instance(N, a, candidate_R, policy)
    if pow(a, candidate_R, N) != 1:
        return {'status': 'VERIFICATION_FAILURE', 'reason': 'not an order multiple', 'factor_divisions': 0}
    remaining = candidate_R; divisor = 2; factors = []; divisions = 0
    while divisor*divisor <= remaining:
        exponent = 0
        while True:
            if divisions >= policy.max_factor_divisions:
                return {'status': 'CERTIFICATION_INCOMPLETE', 'reason': 'factor cap', 'factor_divisions': divisions}
            divisions += 1
            if remaining % divisor:
                break
            remaining //= divisor; exponent += 1
        if exponent:
            factors.append((divisor, exponent))
        divisor += 1
    if remaining > 1:
        factors.append((remaining, 1))
    result = verify_order_certificate(N, a, candidate_R, tuple(factors), policy)
    return {**result, 'factors': tuple(factors), 'factor_divisions': divisions}
