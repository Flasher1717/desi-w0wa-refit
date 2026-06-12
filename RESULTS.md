# RESULTS — desi-w0wa-refit

> §1-2 : conventions et formats extraits des sources (jalon M1), avec
> références précises (papier, section, équation, table). Les sections
> suivantes (méthodo, résultats, limites) seront remplies aux jalons M5-M8.
> Rédigé le 2026-06-11. Extraction : 7 sous-agents (un par source) +
> recoupement croisé + contre-vérification adversariale des équations
> critiques du papier DESI DR2 (Eq. 22, Eqs. 35-36, priors, Tables 5-6) :
> 6/6 claims confirmés chiffre par chiffre, Eqs. (35)-(36) sur LaTeX brut.

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
  - Vérification adversariale (second agent, lecture du LaTeX brut via
    alttext) : Eqs. (35)-(36) confirmées entrée par entrée, signes et
    exposant compris ; ordre (θ*, ωb, ωbc) confirmé ; c'est bien θ*
    (≈ 0.0104 rad), pas 100θ*.
  - **Caveat de précision — RÉSOLU** : le papier imprime θ* = 0.01041
    (5 décimales) alors que σ(θ*) ≈ 2.6×10⁻⁶. La valeur complète a été
    trouvée dans les produits officiels DESI DR2 (yaml Cobaya des chaînes
    publiées, data.desi.lbl.gov, contre-vérifiée sur deux fichiers
    indépendants) : moyennes (0.01041027, 0.02223208, 0.14207901) et
    covariance complète — voir PREREGISTRATION.md P1, épinglage SHA256
    en M2.
  - **Piège** : le papier contient aussi un prior θ*-SEUL distinct
    (100θ* = 1.04110 ± 0.00053, largeur gonflée ~75 %) — à ne jamais
    confondre avec le prior 3D compressé utilisé ici.
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

### 1.7 Formules pré-recombinaison et convention neutrinos

- Le papier fournit sa propre formule d'échelle pour r_d [Section I,
  Eq. (2)] : r_d = 147.05 Mpc · (ω_b/0.02236)^−0.13 · (ω_bc/0.1432)^−0.23 ·
  (Neff/3.04)^−0.1, « scaled to the best-fit values from Planck ».
- Formule de fitting principale du pipeline : Aubourg et al. 2015
  [arXiv:1411.1074, Eq. (16), précision documentée 0.021 %] ; z* pour θ* :
  Hu & Sugiyama 1996 [astro-ph/9510117, App. E, Eq. (E-1)]. Détails,
  constantes verbatim et limitations : PREREGISTRATION.md P2.
- Neutrinos baseline [Section V + chain.input.yaml officiels] :
  Σmν = 0.06 eV (un état massif), Neff = 3.044 ; Ωm inclut les neutrinos
  non relativistes ; ωbc = ωb + ωc les exclut [Section I, Eq. (6)].

### 1.8 Le test low-z fait par DESI eux-mêmes

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

## §3 — Décisions méthodologiques M3-M4 (documentées, aucune silencieuse)

1. **Symétrisation de la covariance Pantheon+** : le fichier STAT+SYS
   publié porte des asymétries d'arrondi du dernier chiffre imprimé
   (778 entrées sur 2 893 401, max |C−Cᵀ| = 3×10⁻⁸) ; symétrisé
   ½(C+Cᵀ) sous garde-fou dur 10⁻⁷ (les consommateurs officiels ne
   vérifient jamais la symétrie). Artefact de fichier, pas un choix
   physique.
2. **Priors G3.3** : extraits de l'entête de la chaîne officielle
   épinglée (omega_m U[0.01,0.99], h0 U[0.3,1], w U[−5,1],
   wa U[−20,10], m U[−1,1]) — le gate est évalué avec CES priors. Le
   couple (m, h0) échantillonné par DES est remplacé par la
   marginalisation analytique de l'offset (les deux ne contraignent que
   la même combinaison ; effet de bord des bornes négligeable, posterior
   d'offset très intérieur).
3. **Modèle SN-only et BAO-only sans radiation** : E² = Ωm(1+z)³ +
   (1−Ωm)f_DE — la paramétrisation background-only (Ωm, h·rd) de DESI ne
   permet même pas de spécifier Ωr ; effet ~10⁻⁴ mag sur μ(z≤1.1),
   négligeable devant les tolérances des gates (0.010 sur Ωm, 0.2σ).
