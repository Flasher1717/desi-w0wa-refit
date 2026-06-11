# PRÉ-ENREGISTREMENT — desi-w0wa-refit

> Gates chiffrés, coupures, métriques et seeds, committés AVANT tout run
> produisant un résultat. Validé par le GO M1 global de Téo (2026-06-11,
> consigné dans MILESTONES.md). Ce fichier ne se modifie plus après le
> premier run concerné par chaque section ; toute déviation est documentée
> dans RESULTS.md.

## P1 — Choix méthodologique CMB (décision GO M1)

- Compression DESI : prior gaussien sur (θ*, ωb, ωbc), moyennes et
  covariance des Eqs. (35)-(36) de arXiv:2503.14738v3 Appendix A
  (vérifiées sur LaTeX brut, voir RESULTS.md §1.4).
- θ* : RÉSOLU (condition GO M1.c, voie haute). Valeurs complètes extraites
  des produits officiels DESI DR2 (yaml Cobaya des chaînes publiées,
  contre-vérifiées identiques sur deux fichiers indépendants base/ et
  base_w_wa/) :
  - moyennes (θ*, ωb, ωbc) = (0.01041027, 0.02223208, 0.14207901)
  - covariance :
    [[6.6209942e-12, 1.24442058e-10, −1.19287532e-09],
     [1.24442058e-10, 2.13441666e-08, −9.40008323e-08],
     [−1.19287532e-09, −9.40008323e-08, 1.48841714e-06]]
  - source : data.desi.lbl.gov/public/papers/y3/bao-cosmo-params/cobaya/
    base_w_wa/desi-bao-all_CMB-compressed-theta-ombh2-ombch2/
    chain.updated.yaml (épinglé + SHA256 en M2 ; sha256sum officiel
    dr2_vac_dr2_bao-cosmo-params_v1.0.sha256sum disponible sur le site).
  - test de cohérence permanent : ces valeurs arrondies redonnent
    l'Eq. (35)-(36) du papier (vérifié : 0.01041, 0.02223, 0.14208 ;
    6.621e-12, 2.1344e-8, 1.4884e-6, etc.).
- PIÈGE documenté : le papier contient DEUX priors θ* distincts — le prior
  θ*-seul « 100θ* = 1.04110 ± 0.00053 » (largeur gonflée ~75 %, autour de
  l'Eq. (16) du papier) et le prior compressé 3D de l'Appendix A (le
  nôtre, 100θ* = 1.041027 ± 0.000257). Ne jamais les mélanger.
- Limitation assumée : les σ des bras +SNe différeront des publiés
  (full CMB chez DESI) ; l'écart est rapporté comme mesure (P4.b).

## P2 — Formules pré-recombinaison (condition GO M1.a — à compléter avant
## tout code CMB, depuis les papiers, jamais de mémoire)

- r_s(z_drag) : formule de fitting d'Aubourg et al. 2015 [arXiv:1411.1074,
  Eq. (16), Section II.B] :
  `r_d ≈ 55.154 · exp[−72.3 (ω_ν + 0.0006)²] / (ω_cb^0.25351 · ω_b^0.12807) Mpc`
  avec ω_cb = Ω_cb h² (baryons + CDM, SANS neutrinos), ω_b = Ω_b h²,
  ω_ν = 0.0107 (Σm_ν/1.0 eV) [texte suivant Eq. (16)].
  Précision documentée : 0.021 % pour Neff = 3.046, Σm_ν < 0.6 eV, ω_b et
  ω_cb à ±3σ de Planck [texte après Eq. (16)]. Convention r_d = CAMB
  (déclarée par le papier). Le papier ne fournit PAS de formule z_drag —
  Eq. (16) calibre r_d directement (z_drag implicite, convention CAMB).
- Cross-check r_d : formule du papier DESI DR2 lui-même [2503.14738v3,
  Eq. (2)] :
  `r_d ≈ 147.05 · (ω_b/0.02236)^−0.13 · (ω_bc/0.1432)^−0.23 · (Neff/3.04)^−0.1 Mpc`
  Test permanent : Aubourg Eq. (16) et DESI Eq. (2) concordent sur le
  domaine des priors (tolérance fixée par les précisions documentées,
  0.021 % + précision DESI Eq. (2) non publiée → tolérance 0.3 %).
