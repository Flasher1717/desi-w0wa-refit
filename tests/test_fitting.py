"""Unit tests for deterministic fitting and the significance convention."""

import numpy as np
import pytest

from desi_w0wa_refit.bao import FloatArray
from desi_w0wa_refit.fitting import (
    aic,
    bic,
    derive_seed,
    minimize_multistart,
    nsigma_from_delta_chi2,
)


def test_derive_seed_is_pure_and_distinct() -> None:
    assert derive_seed("run-a") == derive_seed("run-a")
    assert derive_seed("run-a") != derive_seed("run-b")
    assert 0 <= derive_seed("run-a") < 2**32


def test_nsigma_matches_published_table6_roundings() -> None:
    # arXiv:2503.14738v3 Table 6 pairs (Delta chi2_MAP, printed sigma):
    # -4.7 -> 1.7 sigma ; -8.0 -> 2.4 sigma ; -12.5 -> 3.1 sigma ;
    # -17.4 -> 3.8 sigma ; -21.0 -> 4.2 sigma.
    for delta_chi2, printed in ((4.7, 1.7), (8.0, 2.4), (12.5, 3.1), (17.4, 3.8), (21.0, 4.2)):
        assert round(nsigma_from_delta_chi2(delta_chi2), 1) == printed


def test_nsigma_edge_cases() -> None:
    assert nsigma_from_delta_chi2(0.0) == 0.0
    assert nsigma_from_delta_chi2(-3.0) == 0.0
    with pytest.raises(ValueError, match="2 extra parameters"):
        nsigma_from_delta_chi2(5.0, dof=3)


def test_aic_bic_definitions() -> None:
    assert aic(10.0, 2) == 14.0
    assert abs(bic(10.0, 2, 100) - (10.0 + 2.0 * float(np.log(100.0)))) < 1e-12


def test_multistart_finds_global_minimum_of_two_well_potential() -> None:
    # Two wells: local at x ~ (+1, +1) with f=1, global at (-1, -1) with f=0.
    def chi2_fn(x: FloatArray) -> float:
        a = float((x[0] - 1.0) ** 2 + (x[1] - 1.0) ** 2) + 1.0
        b = float((x[0] + 1.0) ** 2 + (x[1] + 1.0) ** 2)
        return min(a, b)

    fit = minimize_multistart(
        chi2_fn, [(-3.0, 3.0), (-3.0, 3.0)], run_name="test-two-well", n_starts=16
    )
    assert fit.chi2 < 1e-8
    np.testing.assert_allclose(fit.x, [-1.0, -1.0], atol=1e-4)
    assert fit.start_chi2s.size == 16


def test_multistart_is_deterministic() -> None:
    def chi2_fn(x: FloatArray) -> float:
        return float((x[0] - 0.3) ** 2)

    fit_a = minimize_multistart(chi2_fn, [(0.0, 1.0)], run_name="det", n_starts=4)
    fit_b = minimize_multistart(chi2_fn, [(0.0, 1.0)], run_name="det", n_starts=4)
    np.testing.assert_array_equal(fit_a.x, fit_b.x)
    np.testing.assert_array_equal(fit_a.start_chi2s, fit_b.start_chi2s)


def test_multistart_respects_start_constraint() -> None:
    seen: list[float] = []

    def chi2_fn(x: FloatArray) -> float:
        seen.append(float(x[0] + x[1]))
        return float(x[0] ** 2 + x[1] ** 2)

    minimize_multistart(
        chi2_fn,
        [(-1.0, 1.0), (-1.0, 1.0)],
        run_name="constrained",
        n_starts=4,
        constraint=lambda x: float(x[0] + x[1]) < 0.0,
    )
    # The optimizer may explore anywhere, but it must START in the
    # constrained region: the first evaluation of each simplex is x0.
    assert seen[0] < 0.0
