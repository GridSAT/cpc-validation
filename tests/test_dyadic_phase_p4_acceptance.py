from fractions import Fraction as F
from src.dyadic_phase_p4_acceptance import binomial_cdf,upper_tail,calibration_passes,design


def test_exact_binomial_and_calibration():
    assert binomial_cdf(2,0,F(1,2))==F(1,4)
    assert upper_tail(2,1,F(1,2))==F(3,4)
    d=design();n=d['calibration_trials_per_sector']
    assert calibration_passes(0,n,beta_limit=d['beta'],alpha=d['cell_alpha'])
    assert calibration_passes(d['calibration_max_errors'],n,beta_limit=d['beta'],alpha=d['cell_alpha'])
    assert not calibration_passes(d['calibration_max_errors']+1,n,beta_limit=d['beta'],alpha=d['cell_alpha'])
    assert d['calibration_power_at_error_0_1pct_lower']>F(9,10)

def test_predeclared_error_power_and_success_budgets():
    d=design()
    assert 4*d['beta']==d['conditional_wrong_limit_given_good_calibration']==F(1,5)
    assert d['calibration_family_alpha']==d['calibration_exception_limit']==F(1,100)
    assert d['conditional_wrong_limit_given_good_calibration']+d['calibration_exception_limit']==d['wrong_joint_limit']==F(21,100)
    assert d['maximum_wrong_accepted_count']==13
    assert binomial_cdf(128,13,F(1,5))<=F(1,400)
    assert binomial_cdf(128,14,F(1,5))>F(1,400)
    assert d['correct_success_lower_before_noncompletion_gamma']>F(7,10)
    assert d['power_at_correct_acceptance_90pct']>F(9,10)
    assert d['power_at_wrong_acceptance_2pct']>F(9,10)