- z* (pour θ*) : Hu & Sugiyama 1996 [astro-ph/9510117, App. E, Eq. (E-1)] :
  `z* = 1048 [1 + 0.00124 ω_b^−0.738][1 + g1 ω_m^g2]`,
  `g1 = 0.0783 ω_b^−0.238 / [1 + 39.5 ω_b^0.763]`,
  `g2 = 0.560 / [1 + 21.1 ω_b^1.81]`
  (ω_m = Ω_0 h² matière totale ; calibration HS96 : T0 = 2.726 K,
  fν = 0.405, Yp ≈ 0.23 ; validité « percent level » pour
  0.0025 ≲ ω_b ≲ 0.25, 0.025 ≲ ω_m ≲ 0.64 [App. E]).
- z_drag (information, non utilisé si Aubourg Eq. (16) suffit) :
  Eisenstein & Hu 1998 [astro-ph/9709112, Eq. (4)] :
  `z_d = 1291 ω_m^0.251 / [1 + 0.659 ω_m^0.828] · [1 + b1 ω_b^b2]`,
  `b1 = 0.313 ω_m^−0.419 [1 + 0.607 ω_m^0.674]`, `b2 = 0.238 ω_m^0.223`.
- r_s(z) : intégrale numérique r_s = ∫_z^∞ c_s dz'/H(z'),
  c_s = c/√(3(1+R)), R = 31.5 ω_b Θ_2.7^−4 (z/10³)^−1 [EH98, Eq. (5) et
  texte avant Eq. (6) ; T_CMB et la valeur de Θ_2.7 utilisées sont
  committées dans le code avec leur source].
- **Limitation pré-enregistrée (θ*)** : z* HS96 est calibré au niveau du
  pourcent (pré-RECFAST), plus grossier que σ(θ*)/θ* ≈ 2.5×10⁻⁴. Le pull
  induit sur le prior CMB est largement commun à ΛCDM et w0waCDM (atténué
  dans Δχ²_MAP) ; il est borné empiriquement par le gate G5.2 (ancrage
  publié 2.4σ avec la même compression) et mesuré par le test P6. Tout
  échec de G5.2 imputable à ce biais → STOP audit (GO M1.2b), jamais de
  recalibrage silencieux.
- Oracle permanent (test pytest, condition GO M1.b) : le papier DESI DR2
  ne publie pas de r_d fiduciel isolé dans les sections accessibles ; son
  point d'ancrage publié est l'Eq. (2) elle-même : r_d = 147.05 Mpc au
  point Planck (ω_b = 0.02236, ω_bc = 0.1432, Neff = 3.04)
  [2503.14738v3, Section I, « scaled to the best-fit values from
  Planck »]. Oracle : Aubourg Eq. (16) évaluée en ce point (avec
  ω_ν = 0.0107·0.06 = 0.000642, ω_cb = 0.1432) reproduit 147.05 Mpc à
  0.3 % (somme des précisions documentées/estimées des deux formules) ;
  oracle secondaire : concordance Aubourg/DESI Eq. (2) < 0.3 % sur tout le
  domaine des priors.
- Convention neutrinos baseline (extraite, [2503.14738v3, Section V +
  chain.input.yaml officiels : mnu 0.06, nnu 3.044]) : Σmν = 0.06 eV en UN
  état massif, Neff = 3.044, Ωm INCLUT les neutrinos non relativistes,
  ωbc = ωb + ωc les EXCLUT [Section I, Eq. (6)]. Le traitement neutrino
  exact de notre E(z) est fixé en M4 avec oracle astropy et documenté —
  jamais improvisé.
- Mapping officiel paramètres → densités (extrait du yaml DESI épinglé,
  vérifié localement dans data/desi_dr2_cmb_compressed_prior.yaml) :
  `omch2 = omm·(H0/100)² − mnu/93.14 − ombh2` (donc
  ωbc = Ωm h² − Σmν/93.14) ; bloc de sampling DESI pour ce bras :
  (H0, ombh2, w, wa, omm). Le yaml confirme aussi que la likelihood BAO
  officielle DESI lit les MÊMES fichiers que cobaya bao_data
  (`bao_data_v1p2/desi_gaussian_bao_ALL_GCcomb_{mean,cov}.txt`) et
  `inflate_cov: false`.

## P3 — Gates M3 (ancrages SNe-only, avant tout fit M5)