4. **Domaine du cross-check r_d** (Aubourg Eq. 16 vs DESI Eq. 2,
   tolérance 0.3 %) : évalué sur ±5σ du prior gaussien CMB, seul domaine
   où r_d est utilisé (le bras BAO-seul échantillonne h·rd librement).
   Mesuré : 0.21 % à ±5σ ; les deux lois de puissance divergent loin du
   point de calibration (0.70 % au coin arbitraire ωbc = 0.10).
5. **Intégrateurs rapides** : r_s(z*) et D_M(z*) par Simpson sur grilles
   fixes (substitutions a = x² et log(1+z)), validés < 10⁻⁷ relatif
   contre quad adaptatif (test permanent).
6. **Neutrinos** : secteur ν reflète astropy (Komatsu 2011 Eq. 26,
   constantes identiques, oracles < 10⁻⁶ jusqu'à z = 1100) ; mapping
   DESI officiel ωbc = Ωm h² − Σmν/93.14 (yaml épinglé, vérifié exact
   sur les chaînes officielles à 9×10⁻⁹ près) ; ων d'Aubourg
   (0.0107·Σmν) et de DESI (Σmν/93.14) chacun dans sa formule d'origine.

## §4 — Résultats M5 : fits des 5 combinaisons × 2 modèles (pipeline gelé)

Best-fits MAP (Nelder-Mead multi-départs Sobol seedés, 24 ΛCDM /
40 w0waCDM, committés avant les runs ; convergence vérifiée par audit :
4 optimiseurs indépendants coïncident à 2×10⁻⁷, dispersion des départs
~10⁻¹³). Convention σ : Δχ²_MAP → CDF χ²(2 dof) → équivalent gaussien
[Eq. (22)] — la conversion reproduit les 5 paires publiées de la Table 6.

| Bras | n | χ²_ΛCDM | χ²_w0wa | Δχ²_MAP | Nσ | publié | fenêtre | gate |
|---|---|---|---|---|---|---|---|---|
| BAO seul | 13 | 10.271 | 5.619 | −4.652 | **1.66** | 1.7 | [1.5, 1.9] | G5.1 PASS |
| BAO+CMB | 16 | 12.761 | 6.784 | −5.977 | **1.96** | 2.4 (ancrage exact) | [2.1, 2.7] | G5.2 **FAIL** |
| BAO+CMB+Pantheon+ | 1606 | 1418.52 | 1412.12 | −6.406 | **2.05** | 2.8 (full CMB) | [1.8, 3.1] | G5.3 PASS |
| BAO+CMB+Union3 | 38 | 41.163 | 29.033 | −12.131 | **3.05** | 3.8 (full CMB) | [2.8, 4.1] | G5.4 PASS |
| BAO+CMB+DES-SN5YR | 1845 | 1662.20 | 1645.74 | −16.456 | **3.65** | 4.2 (full CMB) | [3.2, 4.5] | G5.5 PASS |

G5.6 (ordre) : 2.05 (P+) < 3.05 (Union3) < 3.65 (DESY5) — PASS.

ΔAIC = Δχ²_MAP + 4 ; ΔBIC = Δχ²_MAP + 2 ln n : BAO −0.65/+0.48 ;
BAO+CMB −1.98/−0.43 ; +P+ −2.41/+8.35 ; +Union3 −8.13/−4.86 ;
+DES −12.46/−1.42 → en BIC (plus punitif), seul Union3 garde une
préférence nette pour w0waCDM ; rapporté en complément comme prévu.

Repères de réplication exacte : BAO-seul ΛCDM (Ωm = 0.2975,
h·rd = 101.54 Mpc) = valeurs publiées DESI DR2 chiffre pour chiffre ;
best-fits w0 des bras SNe proches des publiés (P+ −0.864 vs −0.838 ;
Union3 −0.704 vs −0.667 ; DES −0.778 vs −0.752).

**Effet de compression mesuré (P4 / GO M1.2a)** — écart Nσ_pipeline −
Nσ_publié sur les bras +SNe (full CMB chez DESI, compressé chez nous) :
P+ **−0.75σ**, Union3 **−0.75σ**, DES **−0.56σ** — du même ordre que le
−0.7σ que DESI mesure lui-même sur BAO+CMB (2.4σ compressé vs 3.1σ
full). NB : cet « effet de compression » mesuré ici contient AUSSI le
biais θ* identifié par l'audit (§5) ; la part purement compression vs
part θ* n'est pas séparable sans refaire les fits avec un θ* exact.

## §5 — Audit du gate G5.2 (pré-enregistré : échec ⇒ STOP, audit, jamais
## de relâchement silencieux)

G5.2 est l'ancrage EXACT (DESI publie 2.4σ avec la MÊME compression).
Audit en 5 sondes indépendantes (workflow multi-agents, scripts et
sorties sous `results/audit/`) :

- **Minimiseur hors de cause** (sonde C) : differential_evolution
  seedé, Nelder-Mead (du best-fit M5 ET du point officiel), Powell —
  tous convergent vers χ²_ΛCDM = 12.760649, χ²_w0wa = 6.783639
  (écarts ≤ 2×10⁻⁷) ; dispersion des 24/40 départs ~10⁻¹³. Les warnings
  inf−inf du simplexe sont cosmétiques.
- **Conventions et constantes exactes** (sonde D) : HS96 (E-1), Aubourg
  Eq. (16), EH98 Eq. (5), moyennes/covariance du prior, inflate_cov
  false, mapping mnu/93.14 — tous vérifiés caractère par caractère
  contre les sources et le yaml officiel. AUCUN bug de transcription.
- **Bras BAO hors de cause** (sondes A, B) : notre χ²_BAO recalculé aux
  points des chaînes officielles (colonnes chi2__BAO par point) coïncide
  à +0.13/+0.24 près en moyenne, entièrement expliqué par r_d Aubourg
  bas de −0.028 % (vs rdrag CAMB des chaînes, quasi constant,
  σ ≈ 10⁻⁵ relatif) — effet différentiel < 0.05 sur Δχ².
- **Cause identifiée : biais θ* du modèle HS96+EH98** (sondes A, D) :
  notre θ* est systématiquement bas de −0.10 à −0.13 % (−4.7 à −5.3σ du
  prior !), avec une dépendance résiduelle aux paramètres (scatter
  0.033 %) ; notre χ²_CMB recalculé aux points des chaînes officielles
  est gonflé de +30 à +34 en moyenne. La likelihood officielle calcule
  θ* avec CAMB 1.5.4 (recombinaison complète) ; HS96 est précis au
  pourcent — 40× la largeur du prior. C'est EXACTEMENT la limitation
  pré-enregistrée P2, qui désignait G5.2 comme sa borne empirique.
- **Attribution quantifiée** (sonde E, diagnostic — PAS une correction) :
  en décalant la moyenne θ* du prior par le biais mesuré (−1.013×10⁻⁵),
  les MÊMES fits donnent Δχ²_MAP = −7.544 → 2.27σ (dans la fenêtre
  [2.1, 2.7] ; 77 % de l'écart récupéré), et le best-fit w0waCDM rejoint
  le margestats officiel (h 0.639 vs 0.637 ; w0 −0.461 vs −0.43±0.22 ;
  wa −1.590 vs −1.72±0.64). Le résidu (~23 %) est cohérent avec la
  dépendance paramétrique du biais + r_d (0.028 %) + arrondi de
  l'ancrage publié.
- **Validation croisée de l'ancrage** (sonde A) : reconstruit depuis les
  chaînes officielles elles-mêmes (min de chi2__BAO+chi2__CMB_compressed),
  Δχ²_MAP officiel = −7.965 ≈ −8.0 publié.

**Statut** : G5.2 reste FORMELLEMENT ÉCHOUÉ avec le pipeline gelé —
aucun recalibrage silencieux (P2/GO M1.2b). La cause est attribuée, avec
mécanisme et quantification, à la fidélité du θ* analytique (HS96+EH98)
face à σ(θ*)/θ* = 2.5×10⁻⁴, pas à un bug. Toute remédiation (θ* CAMB,
correction calibrée et pré-enregistrée, ou acceptation en limitation)
est une décision méthodologique qui requiert un GO explicite.

→ Décision de Téo (GO du 2026-06-11) : amendement calibré P8
(PREREGISTRATION.md P8 — transparence totale : décidé APRÈS l'audit,
même statut que la recalibration Keeley du P0). Voir §6.

## §6 — Résultats M5 corrigés P8 (gates G5.xb, mêmes fenêtres)

Amendement P8 : deux constantes multiplicatives sur les sorties
analytiques des bras CMB, calibrées sur les chaînes officielles
épinglées — κ_r = 1.000279376 (r_d Aubourg), κ_θ = 1.001314308 (θ*).
Le scatter résiduel post-correction (7.6×10⁻⁶ ≈ 0.03σ_prior) montre
qu'une constante capture la quasi-totalité du biais ; rien d'autre n'a
changé (vérifiable : seuls les points d'entrée `DESIParams.r_drag_mpc`
et `DESIParams.theta_star` appliquent κ). Le tableau brut (§4) reste le
résultat du pipeline purement analytique.

| Bras | χ²_ΛCDM | χ²_w0wa | Δχ²_MAP | Nσ | publié | fenêtre | gate |
|---|---|---|---|---|---|---|---|
| BAO seul | 10.271 | 5.619 | −4.652 | **1.66** | 1.7 | [1.5, 1.9] | G5.1b PASS |
| BAO+CMB | 15.151 | 7.129 | **−8.023** | **2.36** | 2.4 / −8.0 (ancrage exact) | [2.1, 2.7] | G5.2b PASS |
| BAO+CMB+Pantheon+ | 1420.95 | 1413.37 | −7.574 | **2.28** | 2.8 (full CMB) | [1.8, 3.1] | G5.3b PASS |
| BAO+CMB+Union3 | 43.584 | 29.790 | −13.794 | **3.29** | 3.8 (full CMB) | [2.8, 4.1] | G5.4b PASS |
| BAO+CMB+DES-SN5YR | 1664.66 | 1646.67 | −17.984 | **3.84** | 4.2 (full CMB) | [3.2, 4.5] | G5.5b PASS |

G5.6b (ordre) : 2.28 (P+) < 3.29 (Union3) < 3.84 (DESY5) — PASS.
**6/6 gates verts.** Le bras BAO seul est identique au §4 (P8 ne le
touche pas, comme déclaré).

Points de réplication frappants :
- G5.2b : Δχ²_MAP = −8.023 vs −8.0 publié ; best-fit w0waCDM
  (Ωm = 0.3509, h = 0.6372, w0 = −0.445, wa = −1.645) vs margestats
  officiel (0.353, 0.637, −0.43 ± 0.22, −1.72 ± 0.64) ; best-fit ΛCDM
  χ² = 15.151 vs 15.145 reconstruit des chaînes officielles.
- Bras SNe, best-fits (w0, wa) vs publiés [Table 5] : P+ (−0.853, −0.52)
  vs (−0.838, −0.62) ; Union3 (−0.686, −0.99) vs (−0.667, −1.09) ;
  DES (−0.766, −0.78) vs (−0.752, −0.86).

**Effet de compression re-mesuré proprement (post-P8)** —
Nσ_pipeline − Nσ_publié(full CMB) : P+ **−0.52σ**, Union3 **−0.51σ**,
DES **−0.36σ**, à comparer au **−0.7σ** que DESI mesure sur BAO+CMB
(2.4σ compressé vs 3.1σ full). L'effet est systématiquement
atténuateur et du même ordre ; il est plus faible sur les bras où les
SNe dominent l'information sur (w0, wa) — attendu, la compression ne
dégrade que le canal CMB.

ΔAIC/ΔBIC (k = 2 ; n = points du bras) : BAO −0.65/+0.48 ; BAO+CMB
−4.02/−2.48 ; +P+ −3.57/+7.19 ; +Union3 −9.79/−6.52 ; +DES −13.98/−2.94.

## §7 — M6 : posteriors MCMC w0waCDM (emcee, pipeline P8)

Réglages committés avant les runs (P7) ; convergence exigée
(n_pas − burn) > 50τ partout — la première tentative a échoué ce
critère sur BAO+CMB (50τ = 9312 > 8000) et les chaînes des bras CMB ont
été allongées (le critère n'a jamais bougé) ; seeds dérivés de
20260611 ; walkers initialisés en boule autour du MAP M5b. Artefacts :
results/m6_mcmc.json, results/chains/*.npz (aplaties, thin τ/2),
results/figures/m6_corner_*.png.

Moyennes marginalisées ± écart-type vs publiés [Table 5 ; full CMB chez
DESI sauf BAO seul ; BAO+CMB comparé au margestats officiel compressé] :

| Bras | w0 | w0 publié | wa | wa publié | d((w0,wa), ΛCDM) eucl. / Mahal. |
|---|---|---|---|---|---|
| BAO seul | −0.476 ± 0.262 | −0.48 +0.35/−0.17 | −1.660 ± 0.963 | < −1.34 (68 %) | 2.84 / 3.20 |
| BAO+CMB | −0.430 ± 0.217 | −0.43 ± 0.22 (officiel compressé) | −1.709 ± 0.633 | −1.72 ± 0.64 | 1.74 / 2.60 |
| +Pantheon+ | −0.848 ± 0.056 | −0.838 ± 0.055 | −0.552 ± 0.220 | −0.62 +0.22/−0.19 | 0.54 / 2.65 |
| +Union3 | −0.675 ± 0.090 | −0.667 ± 0.088 | −1.041 ± 0.310 | −1.09 +0.31/−0.27 | 1.04 / 3.50 |
| +DES-SN5YR | −0.761 ± 0.058 | −0.752 ± 0.057 | −0.806 ± 0.239 | −0.86 +0.23/−0.20 | 0.81 / 4.09 |

Constats : (i) le posterior BAO+CMB compressé reproduit le margestats
officiel à la 2e décimale sur les deux paramètres ET leurs largeurs ;
(ii) sur les bras +SNe, malgré le CMB compressé, les moyennes et σ
marginalisés de (w0, wa) collent aux publiés full-CMB à ±0.01 près sur
w0 (l'effet de compression dégrade le Δχ²_MAP, pas sensiblement les
marges de w0/wa) ; (iii) la distance du MAP à (−1, 0) est donnée en
euclidien et en Mahalanobis 2D (covariance marginale (w0, wa) de la
chaîne) — métrique distincte de la convention Nσ d'Eq. (22), rapportée
à titre descriptif (SPEC M6).

## §8 — M7 : profil de sensibilité low-z (coupures P5, CLOSES au GO M1)

Pipeline P8, mêmes moteur et nombres de départs que M5b ; baselines =
bras complets de §6 ; métrique de tableau FIGÉE (P5) ; SHA256 de chaque
sous-échantillon consigné dans results/m7_cuts.json. Coupures :
C-a z > 0.1 ; C-b exclusion CfA (IDSURVEY 61-66) + CSP (5), Foundation
(150) et low-z divers P+ conservés ; C-c DES pur (IDSURVEY = 10) / P+
z > 0.1 ; C-d z > 0.025 (contrôle Dovekie).

**BAO+CMB+Pantheon+** (baseline : N = 1590, Δχ²_MAP = −7.574, 2.279σ,
w0 = −0.853, wa = −0.522) :

| Coupure | N_SNe | Δχ²_MAP | Nσ | ΔNσ | w0_MAP | wa_MAP | Δw0 | Δwa |
|---|---|---|---|---|---|---|---|---|
| C-a | 960 | −6.247 | 2.014 | −0.265 | −0.780 | −0.715 | +0.073 | −0.193 |
| C-b | 1357 | −7.155 | 2.198 | −0.081 | −0.845 | −0.544 | +0.008 | −0.021 |
| C-c | 960 | −6.247 | 2.014 | −0.265 | −0.780 | −0.715 | +0.073 | −0.193 |
| C-d | 1322 | −6.921 | 2.152 | −0.127 | −0.852 | −0.522 | +0.001 | −0.000 |

**BAO+CMB+DES-SN5YR** (baseline : N = 1829, Δχ²_MAP = −17.984, 3.837σ,
w0 = −0.766, wa = −0.778) :

| Coupure | N_SNe | Δχ²_MAP | Nσ | ΔNσ | w0_MAP | wa_MAP | Δw0 | Δwa |
|---|---|---|---|---|---|---|---|---|
| C-a | 1632 | −3.887 | 1.464 | **−2.373** | −0.819 | −0.616 | −0.052 | +0.162 |
| C-b | 1753 | −16.160 | 3.607 | −0.230 | −0.755 | −0.806 | +0.011 | −0.028 |
| C-c | 1635 | −4.184 | 1.540 | **−2.297** | −0.811 | −0.639 | −0.045 | +0.139 |
| C-d | 1829 | −17.984 | 3.837 | ±0.000 | −0.766 | −0.778 | −0.000 | +0.000 |

Lecture factuelle (aucune conclusion physique au-delà du profil) :

- Le bras DES-SN5YR perd l'essentiel de sa préférence dès que les SNe
  z < 0.1 (ou tout le low-z externe) sont retirées : 3.84σ → 1.46-1.54σ
  — miroir quantitatif du test de DESI (Fig. 14, « incertitudes
  élargies, significativité réduite ») et du mécanisme pointé par
  Efstathiou : les best-fits (w0, wa) bougent PEU (Δw0 ≈ −0.05,
  Δwa ≈ +0.15), c'est le pouvoir contraignant qui s'effondre.
- En revanche, l'exclusion ciblée des échantillons historiques
  (CfA + CSP, Foundation conservé — le test de 2502.04212) ne coûte que
  −0.23σ : dans NOTRE profil, la sensibilité vient du retrait de tout
  le levier z < 0.1, pas spécifiquement des relevés historiques.
- La coupure Dovekie z > 0.025 est strictement neutre pour DES (aucune
  SN du release sous z = 0.025 — cohérence vérifiée, ΔNσ = 0 exact).
- Le bras Pantheon+ est robuste : 2.28σ → 2.01σ (z > 0.1), −0.08σ
  (CfA+CSP), −0.13σ (z > 0.025). Contrôle interne : C-c(P+) ≡ C-a(P+)
  chiffre pour chiffre, comme attendu par construction.
