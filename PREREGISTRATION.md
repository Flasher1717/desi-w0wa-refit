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

---

# Extension P2.1 (SPEC_V21.md) — P9-P11, committés au STOP M10

> Rédigés en M10 (2026-06-12), AVANT tout run M11-M13, soumis au GO M10 de
> Téo. Mêmes règles : chaque section gèle au premier run qui la concerne ;
> toute déviation est documentée dans RESULTS.md. Sources extraites en M10
> par revue multi-agents + vérification indépendante (MILESTONES.md,
> entrée M10) : Keeley, Shafieloo & L'Huillier arXiv:2212.07917v3 Sec. 2 ;
> Efstathiou arXiv:2408.07175v3 Sect. 2-3, Table 1 ; fichiers épinglés
> data_manifest.json (les SHA256 existants font foi, DES-SN5YR tag v1.2).

## P9 — V1 : Keeley-test sur la covariance DES-SN5YR (M11)

### P9.1 Échantillon et covariance

- Échantillon : les 1829 SNe de data/DES-SN5YR_HD.csv épinglé, SANS
  coupure (zHD min = 0.0251 ; pas de calibrateurs dans cette release —
  il n'existe pas d'analogue à la sélection « z > 0.01, hors SH0ES »
  de Keeley, fait documenté, pas une décision).
- Covariance : C_totale = STAT+SYS + diag(MUERR_FINAL²), exactement
  telle que la construit `load_des_sn5yr()` (sne.py) — la MÊME matrice
  pour le tirage du bruit ET pour le χ², même facteur de Cholesky
  inférieur (caché) pour les deux usages (Keeley ne spécifie pas la
  factorisation ; nous la fixons : Cholesky inférieur).
- Colonne de redshift : zHD (même convention que tout le pipeline v1).

### P9.2 Méthode (réplique de Keeley Sec. 2, ambiguïtés tranchées ici)

- Fiducial du tirage (PRIMAIRE, à la Keeley — décision GO M10.3 : la
  fidélité à l'étalon prime, c'est une réplication de méthode) : flat
  ΛCDM, Ωm = 0.3, H0 = 70 km/s/Mpc, MB = −19.0 (l'offset est profilé,
  H0 et MB n'entrent que comme convention d'écriture) ; μ fiduciel
  évalué aux zHD des 1829 SNe par le code cosmologique existant du
  pipeline (oracles M4).
- Mocks : mu_mock = mu_fid + L·ξ, ξ ~ N(0, I) — soit N(mu_fid, C_totale)
  [Keeley Sec. 2 : « random noise added... drawn from a multivariate
  Gaussian characterized by the covariance matrix »].
