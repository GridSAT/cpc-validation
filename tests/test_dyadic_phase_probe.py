"""Independent diagnostic fixtures; r/s never enter operational functions."""
import inspect
import numpy as np
import pytest
from scipy import sparse
from src.dyadic_phase_probe import Probe,LOWER,multiplier,operators,generator,prepare,evolve,observation_means


def fixture_vector(N,a,r,s):
    v=np.zeros(1<<(N-1).bit_length(),complex)
    for k in range(r):v[pow(a,k,N)]=np.exp(-2j*np.pi*s*k/r)/np.sqrt(r)
    return v


@pytest.mark.parametrize('j',range(4))
def test_total_unitarity_power_identity_and_controlled_synthesis(j):
    m=Probe(7,3,j);u=multiplier(m).toarray();base=multiplier(Probe(7,3)).toarray()
    assert np.allclose(u.conjugate().T@u,np.eye(8))
    assert np.allclose(u,np.linalg.matrix_power(base,2**j))
    assert u[7,7]==1
    h,J=operators(m);W=sparse.block_diag((np.eye(8),u)).toarray()
    x=np.array([[0,1],[1,0]])
    assert np.allclose(h.toarray(),m.g*W@np.kron(x,np.eye(8))@W.conjugate().T)
    assert np.allclose((h@h).toarray(),m.g**2*np.eye(16))


@pytest.mark.parametrize('N,a,r,s',[(7,3,6,s) for s in range(6)]+[(5,2,4,1),(5,2,4,3)])
def test_sector_stationarity_phase_sign_density_and_reference(N,a,r,s):
    m=Probe(N,a,g=.7,Gamma=1.1);v=fixture_vector(N,a,r,s)
    P=np.outer(v,v.conjugate());Q=np.kron(np.eye(2),P);h,J=operators(m)
    assert np.linalg.norm(h@Q-Q@h)<1e-12
    assert np.linalg.norm(J@Q-Q@J)<1e-12
    initial=np.kron(np.diag([1.,0.]),P)
    phi=2*np.pi*s/r;den=m.Gamma**2+8*m.g**2
    q=-2j*m.g*m.Gamma*np.exp(1j*phi)/den;p=4*m.g**2/den
    ref=np.array([[1-p,q.conjugate()],[q,p]])
    reference=np.kron(ref,P)
    assert np.linalg.norm(generator(m)@reference.reshape(-1,order='F'))<1e-12
    states=evolve(m,initial,(0.,1.,70.))
    for rho in states:
        assert np.trace(rho)==pytest.approx(1,abs=1e-10)
        assert np.linalg.eigvalsh(rho).min()>-1e-10
        assert np.allclose(rho,rho.conjugate().T)
        assert np.trace(Q@rho)==pytest.approx(1,abs=1e-10)
    final=states[-1];assert np.linalg.norm(final-reference)<1e-8
    for theta in (0.,np.pi/2,.37):
        obs=observation_means(m,final,theta,.6)
        assert obs['photon_flux']==pytest.approx(m.Gamma*p,abs=1e-9)
        assert obs['homodyne_mean']==pytest.approx(2*np.sqrt(.6*m.Gamma)*np.real(np.exp(-1j*theta)*q),abs=1e-9)
    assert observation_means(m,final,eta=0)['homodyne_mean']==0


@pytest.mark.parametrize('j',range(4))
def test_order_six_ensemble_negative_control_and_sector_populations(j):
    m=Probe(7,3,j)
    assert abs(sum(np.exp(2j*np.pi*2**j*np.arange(6)/6))/6)<1e-12
    for rho in evolve(m,prepare(m),(0.,1.,40.)):
        assert abs(observation_means(m,rho)['homodyne_mean'])<1e-10
        assert abs(observation_means(m,rho,np.pi/2)['homodyne_mean'])<1e-10
        for s in range(6):
            v=fixture_vector(7,3,6,s);P=np.kron(np.eye(2),np.outer(v,v.conjugate()))
            assert np.trace(P@rho)==pytest.approx(1/6,abs=1e-10)


def test_counting_transient_is_phase_blind_but_quadrature_is_not():
    m=Probe(5,2);records=[]
    for s in (1,3):
        v=fixture_vector(5,2,4,s)
        states=evolve(m,np.kron(np.diag([1.,0.]),np.outer(v,v.conjugate())),(.2,1.,10.))
        records.append([observation_means(m,rho) for rho in states])
    assert [r['photon_flux'] for r in records[0]]==pytest.approx([r['photon_flux'] for r in records[1]])
    assert records[0][-1]['homodyne_mean']==pytest.approx(-records[1][-1]['homodyne_mean'])
    assert abs(records[0][-1]['homodyne_mean'])>.1


def test_advice_boundaries_and_caps():
    for fn in (Probe,multiplier,operators,generator,prepare,evolve):
        for key in ('r','s','order','factors','expected_phases','expected_peaks','semantic_answer'):
            with pytest.raises(TypeError):inspect.signature(fn).bind_partial(**{key:1})
    for args in ((8,3),(6,3),(7,3,9)):
        with pytest.raises(ValueError):Probe(*args)
    with pytest.raises(ValueError):evolve(Probe(7,3),prepare(Probe(7,3)),(81.,))
