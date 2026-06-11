# RESULTS — desi-w0wa-refit

> §1-2 : conventions et formats extraits des sources (jalon M1), avec
> références précises (papier, section, équation, table). Les sections
> suivantes (méthodo, résultats, limites) seront remplies aux jalons M5-M8.
> Rédigé le 2026-06-11. Extraction : 7 sous-agents (un par source) +
> recoupement croisé + contre-vérification adversariale des équations
> critiques du papier DESI DR2.

## §1 — Conventions DESI DR2 (arXiv:2503.14738v3, publié PRD 112, 083515)

### 1.1 Convention de significativité (« la » convention σ du projet)

- Statistique : `Δχ²_MAP ≡ −2Δln L`, évaluée aux points de **maximum a
  posteriori** de chaque modèle (best-fit affiné par iminuit en partant des
  points MAP des chaînes MCMC) [Section V].
- Conversion en σ : ΛCDM étant imbriqué dans w0waCDM en (w0, wa) = (−1, 0),
  Wilks ⇒ Δχ²_MAP ~ χ²(2 dof) sous H0. Le « Nσ » publié est défini par
  CDF_χ²(Δχ²_MAP | 2 dof) = P(|X| < N) pour X ~ N(0,1) [Eq. (22), préambule
  Section VII ; légende Table 6 : « significance levels given 2 extra free
  parameters »].
- Le papier rapporte aussi Δ(DIC) [Table 6] — nous rapporterons ΔAIC/ΔBIC en
  complément (objectif SPEC), sans prétendre répliquer le DIC.

### 1.2 Priors (hérités de DESI DR1, arXiv:2404.03002 Table 2)

« Prior ranges on all sampled parameters match those given in Table 2 of
[DESI 2024 VI] » [Section V]. Pour notre espace de paramètres :

| Paramètre | Prior | Source |
|---|---|---|
| w0 | U[−3, 1] | 2404.03002 Table 2 ; répété Section VII de 2503.14738 |
| wa | U[−3, 2], avec w0 + wa < 0 | idem (domination de matière à haut z) |
| Ωm | U[0.01, 0.99] | 2404.03002 Table 2 |
| h·rd | U[10, 1000] Mpc (fits « background-only ») | 2404.03002 Table 2 |
| H0 | U[20, 100] km/s/Mpc (si calibration externe) | 2404.03002 Table 2 |

### 1.3 Traitement de r_d

- BAO seul : **pas de calcul de r_d** — échantillonnage direct de (Ωm, h·rd) ;
  r_d est absorbé dans le paramètre libre h·rd [Section V].
- BAO calibré (BBN/CMB) : échantillonnage de (H0, ωb…), r_d calculé par le
  code Boltzmann (CAMB via Cobaya) [Section V]. Aucune formule de fitting
  pour r_d n'est utilisée par DESI. Prior BBN : ωb = 0.02218 ± 0.00055
  [Eq. (14), Section IV.1 ; Schöneberg 2024, arXiv:2401.15054].
- Conséquence pour nous (Boltzmann out-of-scope) : voir choix CMB §2.5 — le
  bras BAO-seul est exact (h·rd libre) ; les bras avec CMB nécessitent une
  formule de fitting publiée pour r_d (et z*, r_s(z*)), décision au GO M1.

### 1.4 « CMB » au sens DESI DR2

- Baseline publiée : Planck TT/TE/EE (SimAll + Commander ℓ<30, CamSpec PR4
  ℓ≥30) + lensing Planck+ACT DR6 [Section IV.2]. C'est du full CMB —
  hors de notre périmètre (SPEC).
- **Alternative compressée publiée par DESI eux-mêmes** : prior gaussien
  corrélé sur (θ*, ωb, ωbc), « more model-independent », Appendix A :
  - moyennes (θ*, ωb, ωbc) = (0.01041, 0.02223, 0.14208) [Eq. (35)] ;
  - covariance C = 10⁻⁹ ×
    [[0.006621, 0.12444, −1.1929],
     [0.12444, 21.344, −94.001],
     [−1.1929, −94.001, 1488.4]] [Eq. (36)] ;
  - fondement méthodologique : Lemos & Lewis 2023 (arXiv:2302.12911).
- Point décisif : la ligne « DESI+(θ*, ωb, ωbc)_CMB » figure dans la
  Table 6 publiée (Δχ²_MAP = −8.0, 2.4σ) → ancrage EXACT de notre pipeline
  compressé pour la combinaison BAO+CMB, sans approximation de notre part.

### 1.5 Valeurs publiées à répliquer (ancrages M5)

Δχ²_MAP / significativité [Table 6] et posteriors (moyennes marginalisées ±
68 % [Table 5]) :

