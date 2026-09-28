"""Exact binomial planning/calibration arithmetic; never generates records."""
from fractions import Fraction
from math import comb


def binomial_cdf(n, k, probability):
    if type(n) is not int or not 0 <= n <= 4096 or type(k) is not int or type(probability) is not Fraction or not 0 <= probability <= 1:
        raise ValueError('bounded exact binomial parameters')
    if k < 0:return Fraction(0)
    if k >= n:return Fraction(1)
    return sum((comb(n,i)*probability**i*(1-probability)**(n-i) for i in range(k+1)),Fraction(0))


def upper_tail(n, k, probability):
    return 1-binomial_cdf(n,k-1,probability)


def calibration_passes(errors, trials, *, beta_limit, alpha):
    """Reject error-rate >= beta_limit at one-sided level alpha.

    Separate sector calibration is required; no conditioning on successful
    reconstruction or selecting favorable calibration records is permitted.
    """
    if type(errors) is not int or not 0 <= errors <= trials or not 0 < alpha < 1:
        raise ValueError('calibration count/alpha')
    return binomial_cdf(trials,errors,beta_limit) <= alpha


def design():
    k=4;beta=Fraction(1,20);calibration_alpha=Fraction(1,100);sectors=17
    cell_alpha=calibration_alpha/sectors
    calibration_n=256
    calibration_max_errors=max(t for t in range(calibration_n+1) if binomial_cdf(calibration_n,t,beta)<=cell_alpha)
    calibration_power=binomial_cdf(calibration_n,calibration_max_errors,Fraction(1,1000))**sectors
    calibration_power_lower=Fraction((calibration_power*10**12).numerator//(calibration_power*10**12).denominator,10**12)
    n=128;alpha=Fraction(1,400)
    success_threshold=next(t for t in range(n+1) if upper_tail(n,t,Fraction(7,10))<=alpha)
    conditional_wrong_limit=4*beta
    wrong_joint_limit=conditional_wrong_limit+calibration_alpha
    wrong_threshold=max(t for t in range(n+1) if binomial_cdf(n,t,conditional_wrong_limit)<=alpha)
    return {'fixed_k':k,'beta':beta,'calibration_family_alpha':calibration_alpha,'calibration_cells':sectors,
            'cell_alpha':cell_alpha,'calibration_trials_per_sector':calibration_n,
            'calibration_max_errors':calibration_max_errors,
            'calibration_power_at_error_0_1pct_lower':calibration_power_lower,
            'calibration_power_rounding_error_upper':Fraction(1,10**12),'evaluation_bundles_per_fixture':n,
            'success_minimum':Fraction(7,10),
            'conditional_wrong_limit_given_good_calibration':conditional_wrong_limit,
            'calibration_exception_limit':calibration_alpha,
            'wrong_joint_limit':wrong_joint_limit,
            'per_fixture_per_endpoint_alpha':alpha,'minimum_correct_accepted_count':success_threshold,
            'maximum_wrong_accepted_count':wrong_threshold,
            'power_at_correct_acceptance_90pct':upper_tail(n,success_threshold,Fraction(9,10)),
            'power_at_wrong_acceptance_2pct':binomial_cdf(n,wrong_threshold,Fraction(1,50)),
            'ideal_success_worst_mandatory_order':Fraction(25,27),
            'correct_success_lower_before_noncompletion_gamma':Fraction(25,27)-k*beta-calibration_alpha,
            'evaluation_fresh_trials':4*n*k,'calibration_fresh_trials':sectors*calibration_n}