| Gate | Référence publiée | Critère |
|---|---|---|
| G3.1 Pantheon+ ΛCDM SN-only | Ωm = 0.334 ± 0.018 [Brout 2022, Table 3] | \|Ωm_pipeline − 0.334\| < 0.010 |
| G3.2 DES-SN5YR ΛCDM SN-only | Ωm = 0.352 ± 0.017 [DES 2024, Table 2] | \|Ωm_pipeline − 0.352\| < 0.010 |
| G3.3 DES chaînes officielles w0waCDM SN-only | chaînes v1.2 `fw0wacdm_SN.txt` (pondérées) | avec les MÊMES priors que la chaîne : \|mean_pipeline − mean_chaîne\| < 0.2·σ_chaîne sur chacun de (Ωm, w0, wa) |
| G3.4 Union3 | usage DESI répliqué (cobaya sn.union3) | validation structurelle (22 nœuds, covariance SPD) + cohérence du χ² best-fit ΛCDM avec G5.x en aval |

Conventions : Pantheon+ coupé à zHD > 0.01 ; DES covariance totale =
STAT+SYS + diag(MUERR_FINAL²) ; offset M marginalisé analytiquement
partout (pattern P0 MarginalizedChi2).

## P4 — Gates M5 (5 combinaisons × 2 modèles)

| Gate | Bras | Ancrage publié [2503.14738v3, Table 6] | Critère |
|---|---|---|---|
| G5.1 | BAO DR2 seul | 1.7σ (Δχ²_MAP = −4.7) | Nσ ∈ [1.5, 1.9] |
| G5.2 | BAO+CMB compressé | 2.4σ (Δχ²_MAP = −8.0, MÊME compression) | Nσ ∈ [2.1, 2.7] |
| G5.3 | BAO+CMB+Pantheon+ | 2.8σ (full CMB) | Nσ ∈ [1.8, 3.1] |
| G5.4 | BAO+CMB+Union3 | 3.8σ (full CMB) | Nσ ∈ [2.8, 4.1] |
| G5.5 | BAO+CMB+DESY5 | 4.2σ (full CMB) | Nσ ∈ [3.2, 4.5] |
| G5.6 | ordre | — | Nσ(P+) < Nσ(Union3) < Nσ(DESY5) |

- Convention σ : Δχ²_MAP → CDF χ²(2 dof) → équivalent gaussien 1D
  [Eq. (22)] ; best-fits par optimisation multi-départs (les départs et
  seeds sont fixés dans le code avant les runs).
- (GO M1.2a) Pour G5.3-G5.5, l'écart Nσ_pipeline − Nσ_publié est rapporté
  comme mesure de l'effet de compression, comparé au −0.7σ que DESI mesure
  sur BAO+CMB (2.4σ vs 3.1σ).
- (GO M1.2b) Gate échoué avec cause plausible côté minimiseur : STOP,
  audit documenté ; jamais de relâchement silencieux.
- Priors des fits : w0 ∈ U[−3,1], wa ∈ U[−3,2], w0+wa < 0,
  Ωm ∈ U[0.01,0.99], rd·h ∈ U[10,1000] Mpc (bras BAO seul) [RESULTS §1.2].
- ΔAIC/ΔBIC rapportés en complément (k = 2 paramètres ajoutés ; n = nombre
  de points de données du bras, documenté par bras).

## P5 — M7 : coupures low-z (CLOSES au GO M1 — aucune addition après les
## premiers chiffres)

Appliquées aux bras BAO+CMB+DES-SN5YR et BAO+CMB+Pantheon+ :

| ID | Coupure | Miroir de |
|---|---|---|
| C-a | z > 0.1 | DESI DR2 Fig. 14 ; Efstathiou 2408.07175 |
| C-b | exclusion IDSURVEY CfA (61-66) + CSP, Foundation (150) conservé | 2502.04212 (échantillons historiques) |
| C-c | DES pur (IDSURVEY = 10) ; P+ : z > 0.1 | DESI VII.3 « exclude the low-z sample entirely » |
| C-d | z > 0.025 (contrôle) | coupure Dovekie 2511.07517 Sec. 2.2 |

Note : CSP dans Pantheon+ = IDSURVEY 5 ; le low-z divers P+ (50, 51, 56,
57, 18) est conservé sauf en C-c. Sous-échantillons figés au moment du
download (M2) par hash du fichier filtré.

Métrique de rapport FIGÉE (un tableau par sample) :

| Coupure | N_SNe | Δχ²_MAP | Nσ | ΔNσ vs baseline | w0_MAP | wa_MAP | Δw0 | Δwa |

(baseline = bras complet sans coupure ; aucune autre statistique décidée
après coup ne sera présentée comme résultat principal.)

## P6 — Test de sensibilité θ* — CADUC (condition résolue)