| Combinaison | Δχ²_MAP | σ | w0 | wa |
|---|---|---|---|---|
| DESI seul | −4.7 | 1.7σ | −0.48 +0.35/−0.17 | < −1.34 (68 %) |
| DESI+(θ*,ωb,ωbc)_CMB | −8.0 | 2.4σ | — | — |
| DESI+CMB (full) | −12.5 | 3.1σ | −0.42±0.21 | −1.75±0.58 |
| DESI+CMB+Pantheon+ | −10.7 | 2.8σ | −0.838±0.055 | −0.62 +0.22/−0.19 |
| DESI+CMB+Union3 | −17.4 | 3.8σ | −0.667±0.088 | −1.09 +0.31/−0.27 |
| DESI+CMB+DESY5 | −21.0 | 4.2σ | −0.752±0.057 | −0.86 +0.23/−0.20 |

Sans CMB [Table 6] : DESI+Pantheon+ 1.7σ ; DESI+Union3 2.7σ ; DESI+DESY5
3.3σ. (ΛCDM, contexte : tension BAO–CMB 2.3σ [Section VI].)

### 1.6 Mesures BAO DR2 [Table 4, Section III.3]

7 points effectifs : BGS z=0.295 (D_V/r_d) ; LRG1 z=0.510, LRG2 z=0.706,
LRG3+ELG1 z=0.934, ELG2 z=1.321, QSO z=1.484, Lyα z=2.330 (D_M/r_d et
D_H/r_d corrélés). Valeurs : voir §2.1 (fichiers bao_data) — concordance
vérifiée chiffre à chiffre entre Table 4 et les fichiers (recoupement
croisé : deux agents, deux sources indépendantes).

### 1.7 Le test low-z fait par DESI eux-mêmes

« The constraining power of SNe in measuring the equation of state comes
primarily from the comparison of low-redshift (z<0.1) and high redshift
(z>0.1) supernovae » [Section VII.3]. DESI teste l'exclusion des SNe z<0.1
de DESY5 [Figure 14, panneau central] : incertitudes élargies,
significativité réduite, best-fits (w0, wa) « far from ΛCDM ». Efstathiou
[arXiv:2408.07175] cité, ainsi que la réponse Vincenzi et al.
[arXiv:2501.06664] [Section VII.3].

## §2 — Données, formats, et littérature critique

### 2.1 BAO : CobayaSampler/bao_data, dossier desi_bao_dr2/

- 16 fichiers, 8 paires `*_mean.txt` / `*_cov.txt` (fichier ALL_GCcomb =
  les 13 points concaténés + covariance 13×13 bloc-diagonale ; blocs
  vérifiés identiques aux fichiers par traceur).
- Format mean : 3 colonnes `z valeur observable` (DV_over_rs, DM_over_rs,
  DH_over_rs), 1 ligne de commentaire. **Piège vérifié : pour Lyα (z=2.33),
  l'ordre est DH puis DM, inversé par rapport aux autres tranches.**
- Format cov : matrice pleine en texte, ordre = ordre des lignes du mean.
- Likelihood de référence (cobaya `bao.desi_dr2`, classe `desi_bao_all`) :
  gaussienne pure, logp = −0.5·xᵀC⁻¹x, x = théorie − mesure ; `rs_fid: 1`
  (données déjà en unités de r_d) [cobaya base_classes/bao.py +
  desi_bao_all.yaml, verbatim vérifié].
- Épinglage : le dossier provient d'un unique commit
  `b7b8a36e9bccb063081f811f323cada21ab5fbdd` (2025-03-20) = tag **v2.6** ;
  master actuel (`bb0c1c9…`) strictement identique. URLs raw épinglées sur
  v2.6 ; `+` encodé `%2B`. SHA256 calculés au download (M2).

### 2.2 SNe Pantheon+ (PantheonPlusSH0ES/DataRelease, maîtrisé en P0)

- `Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat` : 47 colonnes
  nommées (CID, IDSURVEY, zHD/zCMB/zHEL, m_b_corr, …) ; 1701 lignes.
- `Pantheon+SH0ES_STAT+SYS.cov` : première ligne = dimension (1701), puis
  N² valeurs (matrice pleine, lecture séquentielle).
- Coupure cosmologie : zHD > 0.01 (→ 1590 SNe) ; les z < 0.01 ne servent
  qu'au bras SH0ES. Réserve : phrase exacte à confirmer dans Scolnic et al.
  2022 (arXiv:2112.03863) — fait partie du gate M3, pas bloquant pour M1.
