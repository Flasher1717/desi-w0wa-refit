# RESULTS — desi-w0wa-refit

> Final document (M8, 2026-06-11; translated to English at M9 — the original
> French working document is kept as RESULTS.fr.md, with identical section
> numbering). §0: executive summary. §1-2: conventions and formats extracted
> from the sources (milestone M1), with precise references (paper, section,
> equation, table). §3: methodological decisions. §4-§8: M5-M7 results.
> §9: limitations. §10: what this work does NOT show. M1 extraction: 7
> subagents (one per source) + cross-checking + adversarial counter-checks of
> the critical equations of the DESI DR2 paper (Eq. 22, Eqs. 35-36, priors,
> Tables 5-6): 6/6 claims confirmed digit by digit, Eqs. (35)-(36) against
> the raw LaTeX. Traceability: every load-bearing figure in this document is
> cross-checked against the committed run records results/*.json by a
> permanent test (tests/test_results_traceability.py).

## §0 — Executive summary

Pre-registered independent reproduction of the w0waCDM preference
(DESI DR2 BAO + compressed CMB + SNe) with a single pipeline — numeric
gates, seeds, priors and cuts committed before each run — followed by a
pre-registered low-z sensitivity profile. Three numbers tell the whole
story:

1. **The 5 published anchors are replicated** (gates G5.1b-G5.5b +
   ordering G5.6b: 6/6 green, pre-registered windows P4): Nσ = 1.66 /
   2.36 / 2.28 / 3.29 / 3.84 for BAO alone / +CMB / +Pantheon+ / +Union3 /
   +DES-SN5YR, against the published 1.7 / 2.4 / 2.8 / 3.8 / 4.2
   [Table 6]. The BAO+CMB anchor is exact (DESI publishes 2.4σ with the
   same compression): Δχ²_MAP = −8.023 vs the published −8.0. The +SNe
   arms sit below the published values by −0.52 / −0.51 / −0.36σ — the
   effect of the CMB compression, of the same order as the −0.7σ DESI
   measures itself (§6, §9.1).
2. **Low-z profile of the DES-SN5YR arm (M7)**: 3.84σ → 1.46σ once the
   z < 0.1 SNe are removed (1.54σ for DES-only), with the (w0, wa)
   best fits barely moving — BUT the targeted exclusion of the historical
   CfA+CSP surveys (Foundation kept) costs only −0.23σ. Pre-registered
   reading (§8): in our profile, the sensitivity comes from removing the
   entire z < 0.1 lever arm, not specifically the historical surveys.
3. **The Pantheon+ arm is robust to the same cuts**: 2.28σ → 2.01σ
   (z > 0.1), −0.08σ (CfA+CSP), −0.13σ (z > 0.025) (§8).

These numbers must be read together with the limitations of §9
(compressed CMB, calibrated P8 amendment, Union3, Pantheon+ covariance,
Dovekie) and the negative scope of §10 — in particular: this work does
not adjudicate between evolving dark energy and SNe systematics, and it
tests no photometric calibration.

## §1 — DESI DR2 conventions (arXiv:2503.14738v3, published PRD 112, 083515)

### 1.1 Significance convention (THE σ convention of this project)

- Statistic: `Δχ²_MAP ≡ −2Δln L`, evaluated at the **maximum a
  posteriori** points of each model (best fit refined with iminuit
  starting from the MAP points of the MCMC chains) [Section V].
- Conversion to σ: ΛCDM being nested in w0waCDM at (w0, wa) = (−1, 0),
  Wilks ⇒ Δχ²_MAP ~ χ²(2 dof) under H0. The published "Nσ" is defined by
  CDF_χ²(Δχ²_MAP | 2 dof) = P(|X| < N) for X ~ N(0,1) [Eq. (22), preamble
  of Section VII; Table 6 caption: "significance levels given 2 extra
  free parameters"].
- The paper also reports Δ(DIC) [Table 6] — we report ΔAIC/ΔBIC as a
  complement (SPEC objective), without claiming to replicate the DIC.

### 1.2 Priors (inherited from DESI DR1, arXiv:2404.03002 Table 2)

"Prior ranges on all sampled parameters match those given in Table 2 of
[DESI 2024 VI]" [Section V]. For our parameter space:

| Parameter | Prior | Source |
|---|---|---|
| w0 | U[−3, 1] | 2404.03002 Table 2; repeated in Section VII of 2503.14738 |
| wa | U[−3, 2], with w0 + wa < 0 | idem (matter domination at high z) |
| Ωm | U[0.01, 0.99] | 2404.03002 Table 2 |
| h·rd | U[10, 1000] Mpc ("background-only" fits) | 2404.03002 Table 2 |
| H0 | U[20, 100] km/s/Mpc (with external calibration) | 2404.03002 Table 2 |

### 1.3 Treatment of r_d

- BAO alone: **no r_d computation** — direct sampling of (Ωm, h·rd);
  r_d is absorbed into the free parameter h·rd [Section V].
- Calibrated BAO (BBN/CMB): sampling of (H0, ωb…), r_d computed by the
  Boltzmann code (CAMB via Cobaya) [Section V]. DESI uses no fitting
  formula for r_d. BBN prior: ωb = 0.02218 ± 0.00055
  [Eq. (14), Section IV.1; Schöneberg 2024, arXiv:2401.15054].
- Consequence for us (Boltzmann out of scope): see the CMB choice in
  §2.5 — the BAO-only arm is exact (h·rd free); the CMB arms require a
  published fitting formula for r_d (and z*, r_s(z*)), decided at the
  M1 GO.

### 1.4 "CMB" in the DESI DR2 sense

- Published baseline: Planck TT/TE/EE (SimAll + Commander ℓ<30, CamSpec
  PR4 ℓ≥30) + Planck+ACT DR6 lensing [Section IV.2]. That is full CMB —
  outside our scope (SPEC).
- **Compressed alternative published by DESI themselves**: correlated
  Gaussian prior on (θ*, ωb, ωbc), "more model-independent",
  Appendix A:
  - means (θ*, ωb, ωbc) = (0.01041, 0.02223, 0.14208) [Eq. (35)];
  - covariance C = 10⁻⁹ ×
    [[0.006621, 0.12444, −1.1929],
     [0.12444, 21.344, −94.001],
     [−1.1929, −94.001, 1488.4]] [Eq. (36)];
  - methodological grounding: Lemos & Lewis 2023 (arXiv:2302.12911).
  - Adversarial verification (second agent, reading the raw LaTeX via
    alttext): Eqs. (35)-(36) confirmed entry by entry, signs and
    exponent included; ordering (θ*, ωb, ωbc) confirmed; it is indeed θ*
    (≈ 0.0104 rad), not 100θ*.
  - **Precision caveat — RESOLVED**: the paper prints θ* = 0.01041
    (5 decimals) while σ(θ*) ≈ 2.6×10⁻⁶. The full-precision value was
    found in the official DESI DR2 products (Cobaya yaml of the
    published chains, data.desi.lbl.gov, cross-checked on two
    independent files): means (0.01041027, 0.02223208, 0.14207901) and
    the full covariance — see PREREGISTRATION.md P1, SHA256 pinning
    at M2.
  - **Trap**: the paper also contains a distinct θ*-ONLY prior
    (100θ* = 1.04110 ± 0.00053, width inflated by ~75 %) — never to be
    confused with the 3D compressed prior used here.
- Decisive point: the line "DESI+(θ*, ωb, ωbc)_CMB" appears in the
  published Table 6 (Δχ²_MAP = −8.0, 2.4σ) → an EXACT anchor for our
  compressed pipeline on the BAO+CMB combination, with no approximation
  on our side.

### 1.5 Published values to replicate (M5 anchors)

Δχ²_MAP / significance [Table 6] and posteriors (marginalized means ±
68 % [Table 5]):

| Combination | Δχ²_MAP | σ | w0 | wa |
|---|---|---|---|---|
| DESI alone | −4.7 | 1.7σ | −0.48 +0.35/−0.17 | < −1.34 (68 %) |
| DESI+(θ*,ωb,ωbc)_CMB | −8.0 | 2.4σ | — | — |
| DESI+CMB (full) | −12.5 | 3.1σ | −0.42±0.21 | −1.75±0.58 |
| DESI+CMB+Pantheon+ | −10.7 | 2.8σ | −0.838±0.055 | −0.62 +0.22/−0.19 |
| DESI+CMB+Union3 | −17.4 | 3.8σ | −0.667±0.088 | −1.09 +0.31/−0.27 |
| DESI+CMB+DESY5 | −21.0 | 4.2σ | −0.752±0.057 | −0.86 +0.23/−0.20 |

Without CMB [Table 6]: DESI+Pantheon+ 1.7σ; DESI+Union3 2.7σ; DESI+DESY5
3.3σ. (ΛCDM, context: BAO-CMB tension 2.3σ [Section VI].)

### 1.6 DR2 BAO measurements [Table 4, Section III.3]

7 effective points: BGS z=0.295 (D_V/r_d); LRG1 z=0.510, LRG2 z=0.706,
LRG3+ELG1 z=0.934, ELG2 z=1.321, QSO z=1.484, Lyα z=2.330 (correlated
D_M/r_d and D_H/r_d). Values: see §2.1 (bao_data files) — agreement
verified digit by digit between Table 4 and the files (cross-check: two
agents, two independent sources).

### 1.7 Pre-recombination formulas and neutrino convention

- The paper provides its own scaling formula for r_d [Section I,
  Eq. (2)]: r_d = 147.05 Mpc · (ω_b/0.02236)^−0.13 · (ω_bc/0.1432)^−0.23 ·
  (Neff/3.04)^−0.1, "scaled to the best-fit values from Planck".
- Main fitting formula of our pipeline: Aubourg et al. 2015
  [arXiv:1411.1074, Eq. (16), documented precision 0.021 %]; z* for θ*:
  Hu & Sugiyama 1996 [astro-ph/9510117, App. E, Eq. (E-1)]. Details,
  verbatim constants and limitations: PREREGISTRATION.md P2.
- Baseline neutrinos [Section V + official chain.input.yaml]:
  Σmν = 0.06 eV (one massive state), Neff = 3.044; Ωm includes
  non-relativistic neutrinos; ωbc = ωb + ωc excludes them [Section I,
  Eq. (6)].

### 1.8 The low-z test done by DESI themselves

"The constraining power of SNe in measuring the equation of state comes
primarily from the comparison of low-redshift (z<0.1) and high redshift
(z>0.1) supernovae" [Section VII.3]. DESI tests the exclusion of the
z<0.1 SNe from DESY5 [Figure 14, central panel]: enlarged uncertainties,
reduced significance, (w0, wa) best fits "far from ΛCDM". Efstathiou
[arXiv:2408.07175] is cited, as is the response by Vincenzi et al.
[arXiv:2501.06664] [Section VII.3].

## §2 — Data, formats, and the critical literature

### 2.1 BAO: CobayaSampler/bao_data, folder desi_bao_dr2/

- 16 files, 8 pairs `*_mean.txt` / `*_cov.txt` (the ALL_GCcomb file =
  the 13 concatenated points + block-diagonal 13×13 covariance; blocks
  verified identical to the per-tracer files).
- Mean format: 3 columns `z value observable` (DV_over_rs, DM_over_rs,
  DH_over_rs), 1 comment line. **Verified trap: for Lyα (z=2.33), the
  order is DH then DM, inverted with respect to the other slices.**
- Cov format: full matrix as text, ordering = the mean file's row order.
- Reference likelihood (cobaya `bao.desi_dr2`, class `desi_bao_all`):
  pure Gaussian, logp = −0.5·xᵀC⁻¹x, x = theory − measurement;
  `rs_fid: 1` (data already in r_d units) [cobaya base_classes/bao.py +
  desi_bao_all.yaml, verified verbatim].
- Pinning: the folder comes from a single commit
  `b7b8a36e9bccb063081f811f323cada21ab5fbdd` (2025-03-20) = tag **v2.6**;
  current master (`bb0c1c9…`) strictly identical. Raw URLs pinned on
  v2.6; `+` encoded `%2B`. SHA256 computed at download time (M2).

### 2.2 Pantheon+ SNe (PantheonPlusSH0ES/DataRelease, mastered in P0)

- `Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat`: 47 named
  columns (CID, IDSURVEY, zHD/zCMB/zHEL, m_b_corr, …); 1701 rows.
- `Pantheon+SH0ES_STAT+SYS.cov`: first line = dimension (1701), then
  N² values (full matrix, sequential read).
- Cosmology cut: strict zHD > 0.01 (→ 1590 of 1701 SNe) — M1
  reservation CLOSED (M9), rule confirmed at the sources: cobaya
  `sn.pantheonplus` (the "without SH0ES" likelihood, i.e. the DESI
  usage) reads the zHD column (mapping `file_cols ["m_b_corr", "zhd",
  "zhel"]` → `["mag", "zcmb", "zhel"]`) and masks `zcmb > 0.01`;
  identical rule in the official release likelihood,
  `Pantheon+_only_cosmosis_likelihood.py` (`ww = data['zHD'] > 0.01`,
  pinned commit c447f0f); Cepheid-host calibrators remain ordinary SNe
  there. The 1580 count (Keeley et al. 2024) is the SH0ES-MODE count:
  the `Pantheon+SH0ES` likelihood selects `(zHD > 0.01) | IS_CALIBRATOR`
  and compares the calibrators to the Cepheid distances, not to the
  cosmological model — leaving 1580 Hubble-diagram SNe (1590 − 10
  calibrators at zHD > 0.01; verified on the pinned file: 77 calibrators
  in total, 10 above the cut). NB: the string "1580" does not appear in
  Brout et al. 2022 (checked on the arXiv and ApJ texts) — it is the
  count of Keeley et al. 2024.
- Published anchors [Brout et al. 2022, arXiv:2202.04077, Table 3]:
  SN-alone FlatΛCDM Ωm = 0.334 ± 0.018; FlatwCDM (Ωm, w) =
  (0.309 +0.063/−0.069, −0.90 ± 0.14); Flatw0waCDM w0 = −0.93 ± 0.15,
  wa = −0.1 +0.9/−2.0.
- Literature: Keeley, Shafieloo & L'Huillier [arXiv:2212.07917,
  published Universe 2024] — χ²_ΛCDM = 1387.10 for 1580 points, >3.9σ
  too low against 10 000 mocks ⇒ Pantheon+ errors overestimated by ~7 %
  [Sec. 2, Fig. 1]. No published number for the effect on the w0wa
  preference. → M8 limitation, no correction on our side (zero tuning).

### 2.3 DES-SN5YR SNe (des-science/DES-SN5YR + Zenodo 12720778)

- **Critical pinning: tag v1.2 (commit `95cf14c8e057ef3c2d6bf72ae22cf0d5
  ee796e1c`)** = the state of the 2024 paper (arXiv:2401.02929). The main
  branch has moved to the "Dovekie" re-analysis (Popovic et al. 2026,
  arXiv:2511.07517) — different files (1820 SNe). Zenodo:
  DES-SN5YR-1.2.zip (1.53 GB, published MD5
  `9019a6ddc569553bc323e9e1b68a55bf`; SHA256 computed by us).
- `4_DISTANCES_COVMAT/DES-SN5YR_HD.csv`: CSV, 1829 SNe (1635 DES
  IDSURVEY=10 + 194 low-z: CfA 61-66, FOUND 150), columns CID, IDSURVEY,
  zCMB, zHD, zHEL, MU, MUERR_FINAL (MU calibrated to H0=70).
- `STAT+SYS.txt.gz`: 1st line = N (1829), then N² values ONE PER LINE
  (full matrix). **Verified trap: STATONLY is ~zero; the total
  covariance = STAT+SYS + diag(MUERR_FINAL²)** [README 4_DISTANCES_COVMAT
  + `5_COSMOLOGY/SN_only_cosmosis_likelihood.py`: `C[i,i] += err²`].
- Official likelihood: analytic marginalization of the offset M
  (degenerate with H0), χ² = Δμᵀ C⁻¹ Δμ modified [paper Section 3,
  Eq. 5; official script] — the same machinery as our MarginalizedChi2
  (P0).
- Official chains (exact M3 anchor): `5_COSMOLOGY/chains/fw0wacdm/`
  etc., CosmoSIS format, columns omega_m, h0, w, wa,
  supernova_params--m, prior, like, post, **weight** (weighted
  polychord); SN and SN+planck variants, ×2 samplers.
- Published best fits [arXiv:2401.02929, Table 2]: SN-alone FlatΛCDM
  Ωm = 0.352 ± 0.017; FlatwCDM (0.264 +0.074/−0.096, −0.80 +0.14/−0.16);
  Flatw0waCDM SN-alone (Ωm, w0, wa) = (0.495, −0.36, −8.8) — a highly
  degenerate posterior; the SN-alone anchor is taken against the chains,
  not this point.

### 2.4 Union3 SNe (rubind/union3_release + cobaya sn_data) — VERDICT: feasible

- Exactly replicable DESI usage: cobaya `sn.union3` reads
  `sn_data/Union3/lcparam_full.txt` (22 nodes, bin00-bin21, z = 0.05 to
  2.26226, column mb = distance modulus with an arbitrary zero point) +
  `mag_covmat.txt` (22×22), marginalized offset (`use_abs_mag: False`).
- Redundant sources: repo rubind/union3_release (Zenodo 14090777) — FITS
  `mu_mat_union3_cosmo=2_mu.fits` (equivalent, inverse covariance) +
  full posterior chains (`all_samples_union3_cosmo=2.npz`).
- Critique of the format [Kim, arXiv:2412.14181]: the published product
  is a spline POSTERIOR (22 nodes) whose implicit prior is not flat in
  (Ωm, w0, wa) [Sec. 3]; DESI uses it as-is as a likelihood without
  dividing by the prior [Sec. 5]; effect judged "inconsequential" by Kim
  himself. → We replicate the DESI usage (the objective is
  reproduction) and document this limitation in M8.
- Decision (SPEC "best-effort"): Union3 INCLUDED, treated identically to
  the DESI usage via the cobaya sn_data files.

### 2.5 CMB compression — sourced options (decision at the M1 GO)

- **Option A (proposed): DESI's own compression** — Gaussian prior on
  (θ*, ωb, ωbc), Eqs. (35)-(36) of 2503.14738 Appendix A (§1.4).
  Advantages: (i) it is THE version published by the very collaboration
  whose result we reproduce; (ii) exact published anchor (2.4σ,
  Table 6); (iii) validated as nearly independent of late-time physics
  [Lemos & Lewis 2023]. Cost: θ* and the conversion (ωb, ωbc) → r_d
  require published pre-recombination fitting formulas (r_s(z_drag),
  z*, r_s(z*)) — to be extracted from their sources at the GO
  (candidates: Aubourg et al. 2015 / Hu & Sugiyama 1996 formulas, exact
  references pinned before M2, never from memory).
- Option B: classical distance priors (R, l_A, ωb, n_s), Planck 2018
  TT,TE,EE+lowE [Chen, Huang & Wang, arXiv:1808.05724, Table 1,
  Eqs. (1)-(2)]: R = 1.7502 ± 0.0046, l_A = 301.471 ± 0.089,
  ωb = 0.02236 ± 0.00015, n_s = 0.9649 ± 0.0043 + published correlation
  matrix. Advantages: the historical standard, complete verbatim values.
  Drawbacks: not DESI's compression, no published anchor in Table 6,
  same need for pre-recombination formulas.
- Limitation (both options): our σ for the SNe combinations will differ
  from the published ones (full CMB there). Expected gap, measured by
  DESI: 2.4σ (compressed) vs 3.1σ (full) on DESI+CMB — folded into the
  M5 gates.

### 2.6 The critics' low-z cuts (basis of the M7 pre-registration)

- Efstathiou [arXiv:2408.07175]: window 0.02 ≤ zHD ≤ 1.2 [Sec. 2];
  low-z/high-z offset ~0.04 mag on the SNe common to DES5Y/Pantheon+
  (Foundation −0.051±0.007; combined low-z −0.0482±0.0057 [Sec. 3,
  Table 1]); subtracting 0.04 mag from the DES5Y low-z makes the w0wa
  preference non-significant (Δχ² ~2.5) [Sec. 3, Fig. 5].
- Huang, Cai & Wang [arXiv:2502.04212]: low-z subsamples in question
  CSP (8), CfA (68), Foundation (118) vs 1635 DES high-z; ~0.043 mag
  intercept discordance [Sec. III.2]; CMB+DESI+DESY5 significances
  3.5-3.7σ → ~1.5-1.6σ after correction [Tables 1-2].
- DES response [Popovic et al., arXiv:2511.07517, MNRAS 2026]: full
  recalibration (Dovekie, DA white-dwarf anchoring), F99 bug fixed
  (~0.01 mag), systematics weights fixed (sum 0.81 → 1) [Sec. 5,
  App. A]. Result: preference reduced 4.2σ → **3.2σ** (DES+CMB+DESI DR2)
  [abstract; w0 = −0.803±0.054, wa = −0.72±0.21]. Only cut: z > 0.025
  (peculiar velocities) [Sec. 2.2]; no z_min variation test in that
  paper.
- Identification in our files: Pantheon+ and DES-SN5YR share the
  IDSURVEY codes (CSP=5 for P+, CfA=61-66, Foundation=150, DES=10;
  miscellaneous P+ low-z: 50, 51, 56, 57, 18). Candidate M7 cuts (frozen
  at the M1 GO): (a) z > 0.1 (mirror of DESI Fig. 14 and Efstathiou);
  (b) exclusion by IDSURVEY of the historical samples (CfA+CSP) keeping
  Foundation; (c) exclusion of all external low-z (pure DES,
  IDSURVEY=10; and P+ z>0.1); (d) control: z > 0.025 (Dovekie cut).

### 2.7 Divergences found between sources ("STOP on divergence" rule)

No blocking convention divergence. Three documented discrepancies, all
explained: (i) the DES repo's main ≠ 2024 paper → resolved by pinning
v1.2; (ii) DESY5 significance 4.2σ (DR2) vs 3.2σ (Dovekie 2026) → two
different releases, we replicate DR2/v1.2 and cite Dovekie as context;
(iii) CMB compression values of 2509.21491 (App. C) ≠ Eqs. (35)-(36) →
dataset variants (P-ACT vs DESI baseline), we use Eqs. (35)-(36) under
Option A.

## §3 — M3-M4 methodological decisions (documented, none silent)

1. **Symmetrization of the Pantheon+ covariance**: the published
   STAT+SYS file carries last-printed-digit rounding asymmetries
   (778 entries out of 2 893 401, max |C−Cᵀ| = 3×10⁻⁸); symmetrized
   ½(C+Cᵀ) under a hard 10⁻⁷ guard (the official consumers never check
   symmetry). A file artifact, not a physics choice.
2. **G3.3 priors**: extracted from the header of the pinned official
   chain (omega_m U[0.01,0.99], h0 U[0.3,1], w U[−5,1], wa U[−20,10],
   m U[−1,1]) — the gate is evaluated with THESE priors. The (m, h0)
   pair sampled by DES is replaced by the analytic marginalization of
   the offset (both constrain only the same combination; boundary
   effects negligible, the offset posterior is well interior).
3. **SN-only and BAO-only model without radiation**: E² = Ωm(1+z)³ +
   (1−Ωm)f_DE — DESI's background-only parametrization (Ωm, h·rd) does
   not even allow specifying Ωr; effect ~10⁻⁴ mag on μ(z≤1.1),
   negligible against the gate tolerances (0.010 on Ωm, 0.2σ).
4. **Domain of the r_d cross-check** (Aubourg Eq. 16 vs DESI Eq. 2,
   tolerance 0.3 %): evaluated on ±5σ of the Gaussian CMB prior, the
   only domain where r_d is used (the BAO-only arm samples h·rd
   freely). Measured: 0.21 % at ±5σ; the two power laws diverge far from
   the calibration point (0.70 % at the arbitrary corner ωbc = 0.10).
5. **Fast integrators**: r_s(z*) and D_M(z*) by Simpson on fixed grids
   (substitutions a = x² and log(1+z)), validated < 10⁻⁷ relative
   against adaptive quad (permanent test).
6. **Neutrinos**: the ν sector mirrors astropy (Komatsu 2011 Eq. 26,
   identical constants, oracles < 10⁻⁶ up to z = 1100); official DESI
   mapping ωbc = Ωm h² − Σmν/93.14 (pinned yaml, verified exact on the
   official chains to within 9×10⁻⁹); Aubourg's ων (0.0107·Σmν) and
   DESI's (Σmν/93.14) each used inside its formula of origin.

## §4 — M5 results: fits of the 5 combinations × 2 models (frozen pipeline)

MAP best fits (seeded Sobol multi-start Nelder-Mead, 24 ΛCDM /
40 w0waCDM, committed before the runs; convergence verified by audit:
4 independent optimizers agree to 2×10⁻⁷, start-point scatter ~10⁻¹³).
σ convention: Δχ²_MAP → χ²(2 dof) CDF → Gaussian equivalent [Eq. (22)] —
the conversion reproduces the 5 published pairs of Table 6.

| Arm | n | χ²_ΛCDM | χ²_w0wa | Δχ²_MAP | Nσ | published | window | gate |
|---|---|---|---|---|---|---|---|---|
| BAO alone | 13 | 10.271 | 5.619 | −4.652 | **1.66** | 1.7 | [1.5, 1.9] | G5.1 PASS |
| BAO+CMB | 16 | 12.761 | 6.784 | −5.977 | **1.96** | 2.4 (exact anchor) | [2.1, 2.7] | G5.2 **FAIL** |
| BAO+CMB+Pantheon+ | 1606 | 1418.52 | 1412.12 | −6.406 | **2.05** | 2.8 (full CMB) | [1.8, 3.1] | G5.3 PASS |
| BAO+CMB+Union3 | 38 | 41.163 | 29.033 | −12.131 | **3.05** | 3.8 (full CMB) | [2.8, 4.1] | G5.4 PASS |
| BAO+CMB+DES-SN5YR | 1845 | 1662.20 | 1645.74 | −16.456 | **3.65** | 4.2 (full CMB) | [3.2, 4.5] | G5.5 PASS |

G5.6 (ordering): 2.05 (P+) < 3.05 (Union3) < 3.65 (DESY5) — PASS.

ΔAIC = Δχ²_MAP + 4; ΔBIC = Δχ²_MAP + 2 ln n: BAO −0.65/+0.48;
BAO+CMB −1.98/−0.43; +P+ −2.41/+8.36; +Union3 −8.13/−4.86;
+DES −12.46/−1.42 → under BIC (more punitive), only Union3 keeps a clear
preference for w0waCDM; reported as a complement, as planned.

Exact-replication landmarks: BAO-only ΛCDM (Ωm = 0.2975,
h·rd = 101.54 Mpc) = the published DESI DR2 values digit for digit; the
SNe arms' w0 best fits are close to the published ones (P+ −0.864 vs
−0.838; Union3 −0.704 vs −0.667; DES −0.778 vs −0.752).

**Measured compression effect (P4 / GO M1.2a)** — gap Nσ_pipeline −
Nσ_published on the +SNe arms (full CMB at DESI, compressed here):
P+ **−0.75σ**, Union3 **−0.75σ**, DES **−0.55σ** — of the same order as
the −0.7σ DESI measures itself on BAO+CMB (2.4σ compressed vs 3.1σ
full). NB: this "compression effect" as measured here ALSO contains the
θ* bias identified by the audit (§5); the purely-compression part and
the θ* part cannot be separated without redoing the fits with an exact
θ*.

## §5 — Audit of gate G5.2 (pre-registered: failure ⇒ STOP, audit, never
## a silent relaxation)

G5.2 is the EXACT anchor (DESI publishes 2.4σ with the SAME
compression). Audit with 5 independent probes (multi-agent workflow,
scripts and outputs under `results/audit/`):

- **Minimizer cleared** (probe C): seeded differential_evolution,
  Nelder-Mead (from the M5 best fit AND from the official point),
  Powell — all converge to χ²_ΛCDM = 12.760649, χ²_w0wa = 6.783639
  (deviations ≤ 2×10⁻⁷); scatter of the 24/40 starts ~10⁻¹³. The
  simplex's inf−inf warnings are cosmetic.
- **Exact conventions and constants** (probe D): HS96 (E-1), Aubourg
  Eq. (16), EH98 Eq. (5), prior means/covariance, inflate_cov false,
  mnu/93.14 mapping — all verified character by character against the
  sources and the official yaml. NO transcription bug.
- **BAO arm cleared** (probes A, B): our χ²_BAO recomputed at the
  official chains' points (per-point chi2__BAO columns) agrees to
  +0.13/+0.24 on average, fully explained by Aubourg's r_d being low by
  −0.028 % (vs the chains' CAMB rdrag, near-constant, σ ≈ 10⁻⁵
  relative) — differential effect < 0.05 on Δχ².
- **Cause identified: θ* bias of the HS96+EH98 model** (probes A, D):
  our θ* is systematically low by −0.10 to −0.13 % (−4.7 to −5.3σ of
  the prior!), with a residual parameter dependence (scatter 0.033 %);
  our χ²_CMB recomputed at the official chains' points is inflated by
  +30 to +34 on average. The official likelihood computes θ* with CAMB
  1.5.4 (full recombination); HS96 is percent-level accurate — 40× the
  prior width. This is EXACTLY the pre-registered limitation P2, which
  designated G5.2 as its empirical bound.
- **Quantified attribution** (probe E, a diagnostic — NOT a
  correction): shifting the prior's θ* mean by the measured bias
  (−1.013×10⁻⁵), the SAME fits give Δχ²_MAP = −7.544 → 2.27σ (inside
  the [2.1, 2.7] window; 77 % of the gap recovered), and the w0waCDM
  best fit joins the official margestats (h 0.639 vs 0.637; w0 −0.461
  vs −0.43±0.22; wa −1.590 vs −1.72±0.64). The residue (~23 %) is
  consistent with the bias's parameter dependence + r_d (0.028 %) +
  rounding of the published anchor.
- **Cross-validation of the anchor** (probe A): reconstructed from the
  official chains themselves (min of chi2__BAO+chi2__CMB_compressed),
  the official Δχ²_MAP = −7.965 ≈ the published −8.0.

**Status**: G5.2 remains FORMALLY FAILED with the frozen pipeline — no
silent recalibration (P2/GO M1.2b). The cause is attributed, with
mechanism and quantification, to the fidelity of the analytic θ*
(HS96+EH98) against σ(θ*)/θ* = 2.5×10⁻⁴, not to a bug. Any remediation
(CAMB θ*, a calibrated pre-registered correction, or acceptance as a
limitation) is a methodological decision requiring an explicit GO.

→ Téo's decision (GO of 2026-06-11): calibrated amendment P8
(PREREGISTRATION.md P8 — full transparency: decided AFTER the audit,
same status as the P0 project's Keeley recalibration). See §6.

## §6 — P8-corrected M5 results (gates G5.xb, same windows)

P8 amendment: two multiplicative constants on the analytic outputs of
the CMB arms, calibrated on the pinned official chains —
κ_r = 1.000279376 (Aubourg r_d), κ_θ = 1.001314308 (θ*). The
post-correction residual scatter (7.6×10⁻⁶ ≈ 0.03σ_prior) shows a
constant captures nearly all of the bias; nothing else changed
(verifiable: only the entry points `DESIParams.r_drag_mpc` and
`DESIParams.theta_star` apply κ). The raw table (§4) remains the output
of the purely analytic pipeline.

| Arm | χ²_ΛCDM | χ²_w0wa | Δχ²_MAP | Nσ | published | window | gate |
|---|---|---|---|---|---|---|---|
| BAO alone | 10.271 | 5.619 | −4.652 | **1.66** | 1.7 | [1.5, 1.9] | G5.1b PASS |
| BAO+CMB | 15.151 | 7.129 | **−8.023** | **2.36** | 2.4 / −8.0 (exact anchor) | [2.1, 2.7] | G5.2b PASS |
| BAO+CMB+Pantheon+ | 1420.95 | 1413.37 | −7.574 | **2.28** | 2.8 (full CMB) | [1.8, 3.1] | G5.3b PASS |
| BAO+CMB+Union3 | 43.584 | 29.790 | −13.794 | **3.29** | 3.8 (full CMB) | [2.8, 4.1] | G5.4b PASS |
| BAO+CMB+DES-SN5YR | 1664.65 | 1646.67 | −17.984 | **3.84** | 4.2 (full CMB) | [3.2, 4.5] | G5.5b PASS |

G5.6b (ordering): 2.28 (P+) < 3.29 (Union3) < 3.84 (DESY5) — PASS.
**6/6 gates green.** The BAO-only arm is identical to §4 (P8 does not
touch it, as declared).

Striking replication points:
- G5.2b: Δχ²_MAP = −8.023 vs the published −8.0; w0waCDM best fit
  (Ωm = 0.3509, h = 0.6372, w0 = −0.445, wa = −1.645) vs the official
  margestats (0.353, 0.637, −0.43 ± 0.22, −1.72 ± 0.64); ΛCDM best fit
  χ² = 15.151 vs 15.145 reconstructed from the official chains.
- SNe arms, (w0, wa) best fits vs published [Table 5]: P+ (−0.853,
  −0.52) vs (−0.838, −0.62); Union3 (−0.686, −0.99) vs (−0.667, −1.09);
  DES (−0.766, −0.78) vs (−0.752, −0.86).

**Compression effect re-measured cleanly (post-P8)** —
Nσ_pipeline − Nσ_published(full CMB): P+ **−0.52σ**, Union3 **−0.51σ**,
DES **−0.36σ**, to be compared with the **−0.7σ** DESI measures on
BAO+CMB (2.4σ compressed vs 3.1σ full). The effect is systematically
attenuating and of the same order; it is smaller on the arms where the
SNe dominate the (w0, wa) information — expected, the compression only
degrades the CMB channel.

ΔAIC/ΔBIC (k = 2; n = the arm's data points): BAO −0.65/+0.48; BAO+CMB
−4.02/−2.48; +P+ −3.57/+7.19; +Union3 −9.79/−6.52; +DES −13.98/−2.94.

## §7 — M6: w0waCDM MCMC posteriors (emcee, P8 pipeline)

Settings committed before the runs (P7); convergence required
(n_steps − burn) > 50τ everywhere — the first attempt failed this
criterion on BAO+CMB (50τ = 9312 > 8000) and the CMB arms' chains were
lengthened (the criterion itself never moved); seeds derived from
20260611; walkers initialized in a ball around the M5b MAP. Artifacts:
results/m6_mcmc.json, results/chains/*.npz (flattened, thinned τ/2),
results/figures/m6_corner_*.png.

Marginalized means ± standard deviation vs published [Table 5; full CMB
at DESI except BAO alone; BAO+CMB compared to the official compressed
margestats]:

| Arm | w0 | w0 published | wa | wa published | d((w0,wa), ΛCDM) eucl. / Mahal. |
|---|---|---|---|---|---|
| BAO alone | −0.476 ± 0.262 | −0.48 +0.35/−0.17 | −1.660 ± 0.963 | < −1.34 (68 %) | 2.84 / 3.20 |
| BAO+CMB | −0.430 ± 0.217 | −0.43 ± 0.22 (official compressed) | −1.709 ± 0.633 | −1.72 ± 0.64 | 1.74 / 2.60 |
| +Pantheon+ | −0.848 ± 0.056 | −0.838 ± 0.055 | −0.552 ± 0.220 | −0.62 +0.22/−0.19 | 0.54 / 2.65 |
| +Union3 | −0.675 ± 0.090 | −0.667 ± 0.088 | −1.041 ± 0.310 | −1.09 +0.31/−0.27 | 1.04 / 3.50 |
| +DES-SN5YR | −0.761 ± 0.058 | −0.752 ± 0.057 | −0.806 ± 0.239 | −0.86 +0.23/−0.20 | 0.81 / 4.09 |

Findings: (i) the compressed BAO+CMB posterior reproduces the official
margestats to the 2nd decimal on both parameters AND their widths;
(ii) on the +SNe arms, despite the compressed CMB, the marginalized
(w0, wa) means and σ match the published full-CMB values to ±0.01 on w0
(the compression effect degrades the Δχ²_MAP, not appreciably the w0/wa
margins); (iii) the distance of the MAP to (−1, 0) is given in Euclidean
and in 2D Mahalanobis form (marginal (w0, wa) covariance of the chain) —
a metric distinct from the Eq. (22) Nσ convention, reported
descriptively (SPEC M6).

## §8 — M7: low-z sensitivity profile (P5 cuts, CLOSED at the M1 GO)

P8 pipeline, same engine and numbers of starts as M5b; baselines = the
full arms of §6; table metric FROZEN (P5); SHA256 of each subsample
recorded in results/m7_cuts.json. Cuts: C-a z > 0.1; C-b exclusion of
CfA (IDSURVEY 61-66) + CSP (5), Foundation (150) and miscellaneous P+
low-z kept; C-c pure DES (IDSURVEY = 10) / P+ z > 0.1; C-d z > 0.025
(Dovekie control).

**BAO+CMB+Pantheon+** (baseline: N = 1590, Δχ²_MAP = −7.574, 2.279σ,
w0 = −0.853, wa = −0.522):

| Cut | N_SNe | Δχ²_MAP | Nσ | ΔNσ | w0_MAP | wa_MAP | Δw0 | Δwa |
|---|---|---|---|---|---|---|---|---|
| C-a | 960 | −6.247 | 2.014 | −0.265 | −0.780 | −0.715 | +0.073 | −0.193 |
| C-b | 1357 | −7.155 | 2.198 | −0.081 | −0.845 | −0.544 | +0.008 | −0.021 |
| C-c | 960 | −6.247 | 2.014 | −0.265 | −0.780 | −0.715 | +0.073 | −0.193 |
| C-d | 1322 | −6.921 | 2.152 | −0.127 | −0.852 | −0.522 | +0.001 | −0.000 |

**BAO+CMB+DES-SN5YR** (baseline: N = 1829, Δχ²_MAP = −17.984, 3.837σ,
w0 = −0.766, wa = −0.778):

| Cut | N_SNe | Δχ²_MAP | Nσ | ΔNσ | w0_MAP | wa_MAP | Δw0 | Δwa |
|---|---|---|---|---|---|---|---|---|
| C-a | 1632 | −3.887 | 1.464 | **−2.373** | −0.818 | −0.616 | −0.052 | +0.162 |
| C-b | 1753 | −16.160 | 3.607 | −0.230 | −0.755 | −0.806 | +0.011 | −0.028 |
| C-c | 1635 | −4.184 | 1.540 | **−2.297** | −0.811 | −0.639 | −0.045 | +0.139 |
| C-d | 1829 | −17.984 | 3.837 | ±0.000 | −0.766 | −0.778 | −0.000 | +0.000 |

Factual reading (no physics conclusion beyond the profile):

- The DES-SN5YR arm loses most of its preference as soon as the z < 0.1
  SNe (or all external low-z) are removed: 3.84σ → 1.46-1.54σ — a
  quantitative mirror of DESI's own test (Fig. 14, "enlarged
  uncertainties, reduced significance") and of the mechanism pointed
  out by Efstathiou: the (w0, wa) best fits move LITTLE (Δw0 ≈ −0.05,
  Δwa ≈ +0.15), it is the constraining power that collapses.
- By contrast, the targeted exclusion of the historical samples
  (CfA + CSP, Foundation kept — the test of 2502.04212) costs only
  −0.23σ: in OUR profile, the sensitivity comes from removing the
  entire z < 0.1 lever arm, not specifically the historical surveys.
- The Dovekie cut z > 0.025 is strictly neutral for DES (no SN of the
  release below z = 0.025 — consistency verified, ΔNσ = 0 exactly).
- The Pantheon+ arm is robust: 2.28σ → 2.01σ (z > 0.1), −0.08σ
  (CfA+CSP), −0.13σ (z > 0.025). Internal control: C-c(P+) ≡ C-a(P+)
  digit for digit, as expected by construction.

## §9 — Limitations (M8)

The pointwise methodological decisions (Pantheon+ covariance
symmetrization, radiation omitted from the SN/BAO-only backgrounds,
cross-check domains) are documented in §3; the six structural
limitations are these.

### 9.1 Compressed CMB vs full CMB — a measured effect

DESI combines its BAO with a full CMB likelihood (Planck PR4 + ACT
lensing); our pipeline uses the Gaussian compression (θ*, ωb, ωbc)
published by DESI themselves [Appendix A] (SPEC: no Boltzmann code).
The effect is not estimated, it is measured, and it has a published
yardstick: on BAO+CMB, DESI reports 2.4σ (compressed) against 3.1σ
(full), i.e. −0.7σ.

| Arm | Nσ pipeline (compressed, P8) | Nσ published | published reference | gap |
|---|---|---|---|---|
| BAO+CMB | 2.36 | 2.4 | compressed (exact anchor) | −0.04σ |
| BAO+CMB | — | 3.1 | full CMB (not replicated) | −0.7σ measured by DESI |
| BAO+CMB+Pantheon+ | 2.28 | 2.8 | full CMB | −0.52σ |
| BAO+CMB+Union3 | 3.29 | 3.8 | full CMB | −0.51σ |
| BAO+CMB+DES-SN5YR | 3.84 | 4.2 | full CMB | −0.36σ |

The gap is systematically attenuating, of the same order as the DESI
yardstick, and smaller on the arms where the SNe dominate the (w0, wa)
information. The marginalized (w0, wa) means and widths (M6, §7), on
the other hand, match the published full-CMB values to ±0.01 on w0: the
compression degrades the Δχ²_MAP, not appreciably the posteriors. Our
Nσ therefore compare to the published full-CMB headline numbers only
through this documented gap.

### 9.2 The calibrated P8 amendment — status owned

- The purely analytic pipeline (Aubourg Eq. 16 + HS96 + EH98) failed
  the exact-anchor gate G5.2 (1.96σ, window [2.1, 2.7]). The
  pre-registered audit (§5, 5 probes, artifacts in results/audit/)
  attributes the gap to the analytic θ* bias (−0.10 to −0.13 % ≈ −5σ of
  the prior, HS96 being percent-level accurate against
  σ(θ*)/θ* = 2.5×10⁻⁴) — no bug.
- The correction (P8): two multiplicative constants
  κ_r = 1.000279376 and κ_θ = 1.001314308, calibrated on the pinned
  official DESI chains, committed BEFORE the re-run, independent of the
  SNe data, of the model and of the M7 cuts. Residual scatter 7.6×10⁻⁶
  (≈ 0.03σ_prior): a constant captures nearly all of the bias.
- This is NOT a blind pre-registration: it was decided AFTER the G5.2
  failure and its audit (the same owned status as the P0 project's
  Keeley recalibration). The raw table (§4) and the formal G5.2 failure
  remain in the record; nothing is overwritten.
- Incident documented during the calibration: the naive root assignment
  ("the root closest to our raw value" when inverting the
  chi2__CMB_compressed quadratic) underestimated κ_θ by about 0.02 %
  (a low-root systematic); identified and replaced by a fixed-point
  iteration BEFORE the constants were committed
  [MILESTONES 2026-06-11, scripts/calibrate_p8.py,
  results/calibration_p8.json].

### 9.3 Union3: a posterior-spline product (Kim 2024)

The public Union3 product used by DESI (and therefore by us) is a
posterior binned on 22 spline nodes, not a per-SN likelihood; its
implicit prior is not flat in (Ωm, w0, wa) and DESI uses it as-is as a
likelihood [Kim, arXiv:2412.14181, Secs. 3 and 5 — an effect judged
"inconsequential" by Kim himself]. We replicate the DESI usage exactly
(cobaya sn_data files); the Union3 arm inherits this construction and
has no testable per-SN equivalent here (no M7 cut is possible on this
arm, incidentally).

### 9.4 Pantheon+ covariance (Keeley et al. 2024)

Keeley, Shafieloo & L'Huillier [arXiv:2212.07917, Universe 2024]
measure χ²_ΛCDM = 1387.10 for 1580 points, lower than 10 000 mocks at
> 3.9σ ⇒ Pantheon+ errors overestimated by about 7 %. No published
number for the effect on the w0wa preference; in line with the
zero-tuning rule, no correction is applied — our Pantheon+ results
(G5.3b, M6, M7) inherit the covariance as published.

### 9.5 Analytic θ*/z* → CAMB (future refinement)

