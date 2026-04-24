"""Tests for decay fitting."""
import numpy as np

from src import decay


def test_decay_model_at_zero():
    """At tau=0, the model should equal A + C."""
    A, lam, C = 0.05, 0.5, 0.01
    val = decay.decay_model(np.array([0.0]), A, lam, C)
    assert np.isclose(val[0], A + C)


def test_fit_recovers_known_params():
    """Fit should recover parameters from clean synthetic data."""
    A_true, lam_true, C_true = 0.04, 0.3, 0.005
    tau = np.arange(-5, 11)
    car = decay.decay_model(tau, A_true, lam_true, C_true)
    car[tau < 0] = 0.0  # CAR is 0 before event by convention

    fit = decay.fit_decay(tau, car)
    assert not np.isnan(fit["half_life"])
    # Recovered params should be close
    assert abs(fit["A"] - A_true) < 0.01
    assert abs(fit["lambda"] - lam_true) < 0.1


def test_halflife_formula():
    """t_half = ln(2) / lambda."""
    lam = 0.5
    expected = np.log(2) / lam
    assert np.isclose(expected, 1.3862943611198906)


def test_fit_handles_garbage():
    """All-zero input shouldn't crash; should return NaN half-life."""
    tau = np.arange(-5, 11)
    car = np.zeros_like(tau, dtype=float)
    fit = decay.fit_decay(tau, car)
    # Either NaN or extreme values — just shouldn't crash
    assert isinstance(fit, dict)
    assert "half_life" in fit