- Ancrages publiés [Brout et al. 2022, arXiv:2202.04077, Table 3] :
  SN-alone FlatΛCDM Ωm = 0.334 ± 0.018 ; FlatwCDM (Ωm, w) =
  (0.309 +0.063/−0.069, −0.90 ± 0.14) ; Flatw0waCDM w0 = −0.93 ± 0.15,
  wa = −0.1 +0.9/−2.0.
- Littérature : Keeley, Shafieloo & L'Huillier [arXiv:2212.07917, publié
  Universe 2024] — χ²_ΛCDM = 1387.10 pour 1580 points, >3.9σ trop bas sur
  10 000 mocks ⇒ erreurs Pantheon+ surestimées d'~7 % [Sec. 2, Fig. 1].
  Aucun effet chiffré publié sur la préférence w0wa. → limitation M8, pas
  de correction de notre part (zéro tuning).

### 2.3 SNe DES-SN5YR (des-science/DES-SN5YR + Zenodo 12720778)

- **Épinglage critique : tag v1.2 (commit `95cf14c8e057ef3c2d6bf72ae22cf0d5
  ee796e1c`)** = état du papier 2024 (arXiv:2401.02929). La branche main est
  passée à la ré-analyse « Dovekie » (Popovic et al. 2026, arXiv:2511.07517)
  — fichiers différents (1820 SNe). Zenodo : DES-SN5YR-1.2.zip (1.53 Go,
  MD5 publié `9019a6ddc569553bc323e9e1b68a55bf` ; SHA256 calculé par nous).
- `4_DISTANCES_COVMAT/DES-SN5YR_HD.csv` : CSV, 1829 SNe (1635 DES IDSURVEY=10
  + 194 low-z : CfA 61-66, FOUND 150), colonnes CID, IDSURVEY, zCMB, zHD,
  zHEL, MU, MUERR_FINAL (MU calibré H0=70).
- `STAT+SYS.txt.gz` : 1ʳᵉ ligne = N (1829), puis N² valeurs UNE PAR LIGNE
  (matrice pleine). **Piège vérifié : STATONLY est ~zéro ; la covariance
  totale = STAT+SYS + diag(MUERR_FINAL²)** [README 4_DISTANCES_COVMAT +
  `5_COSMOLOGY/SN_only_cosmosis_likelihood.py` : `C[i,i] += err²`].
- Likelihood officielle : marginalisation analytique de l'offset M
  (dégénéré avec H0), χ² = Δμᵀ C⁻¹ Δμ modifié [papier Section 3, Eq. 5 ;
  script officiel] — même machinerie que notre MarginalizedChi2 (P0).
- Chaînes officielles (ancrage exact M3) : `5_COSMOLOGY/chains/fw0wacdm/`
  etc., format CosmoSIS, colonnes omega_m, h0, w, wa, supernova_params--m,
  prior, like, post, **weight** (polychord pondéré) ; variantes SN,
  SN+planck, ×2 samplers.
- Best-fits publiés [arXiv:2401.02929, Table 2] : SN-alone FlatΛCDM
  Ωm = 0.352 ± 0.017 ; FlatwCDM (0.264 +0.074/−0.096, −0.80 +0.14/−0.16) ;
  Flatw0waCDM SN-alone (Ωm, w0, wa) = (0.495, −0.36, −8.8) — posterior très
  dégénéré, l'ancrage SN-alone se fera contre les chaînes, pas ce point.

### 2.4 SNe Union3 (rubind/union3_release + cobaya sn_data) — VERDICT : faisable

- Usage DESI réplicable exactement : cobaya `sn.union3` lit
  `sn_data/Union3/lcparam_full.txt` (22 nœuds, bin00-bin21, z = 0.05 à
  2.26226, colonne mb = module de distance à zéro arbitraire) +
  `mag_covmat.txt` (22×22), offset marginalisé (`use_abs_mag: False`).
- Sources redondantes : repo rubind/union3_release (Zenodo 14090777) —
  FITS `mu_mat_union3_cosmo=2_mu.fits` (équivalent, covariance inverse) +
  chaînes de posterior complètes (`all_samples_union3_cosmo=2.npz`).
- Critique du format [Kim, arXiv:2412.14181] : le produit publié est un
  POSTERIOR spline (22 nœuds) dont le prior implicite n'est pas plat en
  (Ωm, w0, wa) [Sec. 3] ; DESI l'utilise tel quel comme likelihood sans
  diviser par le prior [Sec. 5] ; effet jugé « inconsequential » par Kim
  lui-même. → Nous répliquons l'usage DESI (objectif = reproduction) et
  documentons cette limite en M8.
- Décision (SPEC « best-effort ») : Union3 INCLUS, traitement identique à
  l'usage DESI via les fichiers cobaya sn_data.

### 2.5 Compression CMB — options sourcées (décision au GO M1)