The root of the bias corrected by P8 is structural: the Hu & Sugiyama
1996 z* is calibrated at the percent level (pre-RECFAST), 40× the θ*
prior width. The clean refinement — computing θ* (and r_d) with CAMB,
full recombination, like the official likelihood — is outside the v1
scope (SPEC: no Boltzmann); it is the first candidate for a v2, which
would make P8 obsolete.

### 9.6 Dovekie: the ground has already shifted (context, never an anchor)

We replicate the DR2 era by pre-registered decision (M1 GO: "anchors =
DR2 era exclusively"): DES-SN5YR pinned at tag v1.2 (the state of the
2024 paper), anchors = Tables 5-6 of arXiv:2503.14738. Since then, DES
has published its own recalibration (Dovekie, Popovic et al. 2026,
arXiv:2511.07517): F99 bug fixed, systematics weights fixed, preference
reduced from 4.2σ to **3.2σ** on DES+CMB+DESI DR2 — by DES themselves.
Our DES-SN5YR numbers (3.84σ baseline, M7 profile) therefore describe
the v1.2/DR2-era release, not the 2026 state of the art.

## §10 — What this work does NOT show

1. **It does not adjudicate between "evolving dark energy" and "SNe
   systematics"**. A sensitivity profile locates the statistical lever
   arm; it does not identify a cause. That the DES arm's preference
   collapses without the z < 0.1 SNe is compatible both with a low-z
   systematic and with the loss of the genuine information those SNe
   carry (DESI makes the same observation, Section VII.3).
2. **It tests no photometric calibration**. No calibration refit, no
   examination of magnitudes or cross-survey offsets: Efstathiou's
   ~0.04 mag offset [2408.07175] and the intercept discordance of Huang
   et al. [2502.04212] are neither confirmed nor refuted here — our C-b
   only tests the consequence of exclusion, not the mechanism.
3. **Everything is conditional on the pinned DR2-era datasets and on
   the documented CMB compression**: bao_data v2.6, Pantheon+ c447f0f,
   DES-SN5YR v1.2, Union3 cobaya sn_data, DESI compressed CMB prior with
   the calibrated P8 amendment (§9.2). No validity is claimed for other
   releases (Dovekie, §9.6), for the full CMB (§9.1), or for
   parametrizations other than CPL.
4. **No physics conclusion** beyond: the published preference is
   reproduced within the pre-registered windows, and here is its low-z
   sensitivity profile (SPEC, out-of-scope).
