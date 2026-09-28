from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from src.dyadic_phase_ms_dp_p_e3_acquisition import (
    AcquisitionError,
    SequentialBank,
    channel_record_sha256,
    compile_dp_s_permutations,
    local_phases_from_records,
    local_referenced_phase,
    profile_fixed_callback,
    structural_resource_profile,
)

ROOT=Path(__file__).resolve().parents[1]
PATCHED=ROOT/"src/dyadic_phase_ms_dp_p_e3_kernel.c"
BASE=ROOT/"src/dyadic_phase_p3_kernel.c"
BASE_SHA="c9dc0bbb05ff8a51a3b174377412afa1b8c60404804432ce5cd7719c28d4e595"
FIXTURES=((5,2,3),(7,2,4),(7,3,4),(15,2,6))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@pytest.fixture
def native_library(tmp_path):
    compiler=shutil.which("cc")
    if compiler is None:
        pytest.fail("E3-IB native validation requires cc; compiler not found")
    assert sha(PATCHED)=="ff30745e57429df6cefd65ec3803435fdc7949b451b49e97cbabf084a2529aa7"
    library=tmp_path/"e3-kernel.so"
    subprocess.run(
        [compiler,"-std=c11","-O3","-fPIC","-shared",str(PATCHED),
         "-o",str(library),"-lm"],
        check=True,timeout=60,
    )
    assert library.is_file(), "compiler did not produce the E3-IB library"
    return library


@pytest.mark.parametrize("N,a,J",FIXTURES)
def test_exact_frozen_scale_sets(N,a,J):
    m=SequentialBank(N,a)
    assert m.scales==tuple(range(J+1))
    assert m.dimension==2*m.d


@pytest.mark.parametrize("N,a,J",FIXTURES)
def test_compiled_permutations_are_exact_involutions(N,a,J):
    m=SequentialBank(N,a)
    perms=compile_dp_s_permutations(m)
    assert perms.shape==(J+1,m.dimension)
    target=np.arange(m.dimension)
    for p in perms:
        assert np.array_equal(np.sort(p),target)
        assert np.array_equal(p[p],target)


def test_j0_j1_j2_compilation_matches_frozen_p3_single_probe():
    from src.dyadic_phase_p3 import Bank, compile_bank
    m=SequentialBank(7,3)
    ours=compile_dp_s_permutations(m)
    for j in (0,1,2):
        old=compile_bank(Bank(7,3,(j,)))[0]["permutation"]
        assert np.array_equal(ours[j],old)


def synthetic_record(phase,chi,steps=32,dt=.04):
    def one(alpha):
        z=np.exp(2j*np.pi*float(alpha))
        I0=z.imag
        I90=-z.real
        return np.vstack([
            np.full(steps,I0*dt),
            np.full(steps,I90*dt),
        ])
    return one((phase+chi)%1),one(chi%1)


@pytest.mark.parametrize("phase",[0,Fraction(1,4096),Fraction(1,6),Fraction(1,3),
                                  Fraction(1,2),Fraction(5,6),Fraction(4095,4096)])
@pytest.mark.parametrize("chi",[0,Fraction(1,11),Fraction(7,13)])
def test_local_referenced_estimator_exact_on_deterministic_means(phase,chi):
    sig,ref=synthetic_record(phase,chi)
    est=local_referenced_phase(sig,ref,.04)
    q=float(est)
    d=abs((q-float(phase)+.5)%1-.5)
    assert d<1e-14


def test_multiscale_local_estimator_shapes():
    m=SequentialBank(15,2)
    sig=[];ref=[]
    theta=Fraction(1,4)
    for j in m.scales:
        s,r=synthetic_record(((1<<j)*theta)%1,Fraction(1,17))
        sig.append(s);ref.append(r)
    phases=local_phases_from_records(np.asarray(sig),np.asarray(ref),.04)
    assert len(phases)==7
    for j,p in enumerate(phases):
        truth=float(((1<<j)*theta)%1)
        assert abs((float(p)-truth+.5)%1-.5)<1e-14


def test_undefined_reference_fails_closed():
    z=np.zeros((2,8))
    with pytest.raises(AcquisitionError,match="undefined"):
        local_referenced_phase(z,z,.04)


def test_channel_hash_is_stable_and_scale_sensitive():
    s,r=synthetic_record(Fraction(1,3),Fraction(1,7))
    h0=channel_record_sha256(0,s,r)
    assert h0==channel_record_sha256(0,s.copy(),r.copy())
    assert h0!=channel_record_sha256(1,s,r)


@pytest.mark.parametrize("N,a,J",FIXTURES)
def test_structural_profile_counts(N,a,J):
    m=SequentialBank(N,a)
    schedule={
        "dt":.04,"burn":16.,"window":81.92,"eta":.8,
        "transfer_phases":[.7]*(J+1),
        "reset_time":.25,"retune_time":.1,"dead_time":.5,
    }
    p=structural_resource_profile(m,schedule)
    assert p["scale_count"]==J+1
    assert p["data_preparations"]==1
    assert p["probe_resets"]==J
    assert p["retunes"]==J
    assert p["state_dimension"]==2*m.d
    assert p["record_buffer_bytes"]==2*(J+1)*2*2048*8
    assert p["DP_P_physical_resource_equivalence_claimed"] is False


def test_native_patch_is_exactly_two_frozen_replacements():
    assert sha(BASE)==BASE_SHA
    base=BASE.read_text()
    expected=base.replace(
        "m<1 || m>3 || D>64",
        "m<1 || m>7 || D>64",
    ).replace(
        "double complex state[64],refs[3][2];",
        "double complex state[64],refs[7][2];",
    )
    assert expected!=base
    assert PATCHED.read_text()==expected
    assert "m<1 || m>7 || D>64" in expected
    assert "refs[7][2]" in expected


def test_fixed_callback_native_m7_smoke_no_prng(native_library):
    m=SequentialBank(15,2)
    schedule={
        "dt":.04,"burn":0.,"window":.04,"eta":.8,
        "transfer_phases":[.7]*7,
        "reset_time":.25,"retune_time":.1,"dead_time":.5,
    }
    p=profile_fixed_callback(m,schedule,native_library)
    assert p["stochastic_records_generated"]==0
    assert p["record_shape"]==[7,2,1]
    assert p["counters"][0]==1
    assert p["counters"][4]==6


def test_operational_model_rejects_partial_or_extra_scales():
    with pytest.raises(AcquisitionError):
        SequentialBank(15,2,(0,1,2))
    with pytest.raises(AcquisitionError):
        SequentialBank(15,2,tuple(range(8)))