- **Option A (proposée) : la compression de DESI eux-mêmes** — prior
  gaussien (θ*, ωb, ωbc), Eqs. (35)-(36) de 2503.14738 Appendix A (§1.4).
  Avantages : (i) c'est LA version publiée par la collaboration dont on
  reproduit le résultat ; (ii) ancrage exact publié (2.4σ, Table 6) ;
  (iii) validée comme quasi indépendante de la physique tardive
  [Lemos & Lewis 2023]. Coût : θ* et la conversion (ωb, ωbc) → r_d
  exigent des formules de fitting pré-recombinaison publiées (r_s(z_drag),
  z*, r_s(z*)) — à extraire de leur source au GO (candidates : formules
  d'Aubourg et al. 2015 / Hu & Sugiyama 1996, références exactes à épingler
  avant M2, jamais de mémoire).
- Option B : priors de distance classiques (R, l_A, ωb, n_s), Planck 2018
  TT,TE,EE+lowE [Chen, Huang & Wang, arXiv:1808.05724, Table 1, Eqs. (1)-(2)] :
  R = 1.7502 ± 0.0046, l_A = 301.471 ± 0.089, ωb = 0.02236 ± 0.00015,
  n_s = 0.9649 ± 0.0043 + matrice de corrélation publiée. Avantages :
  standard historique, valeurs verbatim complètes. Inconvénients : pas la
  compression de DESI, pas d'ancrage publié dans Table 6, même besoin de
  formules pré-recombinaison.
- Limitation (les deux options) : nos σ des combos avec SNe différeront des
  publiés (full CMB). Écart attendu, mesuré par DESI : 2.4σ (compressé) vs
  3.1σ (full) sur DESI+CMB — à intégrer dans les gates M5.

### 2.6 Coupures low-z des critiques (base du pré-enregistrement M7)

- Efstathiou [arXiv:2408.07175] : fenêtre 0.02 ≤ zHD ≤ 1.2 [Sec. 2] ;
  offset low-z/high-z ~0.04 mag sur les SNe communes DES5Y/Pantheon+
  (Foundation −0.051±0.007 ; low-z combiné −0.0482±0.0057 [Sec. 3,
  Table 1]) ; en soustrayant 0.04 mag au low-z de DES5Y, la préférence
  w0wa devient non significative (Δχ² ~2.5) [Sec. 3, Fig. 5].
- Huang, Cai & Wang [arXiv:2502.04212] : sous-échantillons low-z en cause
  CSP (8), CfA (68), Foundation (118) vs 1635 DES high-z ; discordance
  ~0.043 mag d'intercept [Sec. III.2] ; significativités CMB+DESI+DESY5
  3.5-3.7σ → ~1.5-1.6σ après correction [Tables 1-2].
- Réponse DES [Popovic et al., arXiv:2511.07517, MNRAS 2026] : recalibration
  complète (Dovekie, ancrage naines blanches DA), bug F99 corrigé (~0.01
  mag), poids systématiques corrigés (somme 0.81 → 1) [Sec. 5, App. A].
  Résultat : préférence réduite 4.2σ → **3.2σ** (DES+CMB+DESI DR2)
  [abstract ; w0 = −0.803±0.054, wa = −0.72±0.21]. Seule coupure : z > 0.025
  (vitesses particulières) [Sec. 2.2] ; aucun test de variation z_min dans
  ce papier.
- Identification dans nos fichiers : Pantheon+ et DES-SN5YR partagent les
  codes IDSURVEY (CSP=5 pour P+, CfA=61-66, Foundation=150, DES=10 ;
  low-z divers P+ : 50, 51, 56, 57, 18). Coupures candidates M7 (à figer
  au GO M1) : (a) z > 0.1 (miroir DESI Fig. 14 et Efstathiou) ;
  (b) exclusion par IDSURVEY des échantillons historiques (CfA+CSP) en
  gardant Foundation ; (c) exclusion de tout le low-z externe (DES pur,
  IDSURVEY=10 ; et P+ z>0.1) ; (d) contrôle : z > 0.025 (coupure Dovekie).

### 2.7 Divergences relevées entre sources (règle « STOP si divergence »)

Aucune divergence de convention bloquante. Trois écarts documentés, tous
expliqués : (i) main du repo DES ≠ papier 2024 → résolu par épinglage v1.2 ;
(ii) significativité DESY5 4.2σ (DR2) vs 3.2σ (Dovekie 2026) → deux
releases différentes, nous répliquons DR2/v1.2 et citons Dovekie en
contexte ; (iii) valeurs de compression CMB de 2509.21491 (App. C) ≠
Eqs. (35)-(36) → variantes de datasets (P-ACT vs baseline DESI), nous
utilisons les Eqs. (35)-(36) si Option A retenue.