- Par mock, refit ΛCDM : Ωm seul paramètre non linéaire, borné
  [0.01, 1.0], `scipy.optimize.minimize_scalar` bounded, xatol = 1e-8
  (configuration P0 validée à ~1e-8 contre la minimisation explicite de
  l'offset) ; offset additif unique PROFILÉ analytiquement
  (A − B²/E, Goliath 2001 eq. 21). Keeley « varie (H0, Ωm, MB) » sans
  nommer de minimiseur ; H0-MB sont exactement dégénérés SN-only — le
  profil analytique est l'implémentation que nous fixons. Le χ² cité
  est le χ² PROFILÉ A − B²/E (PAS chi2_marginalized de sne.py, qui
  ajoute le terme log-déterminant de la marginalisation Goliath
  A9-A12 ; la constante ln-terme, identique pour données et mocks,
  sera rapportée explicitement si elle apparaît dans un chiffre).
- IDENTIQUE chemin de code pour le χ²_min des données réelles et celui
  de chaque mock (symétrie que Keeley implique sans l'énoncer).
- Politique d'échec : un mock dont l'optimiseur touche une borne Ωm ou
  ne converge pas est flagué et compté ; si > 1 % des mocks sont
  flagués, STOP audit avant toute interprétation.

### P9.3 N, seeds, statistique et seuils

- N_mocks = 10 000 (comme Keeley). Plancher de résolution déclaré :
  p ≥ 1/10001.
- Seeds : générateur numpy default_rng (PCG64) ; seed du mock i =
  derive_seed(f"m11-v1-mock-{i}") depuis ROOT_SEED = 20260611 (schéma
  P7 inchangé).
- Statistique PRIMAIRE : p = (k+1)/(N+1), k = #{χ²_min,mock < χ²_min,réel},
  queue BASSE one-sided (celle que Keeley teste). Rapportés en
  complément : les deux conversions gaussiennes de p (one-sided et
  two-sided, la two-sided étiquetée « comparaison Keeley » — son
  « > 3.9σ » pour 0/10 000 correspond à la conversion two-sided,
  convention qu'il n'énonce pas).
- Seuils d'interprétation FIGÉS (pas de gate d'ancrage : personne n'a
  publié ce test sur DES) : « χ² anormalement bas » si p < 0.0027
  (équivalent 3σ two-sided) ; « compatible » si 0.0027 ≤ p ≤ 0.9973 ;
  « queue haute anormale » sinon. Quel que soit le verdict : rapporté
  tel quel, zéro correction (SPEC V2.1, M11).
- Référence analytique en CONTEXTE (non gating) : χ²(N dof), N = 1829,
  dof = N à la Keeley (sans soustraction des paramètres ajustés —
  son choix, documenté comme tel).

### P9.4 Livrables secondaires pré-enregistrés (non gating)

- (a) Run répété avec fiducial au best-fit Ωm SN-only DES réel du
  pipeline (le χ²_min est fiducial-indépendant dans la direction
  linéaire profilée mais pas en Ωm — sensibilité quantifiée au lieu
  d'être laissée en ambiguïté). Seeds : derive_seed(f"m11-v1b-mock-{i}").
- (b) Variante excluant les 75 lignes MUERR_FINAL > 1 (poids BEAMS,
  particularité DES sans analogue Pantheon+) — tirage et χ² sur la
  sous-matrice 1754×1754. Seeds : derive_seed(f"m11-v1c-mock-{i}").
- (c) Diagnostics descriptifs à la Keeley : std des résidus normalisés
  du best-fit réel ; δ² soustrait de la diagonale tel que χ²_min = N.
- Pilote technique : un run de chronométrage de 50 mocks (seeds du
  stream primaire), déclaré NON scientifique, autorisé avant le run
  complet pour calibrer le coût — ses χ² ne sont ni rapportés ni
  comparés au χ² réel.

### P9.5 Gates d'ancrage du pipeline mock (RETENUS au GO M10.2)

- G11.1 (synthétique) : covariance diagonale σ²I et modèle linéaire où
  la distribution de χ²_min est connue (χ², N−2 dof effectifs après
  profil) — le percentile empirique d'une valeur de référence doit
  tomber dans ±2 % du percentile analytique.
- G11.2 (Keeley exact, RETENU — GO M10.2 : « sans étalon P+, le verdict
  V1 sur DES serait inédit ET invérifiable ; avec lui, il est
  étalonné ») : re-dérouler le test complet sur Pantheon+ en
  configuration Keeley (zHD > 0.01 ET IS_CALIBRATOR = 0, N = 1580 —
  le compte 1580 inclut TOUJOURS la clause calibrateurs, cf. erratum
  P0 v1.1.1) ; gates : χ²_min réel reproduit à |Δχ²| ≤ 1.0 de 1387.10
  (gate P0) ET p_P+ ≤ 0.0027 (cohérent avec le « 0/10 000 » publié de
  Keeley). Seeds : derive_seed(f"m11-v1pp-mock-{i}").

## P10 — V2 : décomposition leave-one-group-out (M12)

### P10.1 Grille des groupes (CLOSE — aucune addition après les
### premiers chiffres ; tailles post-coupure de chargement zHD > 0.01)

Bras BAO+CMB+Pantheon+ (baseline gelée N = 1590) — 5 groupes
+ 1 ligne agrégée (AMENDEMENT GO M10.4, figé ici avant tout run) :

| Groupe | IDSURVEY | N retiré | N restant |
|---|---|---|---|
| CfA | 61, 62, 63, 64, 65, 66 | 157 | 1433 |
| CSP | 5 | 76 | 1514 |
| Foundation | 150 | 173 | 1417 |
| misc low-z | 18, 50, 51, 56, 57 | 201 | 1389 |
| DES (dans P+) | 10 | 203 | 1387 |
| (agrégé) CfA+CSP | 61-66, 5 | 233 | 1357 |

(SDSS 1, SNLS 4, PS1 15, HST 100/101/106 ne sont JAMAIS retirés —
SPEC V2.1 ne nomme que les groupes ci-dessus ; dans le bloc low-z les
4 premiers groupes le partitionnent exactement.)

- RÉUTILISATION GELÉE (zéro nouveau fit, conforme « V2 réutilise le
  pipeline et les baselines tels quels ») : la ligne agrégée CfA+CSP
  du bras P+ est, par composition, EXACTEMENT le sous-échantillon C-b
  de M7 (exclusion 61-66 + 5, Foundation conservé, N = 1357,
  subset_sha256 eba5ac7c… consigné dans results/m7_cuts.json) ; idem
  la ligne primaire CfA+CSP du bras DES = C-b DES de M7 (N = 1753).
  Pour ces DEUX lignes, les colonnes de fit (Δχ²_MAP, Nσ, ΔNσ, w0, wa,
  Δw0, Δwa) sont REPRISES TELLES QUELLES de results/m7_cuts.json (gelé,
  fait foi) ; seules les colonnes σ_curv sont calculées, par pures
  évaluations FD au MAP gelé `w0wa_params` de C-b (même statut que les
  σ_curv des baselines, P10.3). Test de cohérence : le masque LOO
  reproduit byte-à-byte le subset_sha256 consigné en M7.

Bras BAO+CMB+DES-SN5YR (baseline gelée N = 1829) — 3 groupes primaires
+ 2 sous-lignes descriptives :

| Groupe | IDSURVEY | N retiré | N restant |
|---|---|---|---|
| CfA+CSP | 5, 63, 64, 65, 66 | 76 | 1753 |
| Foundation | 150 | 118 | 1711 |
| DES | 10 | 1635 | 194 |
| (desc.) CfA seul | 63, 64, 65, 66 | 68 | 1761 |
| (desc.) CSP seul | 5 | 8 | 1821 |

- Le fichier DES ne contient AUCUN IDSURVEY 61/62 ni 18/50/51/56/57
  (mesuré M10) : « même métrique pour les deux bras » = même MÉTRIQUE,
  appartenances par bras tabulées ci-dessus. CfA+CSP fusionné en
  primaire côté DES (miroir exact de l'exclusion C-b de M7) parce que
  CSP-DES N = 8 produit un ΔNσ au niveau du bruit de reproductibilité
  de l'optimiseur ; les deux sous-lignes restent rapportées avec
  caveat petit-N explicite.
- Les groupes sont identifiés par codes IDSURVEY entiers (les noms ne
  figurent pas dans les CSV ; mapping standard SNANA cité en
  RESULTS.md §11).

### P10.2 Métrique (FIGÉE, un tableau par bras, même format)

| Groupe retiré | N_SNe | Δχ²_MAP | Nσ | ΔNσ | w0_MAP | wa_MAP | Δw0 | Δwa | σ_curv(w0) | σ_curv(wa) | Δσ_curv(w0) | Δσ_curv(wa) |

(baseline = bras complet GELÉ de results/m5_fits_corrected.json ;
aucune statistique décidée après coup ne sera présentée comme résultat
principal.)

### P10.3 σ_curv : définition (nouvelle quantité dérivée)

- Hessienne H de arm.chi2_w0wa par différences finies centrées
  (stencil 4 points pour les termes croisés) au MAP, dans l'espace à
  5 paramètres (Ωm, h, ωb h², w0, wa) ; F = H/2 ; C = 2 H⁻¹ ;
  σ_curv(w0) = √C[w0,w0], σ_curv(wa) = √C[wa,wa].
- Pas FIXES : δΩm = 1e-3, δh = 1e-3, δωbh² = 1e-4, δw0 = 1e-2,
  δwa = 3e-2 — assez grands pour dominer le plancher de bruit
  optimiseur (fatol 1e-10, reproductibilité ~1e-9), vérifiés contre
  les bornes avant différenciation.
- σ_curv des BASELINES : évaluations de χ² au MAP GELÉ lu dans
  m5_fits_corrected.json — de pures évaluations, PAS un re-fit (le
  gradient résiduel au point JSON-arrondi est documenté, jamais
  re-optimisé).
- Caveat pré-enregistré : σ_curv suppose un pic gaussien ; les
  marginales m6 de wa sont asymétriques (P+ p16/p84 = −0.769/−0.333) —
  σ_curv(wa) sous-estimera l'écart-type MCMC ; rapporté comme quantité
  de courbure, jamais comme intervalle de posterior. Cohérence (non
  gating) : comparaison aux σ m6 gelés (P+ : 0.0555/0.2205 ;
  DES : 0.0584/0.2387).

### P10.4 Politique boundary-MAP et lignes dégénérées

- Si le MAP w0waCDM d'une ligne est à moins de 2 pas FD d'une borne de
  la boîte de priors OU si |w0 + wa| < 0.05 (mur du prior dur
  w0+wa < 0) : ligne flaguée « boundary MAP », σ_curv NON rapporté,
  χ²/Δχ²/Nσ rapportés descriptivement. Cas attendu : la ligne
  DES-retiré (N = 194, tout à z < 0.093, surface (w0, wa) plate).
- Sous-matrice de covariance non définie-positive à la découpe :
  la LIGNE avorte (consignée), pas le run.

### P10.5 Implémentation et coût

- Nouveau script scripts/run_m12_loo.py, clone du pattern
  run_m7_cuts.py : subset par masque survey_ids, sample_hash (SHA256)
  consigné AVANT tout fit, mêmes nombres de départs (24 ΛCDM /
  40 w0waCDM), noms de runs « m12-<sample>-loo-<group>-<model> »
  (streams de seeds FRAIS via derive_seed — zéro collision avec les
  streams m5/m7 gelés), baselines lues de results/m5_fits_corrected.json,
  sortie UNIQUEMENT dans le nouveau results/m12_loo.json.
- AUCUN fichier results/*.json de v1.0.0 n'est modifié ; non-régression
  (SPEC V2.1 [TESTS]) : les tests de traçabilité v1.0.0 restent verts.
- Décompte (amendement GO M10.4) : lignes FRAÎCHES = 5 (P+ : CfA, CSP,
  Foundation, misc low-z, DES-in-P+) + 4 (DES : Foundation, DES,
  desc. CfA seul, desc. CSP seul) = 9 lignes × 2 modèles = 18 fits ;
  les 2 lignes CfA+CSP (P+ agrégée, DES primaire) sont REPRISES de
  m7_cuts.json (zéro fit). Correction d'arithmétique vs la version du
  STOP M10 (qui annonçait « 7 lignes primaires + 2 descriptives =
  18 fits » : c'était 8 + 2 = 20 ; l'amendement ramène bien à 18).
- Coût estimé (chronométrages M7) : ≈ 1.5-2 h.

## P11 — V3 : SNe communes appariées (M13)

### P11.1 Règle d'appariement (établie M10 depuis les fichiers réels)

- CID lus comme STRINGS (49 CID Pantheon+ ont des zéros de tête) ;
  normalisation : strip, lowercase, suppression du préfixe « sn »
  UNIQUEMENT si suivi d'un chiffre (protège « SNF20080514-002 »,
  fusionne l'incohérence interne P+ « 2016coj »/« SN2016coj ») ;
  appariement par égalité exacte de la clé normalisée ; garde-fou
  |zHD_PP − zHD_DES| < 0.01 par paire.
- Comptes ÉPINGLÉS (mesurés M10, vérifiés deux fois indépendamment,
  fixés en test pytest) : 335 objets communs (Tier P) ; 332 paires
  même-survey (Tier R) ; 4 low-z DES sans contrepartie P+ (2001ay,
  2004gc, 2007ob, 2007R — absences réelles, pas des écarts de
  nommage) ; 3 objets Tier-P-seulement (2005hj, 2005ir, 2006ev — CfA3K
  côté DES, courbes CSP-seulement côté P+).

### P11.2 Tier R — réplication Efstathiou Table 1 (gate d'ancrage,
### statut de non-aveuglement DÉCLARÉ)

- TRANSPARENCE (décision GO M10.1, même statut assumé que P8) : la
  règle d'appariement d'Efstathiou n'est PAS énoncée dans
  arXiv:2408.07175 ; elle a été rétro-ingéniérée en M10 (revue croisée
  + vérification indépendante par script jetable), ce qui a
  nécessairement produit les chiffres de réplication AVANT ce
  pré-enregistrement. CE QUI A ÉTÉ VU en M10 : l'intégralité des
  chiffres Tier R (comptes 145/118/14/27/18/3/7/187 ; moyennes de
  groupe −0.0122…−0.0482 ; SEM ; différentiel −0.0360 ; max |Δz| ;
  identités des non-appariées et des cross-survey). CE QUI N'A PAS ÉTÉ
  CALCULÉ : toute quantité Tier P (P11.3) — aucun Δμ = MU_SH0ES −
  MU_DES, aucune moyenne de groupe sous cette définition, ni S, ni
  l'application de la règle des doublons. HONNÊTETÉ SUPPLÉMENTAIRE :
  le Tier P n'est « aveugle » qu'au sens strict du non-calcul — sa
  valeur attendue est fortement contrainte par les chiffres Tier R
  déjà vus (statistiques étroitement corrélées sur ~les mêmes paires) ;
  il ne sera pas présenté comme une prédiction indépendante. G13.x est
  un gate de REPRODUCTIBILITÉ PIPELINE sur des nombres connus au gel.
- Méthode (Efstathiou Sect. 3, Table 1 « tab:magfits ») : paires
  même-survey (clé normalisée + même IDSURVEY dans les deux releases) ;
  Δ_i = m_b_corr − (MU − 19.33) [Eq. 2 « equ:calib » ; la constante
  −19.33 est imprimée et sans effet sur tout différentiel] ; moyennes
  NON pondérées par groupe (« giving each SN equal weight », Sect. 3) ;
  erreurs = std(ddof=0)/√N (convention inférée, validée au dernier
  chiffre imprimé sur 5 lignes de la Table 1).
- Gates G13.1-G13.3 (tolérances justifiées par la reproduction au
  dernier chiffre en M10) :
  - G13.1 comptes exacts : 145 (DES), 118 (FOUND), 14 (CFA3S = IDSURVEY
    63), 27 (CFA3K = 64), 18 (CFA4P2 = 65), 3 (CFA4P3 = 66), 7 (CSP = 5),
    187 (all low-z).
  - G13.2 moyennes de groupe à ±0.001 de : −0.0122, −0.0508, −0.0344,
    −0.0616, −0.0547, +0.0285, +0.0037, −0.0482 (Table 1 ; CSP imprimé
    +0.0036 et CFA4P3 imprimé 0.029 = arrondis).
  - G13.3 différentiel (all low-z) − (DES) à ±0.002 de −0.0360 (le
    « ~0.04 mag » du papier, quantité invariante de zéro).
  - SEM comparés aux valeurs CORRIGÉES (DES 0.0055, FOUND 0.0070,
    all low-z 0.0058) — les ±0.0006/±0.0007 imprimés de la Table 1
    sont d'apparentes typos décimales ×10 (démontré M10 : la
    convention SEM reproduit exactement les 5 autres erreurs
    imprimées) ; documenté en RESULTS.md §11 avec la démonstration
    complète, formulé prudemment (« apparent decimal typos in the
    printed uncertainties », décision GO M10.1), jamais utilisé comme
    cible.
  - 1304442 INCLUS en Tier R (le N = 145 d'Efstathiou l'inclut).
- Trois z_median de la Table 1 (CFA3S 0.037, CFA4P3 0.033, CSP 0.038)
  ne se recomputent ni sur zHD ni sur zCMB (nos valeurs : 0.034-0.035,
  0.039, 0.044) alors que les grandes lignes concordent — divergence
  cosmétique NON GATING, consignée telle quelle.

### P11.3 Tier P — analyse appariée principale (AVEUGLE : non calculée
### en M10)

- Ensemble : les 335 objets communs, UNE valeur de μ par objet et par
  release. DES : MU (une ligne par objet). Pantheon+ : la ligne de
  même IDSURVEY que la ligne DES si elle existe ; sinon priorité
  déterministe : ligne de plus petite m_b_corr_err_DIAG, tie-break
  IDSURVEY croissant. Variante secondaire pré-enregistrée :
  combinaison inverse-variance des lignes dupliquées avec le
  sous-bloc de covariance P+ publié.
- Δμ_i = MU_SH0ES,i − MU_DES,i (modules de distance publiés ; tout
  zéro de compilation s'annule dans la statistique différentielle).
- Split low/high par échantillon source (comme Efstathiou, pas par
  coupure z) : high-z = IDSURVEY_DES 10 ; low-z = le reste.
- Statistique PRINCIPALE : S = mean(Δμ_i, low-z) − mean(Δμ_i, high-z),
  moyennes NON pondérées ; incertitude PRIMAIRE = somme quadratique
  des SEM empiriques (std(ddof=0)/√N) des deux groupes — cohérente
  Tier R, et la dispersion par paire (~0.067 mag) est très inférieure
  aux erreurs de catalogue, ce qui invaliderait des poids
  inverse-variance catalogue.
- Incertitude SECONDAIRE pré-enregistrée : erreurs « covariance-aware »
  utilisant les sous-blocs appariés des covariances publiées des deux
  releases ; LIMITATION EXPLICITE (AMENDEMENT GO M10, A2) : les
  corrélations INTER-release des Δμ (les deux compilations standardisent
  largement les MÊMES courbes de lumière sources pour les communes) sont
  inconnues et NON modélisées — les erreurs publiées des catalogues ne
  sont donc PAS une mesure valide de l'incertitude des Δμ ; la
  dispersion EMPIRIQUE des Δμ est LA mesure d'incertitude primaire du
  Tier P, et l'erreur secondaire « covariance-aware » n'est pas une
  erreur jointe complète (RESULTS.md §11).
- EXCLUSION pré-enregistrée du Tier P primaire : 1304442 (zHD révisé
  entre releases : 0.22449 P+ vs 0.21711 DES, |Δz| = 0.0074 — μ non
  comparables à z fixé) ; ligne de sensibilité avec/sans rapportée.
  Aucune autre exclusion ; max MUERR_FINAL des 145 DES appariées =
  0.2423 (aucun screening BEAMS nécessaire, mesuré M10).
- Complément descriptif (non principal) : S recalculé avec
  Δ_i du Tier R (m_b_corr-based) sur les 335 ; tableau par groupe
  IDSURVEY au format Table 1 pour les deux définitions.

### P11.4 Tests V3 (SPEC V2.1 [TESTS])

- Appariement déterministe (ordre d'entrée indifférent) ; comptes 335 /
  332 / 4 / 3 épinglés en pytest (requires_data) ; zéro doublon de clé
  dans l'ensemble apparié ; auto-test : une SN appariée à elle-même
  (mêmes μ) donne Δμ = 0 exactement ; le garde-fou |Δz| < 0.01 laisse
  passer exactement 1304442 comme seul |Δz| > 0.003 (deuxième max
  0.00207).
