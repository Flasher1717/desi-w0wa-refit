"""Keeley-style SN covariance corrections (PREREGISTRATION.md P12, V4).

A pre-registered SENSITIVITY analysis -- NEVER "the" corrected preference; the
published covariance stays the v1.1.0 baseline. Two ways of applying Keeley,
Shafieloo & L'Huillier [arXiv:2212.07917 v3, Sec. 2]'s characterization of the
SN distance-error overestimation as a covariance correction, frozen at the
GO M15 (decision A, "report both"):

- Scenario (i-kappa), PRIMARY: global rescale ``C -> C * kappa`` with
  ``kappa = chi2_min / N``, the reduced chi2 of the offset-profiled flat-LCDM
  SN-only fit (Keeley dof = N, no parameter subtraction). This is Keeley's
  full-covariance whitening reading [Eqs. (9)-(10): the sum of squared
  whitened residuals equals chi2, so a uniform rescale by chi2/N lands
  chi2/dof = 1 EXACTLY]. A uniform positive rescale leaves the SN-only argmin
  unchanged, so the corrected reduced chi2 is 1 by construction.
- Scenario (i-s), DESCRIPTIVE: ``C -> C * s_diag^2`` with ``s_diag`` the
  V1-committed DIAGONAL normalized-residual std
  (``mocks.normalized_residual_std``, normalized by ``sqrt(diag C)``). Because
  the diagonal ignores the off-diagonal correlations Keeley whitens, this does
  NOT land chi2/dof = 1 (residual ~1.05 P+ / 1.10 DES); the gap is the measured
  diagonal-vs-full sensitivity (GO M15, decision A).
- Scenario (ii): ``C -> C - delta^2 I`` with ``delta^2`` tuned so chi2_min = N
  (``mocks.delta2_for_chi2_eq_n``), Keeley's intrinsic-scatter subtraction
  (prose in v3, no equation number).

The correction touches the SN covariance ONLY; the BAO and CMB blocks are
untouched (the corrected ``SNSample`` is passed to ``arms.make_cmb_arm``).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from desi_w0wa_refit.mocks import (
    delta2_for_chi2_eq_n,
    fit_lcdm_profiled,
    normalized_residual_std,
)
from desi_w0wa_refit.sne import SNSample


@dataclass(frozen=True)
class CorrectionFactors:
    """The three pre-registered correction factors for one SN sample (P12.2-P12.3).

    All derived from the offset-profiled flat-LCDM SN-only fit on the sample's
    OWN data (so factors match the arm they correct, GO M15 decision B).
    """

    n_sne: int
    chi2_min_sn_only: float
    reduced_chi2: float  # chi2_min / N (Keeley dof = N)
    kappa: float  # scenario (i-kappa): equals reduced_chi2
    s_diag: float  # scenario (i-s): diagonal normalized-residual std
    delta2: float  # scenario (ii): diagonal subtraction so chi2_min = N
    chi2_at_delta2: float


def correction_factors(sample: SNSample) -> CorrectionFactors:
    """Compute (kappa, s_diag, delta^2) from the offset-profiled SN-only LCDM fit."""
    fit = fit_lcdm_profiled(sample, sample.mag)
    n = sample.n_sne
    delta2, chi2_at = delta2_for_chi2_eq_n(sample)
    return CorrectionFactors(
        n_sne=n,
        chi2_min_sn_only=fit.chi2,
        reduced_chi2=fit.chi2 / n,
        kappa=fit.chi2 / n,
        s_diag=normalized_residual_std(sample, fit),
        delta2=delta2,
        chi2_at_delta2=chi2_at,
    )


def rescale_covariance(sample: SNSample, factor: float) -> SNSample:
    """Return a copy of ``sample`` with ``C -> C * factor`` (factor > 0).

    Used for scenarios (i-kappa) [factor = kappa] and (i-s) [factor = s_diag^2].
    A positive scalar rescale keeps the covariance symmetric positive definite,
    so the ``SNSample`` Cholesky in ``__post_init__`` stays valid.
    """
    if not factor > 0.0:
        raise ValueError(f"{sample.name}: rescale factor must be positive, got {factor}")
    return SNSample(
        name=sample.name,
        z_cmb=sample.z_cmb,
        z_hel=sample.z_hel,
        mag=sample.mag,
        cov=sample.cov * factor,
        survey_ids=sample.survey_ids,
    )


def subtract_diagonal(sample: SNSample, delta2: float) -> SNSample:
    """Return a copy with ``C -> C - delta^2 I`` (scenario ii, Keeley intrinsic scatter).

    ``delta2`` from ``mocks.delta2_for_chi2_eq_n`` stays within the SPD domain
    (bounded by the smallest eigenvalue), so the ``SNSample`` Cholesky is valid.
    """
    return SNSample(
        name=sample.name,
        z_cmb=sample.z_cmb,
        z_hel=sample.z_hel,
        mag=sample.mag,
        cov=sample.cov - delta2 * np.eye(sample.n_sne),
        survey_ids=sample.survey_ids,
    )


def corrected_reduced_chi2(sample: SNSample) -> float:
    """Reduced chi2 (chi2_min / N, Keeley dof = N) of the offset-profiled
    SN-only LCDM fit on a (possibly corrected) sample -- the control quantity
    of gate G16.1."""
    return fit_lcdm_profiled(sample, sample.mag).chi2 / sample.n_sne