- La clause GO M1.c prévoyait ce test « si la valeur complète est
  introuvable ». Elle a été trouvée (P1) : le test de sensibilité ±5×10⁻⁶
  n'a plus d'objet et ne sera pas exécuté. Restent : le test de cohérence
  troncature (P1) et l'épinglage SHA256 du yaml source (M2).

## P7 — Déterminisme

- Seed racine du projet : 20260611 (toute dérivation de seed est une
  fonction pure et committée de ce seed + nom du run).
- MCMC M6 : emcee, convergence ≥ 50·τ ; nwalkers et longueurs fixés et
  committés avant les runs M6 ; prédictions pré-run committées quand
  pertinent (SPEC).
- Tolérances M4 (SPEC) : intégrale vs forme fermée CPL < 1e-12 relatif sur
  la grille du prior ; oracles astropy < 1e-6 ; ΛCDM ≡ w0waCDM(−1, 0)
  exact (mêmes chemins de code).

## P8 — Amendement calibré θ*/r_d (GO Téo du 2026-06-11, APRÈS l'audit
## G5.2 — transparence totale)

- **Statut et transparence** : cet amendement N'EST PAS un
  pré-enregistrement aveugle. Il a été décidé APRÈS l'échec du gate G5.2
  (1.957σ, fenêtre [2.1, 2.7]) et son audit (RESULTS.md §5), qui a
  identifié un biais de ~−0.1 % du θ* analytique (HS96+EH98) face à
  σ(θ*)/θ* = 2.5×10⁻⁴ ; le diagnostic d'audit (prior décalé du biais
  alors estimé) donnait déjà ~2.27σ. Même statut assumé que la
  recalibration Keeley du projet P0. Committé AVANT tout re-run M5.
- **Nature de la correction** : deux constantes MULTIPLICATIVES sur les
  sorties analytiques des bras CMB, et rien d'autre —
  `KAPPA_R_DRAG` sur r_d(Aubourg Eq. 16) et `KAPPA_THETA_STAR` sur
  θ* = r_s(z*)/D_M(z*) (équivalent à une constante sur r_s(z*)).
  Indépendantes des données SNe, du modèle (ΛCDM/w0waCDM) et des
  coupures M7 — vérifiable dans le code (cmb.py, DESIParams).
- **Source de calibration** : l'ancrage publié DESI Eq. (2)
  (r_d = 147.05 Mpc) est INSUFFISANT pour θ* (il calibre l'époque drag,
  pas z*, et l'audit mesure des biais différents : −0.028 % vs −0.13 %) ;
  conformément à l'ordre de préférence du GO, la calibration utilise les
  chaînes officielles DESI DR2 épinglées (data_manifest.json, SHA256) :
  κ_r = moyenne pondérée de rdrag_CAMB/r_d_Aubourg (colonne `rdrag`) ;
  κ_θ = moyenne pondérée de θ*_CAMB/θ*_analytique, θ*_CAMB reconstruit
  point par point en inversant la forme quadratique de la colonne
  `chi2__CMB_compressed` à (ωb, ωbc) connus, choix de racine itéré à
  point fixe (le choix naïf « racine la plus proche de notre valeur
  brute » serait systématiquement biaisé bas de ~E[séparation]/2 ;
  l'itération symétrise les erreurs d'assignation). Script committé :
  scripts/calibrate_p8.py ; sortie : results/calibration_p8.json.
- **Valeurs committées** (stride 10, chaînes base + base_w_wa poolées à
  poids égal par modèle) :
  - `KAPPA_R_DRAG = 1.000279376` (par modèle : 1.0002834 / 1.0002753)
  - `KAPPA_THETA_STAR = 1.001314308` (par modèle : 1.0013114 / 1.0013173 ;
    scatter résiduel 7.6×10⁻⁶ ≈ 0.03σ_prior — la correction constante
    capture la quasi-totalité du biais ; la « dépendance paramétrique »
    de l'audit était dominée par le bruit d'assignation de racine)
- **Gates re-évalués** : G5.1b-G5.6b, MÊMES fenêtres que P4. G5.2
  (pipeline analytique brut) reste ÉCHOUÉ dans l'historique ; RESULTS.md
  conserve les deux tableaux côte à côte. Re-run M5 COMPLET (la
  correction touche tous les bras CMB) ; effet de compression re-mesuré.
- **Fallback (clause du GO)** : si G5.2b n'est pas vert avec ces seules
  constantes, STOP — bascule sur l'option (a) (limitation documentée),
  sans itération supplémentaire.
- CAMB/CLASS restent hors périmètre v1 (raffinement futur mentionné en M8).
