# MILESTONES — append-only

Journal des jalons et décisions. Une fois committée, une entrée ne s'édite
jamais ; toute correction est une nouvelle entrée datée.

---

## 2026-06-11 — M0 : bootstrap

- Création du repo `desi-w0wa-refit` (nom par défaut du SPEC) dans
  `C:\Users\flash\dev\desi-w0wa-refit`. Note : le dossier courant de la
  session était `C:\windows\system32` (non utilisable comme dossier de
  travail) ; emplacement choisi et signalé au STOP M1.
- Le prompt fondateur a été ajusté par Téo en cours de M0 (avant le premier
  commit) ; SPEC.md = copie intégrale de la version ajustée. Ajouts notables :
  réponse DES arXiv:2511.07517, politique d'effort, identité git, Keeley 2024
  (covariance Pantheon+) en limitation M8, download atomique/idempotent.
- SPEC.md (immuable), CLAUDE.md (<200 lignes), MILESTONES.md, PROGRESS.md.
- git init ; identité locale `Téo Alletz <teo.alletz@gmail.com>` configurée
  avant le premier commit.
- pyproject (uv, src layout, package `desi_w0wa_refit`), ruff, pyright
  strict, pytest (marker `requires_data`), CI GitHub Actions matrice
  ubuntu/windows. Licence MIT (défaut du SPEC).
- M1 lancé en parallèle (ultracode, conformément au SPEC) : 7 extractions
  sourcées — DESI DR2 (2503.14738), bao_data, DES-SN5YR, Union3,
  compression CMB, coupures low-z (2408.07175, 2502.04212) + ancrage
  Pantheon+ (2202.04077), réponse DES (2511.07517) + Keeley 2024.
  Recoupement croisé prévu avant le STOP M1.

## 2026-06-11 — M1 : extraction des conventions (terminée, en attente du GO)

- 7 extractions rentrées ; RESULTS.md §1-2 rédigé avec n° de
  section/équation/table pour chaque fait.
- Recoupement croisé : Table 4 (DESI DR2) vs fichiers bao_data — concordance
  chiffre à chiffre sur les 13 points et covariances (deux agents, deux
  sources indépendantes).
- Contre-vérification adversariale (agent indépendant, LaTeX brut) des
  Eqs. (22), (35), (36), priors, Tables 5-6 : 6/6 confirmés. Trouvaille :
  θ* imprimé à 5 décimales dans le papier (troncature source) vs
  σ(θ*) ≈ 2.6×10⁻⁶ — à traiter au GO M1.
- Découvertes critiques : DES-SN5YR à épingler au tag v1.2 (main = Dovekie
  2026, 1820 SNe ≠ papier 2024) ; bao_data tag v2.6, ordre Lyα inversé
  (DH avant DM) ; covariance DES totale = STAT+SYS + diag(MUERR_FINAL²) ;
  ancrage exact publié du pipeline compressé DESI+(θ*,ωb,ωbc)_CMB = 2.4σ
  [Table 6].
- Union3 : décision best-effort → INCLUS (fichiers cobaya sn_data, usage
  identique à DESI ; limite Kim arXiv:2412.14181 documentée en M8).
- STOP M1 présenté à Téo : plan M2-M9, choix CMB (Option A = compression
  DESI Eqs. 35-36 recommandée), traitement r_d, tolérances de gates,
  coupures M7 candidates. En attente du GO.

## 2026-06-11 — GO M1 GLOBAL de Téo (4 décisions validées, avec conditions)

1. CMB : Option A (compression DESI, Eqs. 35-36, Lemos & Lewis 2023).
   Conditions : (a) formules de fitting r_s(z_drag)/z*/r_s(z*) extraites des
   papiers (n° d'équations), pré-enregistrées et committées en DÉBUT de M2,
   avant tout code CMB ; (b) oracle permanent : la formule reproduit le r_d
   fiducial du papier DESI (valeur extraite, jamais de mémoire) à la
   précision documentée de la formule ; (c) θ* tronqué : effort borné
   (≤ 1 session) pour trouver la valeur complète dans les produits publics
   DESI (desilike, chaînes, notebooks App. A) ; sinon 0.01041 + test de
   sensibilité pré-enregistré (θ* ± 5e-6, effet rapporté en Nσ par bras).
2. Gates deux niveaux : validés tels quels. Précisions : (a) sur les bras
   +SNe, l'écart mesuré vs publié est RAPPORTÉ comme mesure de l'effet de
   compression (référence : −0.7σ mesuré par DESI sur BAO+CMB) ; (b) gate
   échoué pour cause plausible de minimiseur (scipy vs iminuit) : audit
   documenté, jamais de relâchement silencieux ; l'ordre P+ < Union3 < DESY5
   est un gate à part entière.
3. Coupures M7 (a)-(d) : validées et CLOSES — aucune coupure ajoutée après
   les premiers chiffres. Métrique de rapport pré-enregistrée avant tout
   run M7 : ΔNσ par coupure + déplacement du best-fit (w0, wa), format de
   tableau figé.
4. Repo : C:\Users\flash\dev\desi-w0wa-refit conservé. Ancrages = ère DR2
   exclusivement (DES v1.2/Zenodo, Tables 5-6) ; Dovekie (3.2σ) = contexte
   M8 uniquement, jamais un ancrage.

Périmètre inchangé : M2 ne démarre qu'avec les formules r_s committées.
Prochain STOP : fin M5 (gates d'ancrage), rapport chiffré complet avant M6.

## 2026-06-11 — Conditions du GO M1 levées, pré-enregistrement committé

- (1a) Formules extraites des papiers, constantes verbatim : Aubourg 2015
  Eq. (16) (r_d, précision 0.021 %), HS96 Eq. (E-1) (z*), EH98 Eq. (4)
  (z_d, information), r_s intégral [EH98 Eqs. (5)-(6)] ; cross-check :
  formule du papier DESI lui-même [2503.14738v3, Eq. (2)].
- (1b) Oracle r_d : point d'ancrage publié Eq. (2) = 147.05 Mpc au point
  Planck (le papier ne publie pas de r_d fiduciel isolé) ; tolérance 0.3 %.
- (1c) θ* complet TROUVÉ dans les produits officiels (yaml des chaînes
  DESI DR2, data.desi.lbl.gov, contre-vérifié sur 2 fichiers) :
  (0.01041027, 0.02223208, 0.14207901) + covariance complète. Test de
  sensibilité P6 caduc (clause conditionnelle non déclenchée).
- Conventions neutrinos baseline extraites (Σmν = 0.06 eV un état massif,
  Neff = 3.044, Ωm inclut ν non relativistes, ωbc les exclut).
- Limitation pré-enregistrée : précision percent-level de z* HS96 vs
  σ(θ*)/θ* ≈ 2.5e-4 — bornée par le gate G5.2, jamais recalibrée en
  silence.
- PREREGISTRATION.md committé → M2 ouvert.

## 2026-06-11 — M2 : likelihood BAO + download épinglé (terminé)

- `data_manifest.json` : 3 fichiers épinglés (bao_data ALL_GCcomb mean+cov
  au commit b7b8a36 = v2.6 ; yaml officiel DESI du prior CMB compressé) avec
  SHA256 calculés au premier download et vérifiés à chaque run.
- `scripts/download_data.py` : stdlib seul, atomique (tmp+rename),
  idempotent (skip si hash OK), erreur dure si mismatch. Seule étape réseau.
- `src/desi_w0wa_refit/bao.py` : parsing bao_data + validation covariance
  (finitude, symétrie, Cholesky — pattern P0) + χ² gaussien (Cholesky solve),
  identique en convention à cobaya `bao.desi_dr2` (logp = −χ²/2, rs_fid=1).
- Vérité terrain au download : 13 points conformes, ordre Lyα DH-avant-DM
  confirmé ; yaml DESI = valeurs pré-enregistrées EXACTES ; bonus extrait
  du yaml : mapping officiel `omch2 = omm·(H0/100)² − mnu/93.14 − ombh2`
  (consigné dans PREREGISTRATION P2).
- Découverte mineure documentée : la Table 4 du papier TRONQUE au moins une
  valeur (38.98897… imprimé 38.988) — tolérance du test d'ancrage 1e-3,
  commentée dans le test.
- 20 tests verts (13 unitaires + 7 ancrages requires_data) ; auto-skip
  sans data/ vérifié (13 passed, 7 skipped). ruff/format/pyright strict :
  zéro erreur.

## 2026-06-11 — M3 : likelihoods SNe + gates d'ancrage (terminé, 4/4 PASS)

- Données épinglées (data_manifest.json, SHA256 au premier download) :
  Pantheon+ DataRelease commit `c447f0f` (dat + cov STAT+SYS) ; DES-SN5YR
  tag v1.2 commit `95cf14c` (HD.csv, STAT+SYS.txt.gz, chaînes officielles
  fw0wacdm_SN/flcdm_SN, script likelihood officiel comme référence de
  convention) ; Union3 cobaya sn_data commit `61d9643`.
- Trouvaille décisive : l'entête de la chaîne officielle fw0wacdm_SN.txt
  contient les priors exacts (omega_m U[0.01,0.99], h0 U[0.3,1],
  w U[-5,1], wa U[-20,10], m U[-1,1]) → gate G3.3 évalué avec CES priors,
  comme pré-enregistré (« les MÊMES priors que la chaîne »).
- sne.py : marginalisation analytique de l'offset (Goliath A9-A12),
  équivalente à la projection cobaya à la constante +ln(c/2π) près
  (exposée pour la comparaison DES) ; P+ coupé zHD > 0.01 (1701 → 1590) ;
  DES cov totale = STAT+SYS + diag(MUERR_FINAL²) (1829) ; Union3 22 nœuds.
- Décision documentée : la cov STAT+SYS Pantheon+ publiée porte des
  asymétries d'arrondi du dernier chiffre imprimé (778 entrées, max
  3e-8) → symétrisée sous garde-fou dur 1e-7 (les consommateurs
  officiels — cobaya, script DES — ne vérifient jamais la symétrie).
- Composition DES vérifiée : 1635 DES + 8 CSP + 68 CfA + 118 Foundation —
  concordance exacte avec Huang et al. 2502.04212.
- GATES (résultats, PREREGISTRATION P3) — TOUS PASSÉS :
  - G3.1 P+ ΛCDM SN-only : Ωm = 0.3316 (ancrage 0.334, écart 0.0024 < 0.010).
  - G3.2 DES ΛCDM SN-only : Ωm = 0.3520 (ancrage 0.352, écart 0.00002 < 0.010).
  - G3.3 DES w0waCDM SN-only vs chaîne officielle pondérée, mêmes priors,
    emcee seedé (32 walkers, 6000 pas, burn 1500, seed dérivé
    « m3-g33-emcee », convergence 50·τ vérifiée) : pulls 0.112 (Ωm),
    0.064 (w0), 0.052 (wa) en σ_chaîne — critère < 0.2.
  - G3.4 Union3 : 22 nœuds, cov SPD, Ωm = 0.3559 (la valeur publiée
    Rubin et al. est 0.356 — non utilisée comme gate, cohérence notée).
- Diagnostic (non-gate) : notre log-like convention DES évaluée aux
  points pondérés de la chaîne officielle (99.999999 % du poids) :
  delta = -5.40 ± 2.23 (max 10.7) — explicable par leurs fichiers pippin
  (n=1828) + théorie CAMB vs release (n=1829) + notre fond ; une erreur
  de convention de covariance décalerait de plusieurs centaines. Les
  223/908 points morts polychord (poids total 4e-82, like jusqu'à
  -344692) sont exclus du diagnostic.
- Note de transparence : le runner run_m3_gates.py a été committé pendant
  le premier run (settings identiques) ; le re-run déterministe après
  commit a reproduit les gates à l'identique (mêmes seeds → mêmes
  chiffres), seul le diagnostic a été affiné (filtrage par poids).
- Résultats committés : results/m3_gates.json + tests pytest pérennes
  (G3.1/G3.2/G3.4 re-fittés inline requires_data ; G3.3 asserté depuis
  le JSON committé).

## 2026-06-11 — M4 : modèles + prior CMB compressé (terminé, oracles verts)

- cosmology.py : fond flat w0waCDM indépendant, conventions astropy
  reflétées exactement (E², fermeture plate, neutrinos Komatsu 2011
  Eq. (26) avec constantes identiques — astropy jamais importé dans src,
  oracle uniquement). CPL forme fermée vs intégrale définitoire
  < 1e-12 relatif sur la grille des priors (élargie aux coins G3.3
  w∈[-5,1], wa∈[-20,10]) ; ΛCDM ≡ w0waCDM(-1,0) exact (mêmes chemins) ;
  oracles astropy < 1e-6 (FlatLambdaCDM, Flatw0waCDM, avec et sans
  radiation/neutrinos, jusqu'à z=1100).
- cmb.py : Aubourg Eq. (16) → r_d = 146.855 Mpc au point Planck (ancrage
  publié 147.05, écart 0.133 % < 0.3 %) ; z* HS96 Eq. (E-1) ; r_s(z*)
  intégral EH98 Eq. (5) ; θ* au point moyen du prior = 0.0104001
  (publié 0.0104103, écart 0.097 % — dans la limitation percent-level
  pré-enregistrée P2, bornée par G5.2). Prior compressé P1 vérifié ÉGAL
  au yaml officiel épinglé (test permanent) et arrondissant aux
  Eqs. (35)-(36) imprimées.
- Précision d'interprétation documentée (pas un relâchement) : le
  cross-check Aubourg vs DESI Eq. (2) < 0.3 % est évalué sur ±5σ du
  prior gaussien CMB — seul domaine où r_d est utilisé (le bras BAO-seul
  échantillonne h·rd librement). Mesuré : 0.21 % à ±5σ ; les deux lois
  de puissance divergent loin du point de calibration (0.70 % au coin
  arbitraire ωbc=0.10).
- Intégrateurs rapides (Simpson grille fixe, substitutions a=x² et
  log(1+z)) validés < 1e-7 contre quad adaptatif ; nécessaires aux fits
  M5 (~10× plus rapides).
- Traitement neutrinos fixé (condition M4 du SPEC) : secteur ν astropy
  (Komatsu), Ωm DESI inclut les ν non relativistes via le mapping
  officiel ωbc = Ωm h² − Σmν/93.14 (yaml épinglé) ; conventions ων
  distinctes d'Aubourg (0.0107·Σmν) et de DESI (Σmν/93.14) chacune dans
  sa formule d'origine.

## 2026-06-11 — M5 : fits 5 combinaisons × 2 modèles (5/6 gates PASS,
## G5.2 ÉCHOUÉ → audit pré-enregistré exécuté, cause attribuée)

- Moteur committé AVANT les runs (06ba107) : Nelder-Mead multi-départs
  Sobol seedés (24 ΛCDM / 40 w0waCDM, seeds dérivés de 20260611),
  conversion Nσ vérifiée contre les 5 paires publiées de la Table 6.
- Résultats (results/m5_fits.json, tableau complet RESULTS.md §4) :
  G5.1 1.66σ [1.5,1.9] PASS ; G5.2 1.96σ [2.1,2.7] **FAIL** ;
  G5.3 2.05σ [1.8,3.1] PASS ; G5.4 3.05σ [2.8,4.1] PASS ;
  G5.5 3.65σ [3.2,4.5] PASS ; G5.6 ordre P+ < Union3 < DESY5 PASS.
  Réplication exacte BAO-seul ΛCDM : Ωm = 0.2975, h·rd = 101.54 Mpc.
- Effet de compression mesuré (GO M1.2a) : −0.75σ (P+), −0.75σ (Union3),
  −0.56σ (DES) vs le −0.7σ que DESI mesure sur BAO+CMB.
- AUDIT G5.2 (mot-clé ultracode, workflow 5 sondes indépendantes,
  artefacts results/audit/) — verdict unanime, AUCUN bug : minimiseur
  parfait (4 optimiseurs, mêmes minima à 2e-7) ; constantes vérifiées
  aux sources caractère par caractère ; bras BAO innocenté (r_d Aubourg
  −0.028 % vs rdrag CAMB des chaînes officielles, différentiel < 0.05 en
  Δχ²) ; CAUSE = biais θ* du modèle analytique HS96+EH98 : −0.10 à
  −0.13 % ≈ −5σ du prior, scatter paramétrique 0.033 %, χ²_CMB gonflé de
  +30 vs les colonnes chi2__CMB_compressed officielles. Diagnostic
  d'attribution (PAS une correction) : prior θ* décalé du biais mesuré →
  Δχ²_MAP = −7.544 → 2.27σ (dans la fenêtre), best-fit aligné sur le
  margestats officiel. Ancrage validé depuis leurs propres chaînes
  (Δχ²_MAP reconstruit −7.965 ≈ −8.0).
- C'est exactement la limitation pré-enregistrée P2 (z* HS96 percent
  level vs σ(θ*)/θ* = 2.5e-4), qui désignait G5.2 comme sa borne
  empirique. Conformément à P2/GO M1.2b : G5.2 reste FORMELLEMENT
  ÉCHOUÉ, aucun recalibrage silencieux ; toute remédiation (θ* CAMB,
  correction calibrée pré-enregistrée, ou acceptation en limitation)
  attend le GO de Téo au STOP M5.
- Données d'audit épinglées au manifest : chaînes officielles DESI
  base/base_w_wa du bras compressé (8 fichiers + 2 margestats, SHA256) —
  colonnes par point chi2__BAO, chi2__CMB_compressed, rdrag.
- Note de transparence : une erreur 50x transitoire de data.desi.lbl.gov
  a produit un premier margestats base_w_wa corrompu (page HTML),
  détecté à la vérification de taille et re-téléchargé avant épinglage.

## 2026-06-11 — GO Téo décision G5.2 : option (b), amendement calibré P8

- Conditions du GO : P8 committé avant tout re-run (nature constante,
  source de calibration ordonnée, transparence totale) ; rien d'écrasé
  (tableau brut conservé, gate corrigé = G5.2b) ; re-run M5 complet ;
  CAMB/CLASS restent hors périmètre ; fallback = option (a) si G5.2b
  pas vert sans autre changement. Après re-run vert : GO M6 + M7
  enchaînés, prochain STOP fin M7.
- L'ancrage publié Eq. (2) jugé insuffisant pour θ* (calibre l'époque
  drag ; biais audités différents −0.028 % vs −0.13 %) → calibration
  sur les chaînes officielles épinglées (préférence (ii) du GO).
- scripts/calibrate_p8.py : κ_r = moyenne pondérée rdrag_CAMB/r_d_Aubourg ;
  κ_θ par inversion de la quadratique chi2__CMB_compressed avec
  assignation de racine itérée à point fixe — le choix naïf « racine la
  plus proche de notre valeur brute » sous-estimait κ_θ de ~0.02 %
  (systématique de racine basse, identifié et corrigé AVANT le commit
  des constantes). Valeurs committées : κ_r = 1.000279376,
  κ_θ = 1.001314308 (scatter résiduel 7.6e-6 ; accord inter-modèles 6e-6).
- P8 committé (9411591) AVANT le re-run.

## 2026-06-11 — M5b : re-run complet P8 — 6/6 gates VERTS

- G5.1b 1.656σ (identique au brut — P8 ne touche pas le bras BAO, comme
  déclaré) ; G5.2b Δχ²_MAP = −8.023 → 2.363σ (ancrage −8.0/2.4σ ;
  best-fits alignés sur les produits officiels à ~4 décimales) ;
  G5.3b 2.279σ ; G5.4b 3.288σ ; G5.5b 3.837σ ; G5.6b ordre OK.
- Effet de compression re-mesuré proprement : −0.52σ (P+), −0.51σ
  (Union3), −0.36σ (DES) vs −0.7σ mesuré par DESI sur BAO+CMB.
- Résultats : results/m5_fits_corrected.json ; RESULTS.md §6 (le
  tableau brut §4 et le verdict G5.2 FAIL restent dans l'historique).
- Fallback du GO non déclenché. Enchaînement M6 puis M7 (runners
  committés avant leurs runs : e8d5a9e).

## 2026-06-11 — M6 : posteriors MCMC w0waCDM (5 bras, convergés)

- emcee, seeds dérivés de 20260611, walkers en boule autour du MAP M5b,
  convergence exigée (n_pas − burn) > 50τ. Première tentative : échec du
  critère sur BAO+CMB (50τ = 9312 > 8000) → chaînes des bras CMB
  allongées (22000/16000/20000/16000, burn 3000, commit da5257c AVANT la
  relance) ; le critère lui-même n'a jamais bougé. Tous les bras
  convergés (τ_max : 133/234/65/64/66).
- Réplications (moyennes ± σ marginalisés vs publiés Table 5) :
  BAO seul w0 = −0.476±0.262 (publié −0.48 +0.35/−0.17) ; BAO+CMB
  w0 = −0.430±0.217, wa = −1.709±0.633 (margestats officiel compressé :
  −0.43±0.22, −1.72±0.64 — réplication à la 2e décimale) ; bras +SNe
  collent aux publiés full-CMB à ±0.01 sur w0. Détails RESULTS.md §7.
- Artefacts committés : results/m6_mcmc.json, chaînes aplaties
  results/chains/*.npz, corner plots results/figures/m6_corner_*.png.

## 2026-06-11 — M7 : profil de sensibilité low-z (terminé) — STOP fin M7

- Coupures P5 (closes au GO M1), pipeline P8, baselines M5b, métrique
  figée, SHA256 des sous-échantillons consignés (déviation documentée :
  hash au premier run M7 plutôt qu'au download M2).
- Résultat saillant : la préférence du bras DES-SN5YR s'effondre sans le
  low-z externe (3.84σ → 1.46σ pour z > 0.1 ; 1.54σ pour DES pur), avec
  des best-fits (w0, wa) quasi inchangés — c'est le pouvoir contraignant
  qui disparaît ; l'exclusion ciblée CfA+CSP (Foundation conservé) ne
  coûte que −0.23σ ; z > 0.025 strictement neutre (aucune SN DES sous
  0.025). Pantheon+ robuste (2.28 → 2.01/2.20/2.15σ). Contrôle interne
  C-c(P+) ≡ C-a(P+) exact. Tableaux complets : RESULTS.md §8.
- STOP fin M7 présenté à Téo (rapport complet). Prochain jalon : M8
  (RESULTS final, limites) après GO.

## 2026-06-11 — M8 : RESULTS.md final (terminé) — STOP avant M9

- GO M8 reçu avec exigences explicites (résumé exécutif 3 chiffres,
  lecture M7 pré-enregistrée inchangée, limites complètes, périmètre
  négatif, test de traçabilité).
- §0 résumé exécutif : (1) 6/6 gates b verts, ancrage exact BAO+CMB
  Δχ²_MAP = −8.023 vs −8.0 ; (2) profil M7 DES 3.84 → 1.46σ (z > 0.1)
  MAIS −0.23σ pour CfA+CSP exclus ; (3) Pantheon+ robuste 2.28 → 2.01σ.
  Lecture M7 reprise verbatim de §8 (« la sensibilité vient du retrait
  de tout le levier z < 0.1, pas spécifiquement des relevés
  historiques »), sans attribution causale.
- §9 limites : effet de compression CMB (tableau, étalon −0.7σ DESI),
  statut P8 (amendement calibré assumé, constantes, incident
  d'assignation de racine), Union3 posterior-spline (Kim 2412.14181),
  covariance Pantheon+ (Keeley 2024, zéro correction), z* HS96 → CAMB
  (raffinement v2), Dovekie 4.2σ → 3.2σ (contexte, jamais un ancrage).
- §10 « ce que ce travail ne montre PAS » : ne tranche pas énergie noire
  évolutive vs systématiques ; ne teste aucune calibration
  photométrique ; conditionnel aux datasets DR2-era épinglés et à la
  compression documentée ; aucune conclusion physique.
- Test de traçabilité permanent (tests/test_results_traceability.py,
  8 tests) : chaque chiffre porteur de RESULTS.md (§0, §4, §6, §7, §8,
  constantes P8) recomputé depuis results/*.json à l'arrondi affiché.
- Le test a détecté 4 écarts d'arrondi dans le texte (les JSON committés,
  inchangés, font foi) — corrigés dans RESULTS.md : §4 ΔBIC brut P+
  +8.35 → +8.36 ; §4 effet de compression brut DES −0.56σ → −0.55σ
  (l'entrée M5 de ce journal porte le −0.56 d'origine — append-only,
  correction consignée ici) ; §6 χ²_ΛCDM DES 1664.66 → 1664.65 ;
  §8 w0_MAP DES C-a −0.819 → −0.818. Aucun chiffre de gate ni aucune
  conclusion affectés.
- Rituels : 90 tests verts à l'ouverture ; ruff/format/pyright/pytest
  tout vert à la fermeture (98 tests). JAMAIS pushé.
- STOP fin M8 : relecture de RESULTS.md complet par Téo AVANT M9
  (release, tag et push attendent cette relecture).

## 2026-06-11 — GO M9 conditionnel de Téo, conditions levées

- Condition 1 — traduction anglaise intégrale de RESULTS.md et README
  (public international) : faite, numérotation de sections et chiffres
  identiques ; VF conservée en RESULTS.fr.md (note d'en-tête) ; les
  8 tests de traçabilité re-exécutés verts post-traduction (98 tests au
  total). Déviation documentée : la règle CLAUDE.md « docs *.md en
  français » est levée par ce GO pour les deux documents publics ;
  SPEC/MILESTONES/PROGRESS/PREREGISTRATION restent en français.
- Condition 2 — réserve §2.2 (sélection Pantheon+) LEVÉE, aux sources :
  cobaya `sn.pantheonplus` (likelihood « without SH0ES », l'usage DESI)
  lit zHD et masque `> 0.01` ; identique dans
  `Pantheon+_only_cosmosis_likelihood.py` du release épinglé c447f0f
  (`ww = data['zHD'] > 0.01`), calibrateurs inclus comme SNe ordinaires
  → 1590/1701 = notre implémentation exacte. Le 1580 (Keeley 2024) est
  le compte du MODE SH0ES : masque `(zHD > 0.01) | IS_CALIBRATOR`,
  calibrateurs comparés aux distances Céphéides → 1590 − 10 = 1580
  (vérifié sur le fichier épinglé : 77 calibrateurs, 10 au-dessus de la
  coupure). NB : « 1580 » n'apparaît pas dans Brout et al. 2022
  (vérifié sur les textes arXiv et ApJ).
- M9 engagé : repo public Flasher1717/desi-w0wa-refit, identité git
  locale vérifiée (Téo Alletz <teo.alletz@gmail.com>), compte gh
  basculé Kodiaquebec → Flasher1717 AVANT toute opération GitHub ;
  branche master renommée main (la CI committée ne se déclenche que sur
  main) ; ordre imposé : push → CI verte matrice complète → tag v1.0.0
  → release factuelle zéro adjectif. Rien d'autre ne change — ni
  chiffre, ni test.

## 2026-06-11 — M9 : publication (terminé) — v1.0.0

- Repo public créé et main poussé :
  https://github.com/Flasher1717/desi-w0wa-refit
- CI run 27392820293 : matrice complète VERTE (4/4 : ubuntu/windows ×
  3.11/3.13) AVANT le tag. Annotation non bloquante consignée :
  dépréciation Node 20 des actions checkout@v4 / setup-uv@v5 (bascule
  forcée Node 24 le 2026-06-16) — maintenance future, hors v1.0.0.
- Tag annoté v1.0.0 poussé ; release factuelle publiée :
  https://github.com/Flasher1717/desi-w0wa-refit/releases/tag/v1.0.0
  (contenu : 5 ancrages répliqués, profil M7 3.84→1.46σ / −0.23σ, effet
  de compression mesuré, lien RESULTS.md au tag, renvoi §9-§10 et P8).
- Projet v1 clos. Candidat v2 consigné : θ*/r_d par CAMB (rendrait P8
  caduc, RESULTS.md §9.5).

## 2026-06-12 — Ouverture P2.1 (SPEC_V21.md) + M10 : extraction et
## pré-enregistrement (STOP, en attente du GO)

- Rituel d'ouverture : 98 tests verts, repo propre sur v1.0.0, SPEC +
  PREREGISTRATION + PROGRESS + git log relus. SPEC_V21.md committé
  (copie intégrale immuable du prompt P2.1) ; jalons M10-M14 ajoutés,
  append-only ; résultats v1.0.0 GELÉS.
- M10 (effort ultracode) : revue multi-agents — 4 agents d'extraction
  parallèles (Keeley arXiv:2212.07917v3 Sec. 2 + notes P0 C:\JJP-JANUS ;
  Efstathiou arXiv:2408.07175v3 Sect. 2-3/Table 1 ; règle d'appariement
  V3 sur les fichiers épinglés ; grille V2 + faisabilité sur le pipeline
  local) + 1 agent de recoupement croisé, PUIS contre-vérification
  indépendante par script jetable (non committé) des comptes
  d'appariement et de la réplication Table 1. Anti-injection : aucun
  contenu suspect dans les sources fetchées (consigné par les agents).
- Découvertes M10 porteuses :
  - La règle d'appariement d'Efstathiou (jamais énoncée dans le papier)
    est rétro-ingéniérée et VÉRIFIÉE : paires même-survey (CID normalisé
    + même IDSURVEY) → 332 paires, comptes Table 1 exacts
    (145/118/14/27/18/3/7), toutes les moyennes reproduites au dernier
    chiffre imprimé, différentiel low-z−DES = −0.0360.
  - Les erreurs imprimées ±0.0006 (DES5Y) et ±0.0007 (FOUND) de la
    Table 1 sont des typos décimales ×10 (les 5 autres erreurs
    imprimées se reproduisent exactement avec SEM = std(ddof=0)/√N ;
    valeurs vraies 0.0055 / 0.0070).
  - Appariement objet (Tier P) : 335 objets communs ; 4 low-z DES
    absents de P+ (2001ay, 2004gc, 2007ob, 2007R — absences réelles) ;
    3 objets CfA3K-DES présents dans P+ en CSP seulement ; paire
    1304442 à zHD révisé entre releases (|Δz| = 0.0074).
  - DES-SN5YR ne contient AUCUN IDSURVEY 61/62 ni 18/50/51/56/57 ;
    son CfA = 63-66 (68 SNe), CSP = 5 (8 SNe), Foundation = 150 (118).
  - Keeley Sec. 2 : fiducial FIXE (Ωm 0.3, H0 70, MB −19.0), 10 000
    mocks N(mu_fid, C_released), refit (H0, Ωm, MB) par mock, stat =
    χ²_min, 0/10 000 sous 1387.10 → « > 3.9σ » (conversion two-sided
    non énoncée). Conventions manquantes du papier tranchées en P9.
- PREREGISTRATION.md étendu : P9 (V1 mocks DES : N = 10 000, seeds
  derive_seed m11-v1*, p = (k+1)/(N+1) queue basse, seuil 0.0027,
  secondaires non gating, gates G11.1 synthétique / G11.2 Keeley-P+
  optionnel), P10 (V2 LOO : grilles closes 5 groupes P+ / 3+2 DES,
  métrique figée + σ_curv Hessienne FD à pas fixes, politique
  boundary-MAP, run_m12_loo.py → results/m12_loo.json), P11 (V3 :
  règle d'appariement épinglée 335/332/4/3, Tier R = gate d'ancrage
  Efstathiou NON AVEUGLE — déclaré, même statut assumé que P8 —,
  Tier P = analyse principale aveugle Δμ = MU_SH0ES − MU_DES,
  S = mean low-z − mean high-z, exclusion pré-enregistrée 1304442).
- DÉCISION proposée au STOP (SPEC V2.1 : « à trancher au STOP M10 ») :
  notre méthode réplique exactement celle d'Efstathiou → statut GATE
  D'ANCRAGE retenu pour Tier R, avec non-aveuglement déclaré dans P11.2.
- STOP M10 : AUCUN run M11-M13 effectué ; les seuls calculs sont
  l'extraction/appariement demandés par M10(b) et la vérification de la
  règle. Attente du GO de Téo (questions ouvertes listées en session).

## 2026-06-12 — GO M10 de Téo : 5 décisions + 2 amendements, P9-P11 gelés

- D1 : gate d'ancrage Efstathiou RETENU (G13.1-G13.3, tolérances du
  STOP) ; P11.2 précise EXACTEMENT ce qui a été vu en M10 (tous les
  chiffres Tier R) et ce qui ne l'a pas été (tout le Tier P) + caveat
  d'honnêteté : le Tier P n'est aveugle qu'au sens du non-calcul, sa
  valeur attendue étant contrainte par le Tier R. Typos SEM Table 1 :
  documentées §11 avec démonstration, formulation prudente
  (« apparent decimal typos »).
- D2 : G11.2 (étalon Keeley sur Pantheon+, 10 000 mocks) RETENU,
  gate p_P+ ≤ 0.0027 + |Δχ²| ≤ 1.0 de 1387.10.
- D3 : fiducial V1 primaire = Keeley fixe (Ωm 0.3, H0 70, MB −19.0) ;
  best-fit en secondaire non gating.
- D4 + AMENDEMENT 1 : grille DES 3 primaires + 2 sous-lignes ; ajout
  côté P+ d'une ligne AGRÉGÉE CfA+CSP. Mise en œuvre conforme
  « résultats gelés » : les 2 lignes CfA+CSP (P+ agrégée N=1357, DES
  primaire N=1753) sont par composition EXACTEMENT les C-b de M7 →
  colonnes de fit REPRISES de results/m7_cuts.json (zéro nouveau fit),
  σ_curv par évaluations FD au MAP gelé w0wa_params (vérifié présent
  dans le JSON), test de cohérence sur subset_sha256. Décompte
  corrigé : 9 lignes fraîches = 18 fits (la version STOP annonçait
  « 7+2 = 18 », c'était 8+2 = 20 ; l'amendement ramène à 18).
- D5 : doublons Tier P = même-survey > plus petite m_b_corr_err_DIAG >
  tie-break IDSURVEY ; combinaison covariance en secondaire.
- AMENDEMENT 2 : P11.3 explicite que les corrélations INTER-release
  des Δμ ne sont pas modélisées et que la dispersion empirique des Δμ
  est LA mesure d'incertitude primaire du Tier P.
- Séquence accordée : M11 → M12 → M13 d'une traite, STOP fin M13
  (rapport chiffré des 3 volets). P9-P11 GÈLENT à leurs premiers runs.

## 2026-06-12 — M11 : V1 Keeley-test sur DES-SN5YR (terminé)

- Moteur committé AVANT les runs (a1d1f43) ; P9 gelé au premier run.
- Pilote P9.4 : 50 mocks, chronométrage seul (0.18 s/mock), χ² jetés.
- G11.1 (synthétique, pytest) : percentile empirique de la médiane
  χ²(N−2) à < 2 % — VERT. G11.2 (étalon Keeley sur P+, N = 1580,
  10 000 mocks) : χ²_réel = 1386.405 (|Δ| = 0.695 ≤ 1.0 de 1387.10),
  k = 1/10 000, p = 2.0e-4 ≤ 0.0027 — VERT (Keeley publiait 0/10 000).
- V1 PRIMAIRE (DES-SN5YR, N = 1829, fiducial Keeley Ωm = 0.3,
  10 000 mocks N(mu_fid, C_totale)) : χ²_réel = 1640.083,
  k = 5/10 000, p = 6.0e-4 → verdict pré-enregistré « χ² anormalement
  bas » (z two-sided « convention Keeley » : 3.43σ ; mocks
  mean = 1828.1, std = 59.5). PERSONNE n'avait publié ce test sur
  DES : la covariance DES-SN5YR totale surestime les erreurs, comme
  Pantheon+ chez Keeley. Rapporté tel quel, ZÉRO correction (SPEC V2.1).
- Secondaires non gating : V1b (fiducial au best-fit Ωm = 0.3520) :
  k = 7, p = 8.0e-4 — robuste au fiducial. V1c (sans les 75 lignes
  MUERR_FINAL > 1) : χ²_réel = 1639.39, k = 287, p = 0.0288 —
  l'anomalie s'atténue fortement sans les lignes BEAMS-downweightées.
- Diagnostics descriptifs : std résidus normalisés 0.904 (DES) /
  0.914 (P+ ; Keeley 0.93) ; δ² = +0.002065 (DES) / +0.002185 (P+ ;
  Keeley 0.002). 0 mock flagué sur les 4 runs.
- results/m11_pilot.json + results/m11_mocks.json (χ² des 10 000 mocks
  inclus, arrondis 1e-4, reproductibles par seed).

## 2026-06-12 — M12 : V2 leave-one-group-out (terminé)

- Runner committé AVANT le run (a53e968) ; P10 gelé au premier run.
- Hash C-b de M7 reproduits byte-à-byte pour les DEUX lignes CfA+CSP
  (P+ eba5ac7c…, DES 70289ddf…) → chiffres de fit repris GELÉS,
  σ_curv seul calculé aux MAP gelés (GO M10.4).
- σ_curv baselines (évaluations au MAP gelé, P10.3) : P+ 0.0910/0.3562,
  DES 0.0925/0.3760 (w0/wa ; sous-estiment les σ MCMC m6 comme
  pré-annoncé pour wa asymétrique).
- Bras P+ (baseline 2.279σ) : ΔNσ = CfA −0.028 ; CSP −0.006 ;
  Foundation +0.367 (la préférence MONTE sans Foundation) ;
  misc-lowz −0.436 ; DES-in-P+ −0.598 ; CfA+CSP (repris) −0.081.
- Bras DES (baseline 3.837σ) : ΔNσ = CfA+CSP (repris) −0.230 ;
  Foundation −1.335 (3.84 → 2.50σ — LE levier dominant, 118 SNe) ;
  DES-removed −1.323 (N = 194, MAP dégénéré w0 = −0.46, wa = −1.61,
  σ_curv RETENU par la politique P10.4 : variance de courbure non
  positive, consigné) ; desc. CfA seul −0.274 ; desc. CSP seul +0.036
  (N = 8, caveat petit-N).
- Lecture du paradoxe M7 : côté DES le levier low-z est massivement
  Foundation, pas les échantillons historiques ; côté P+ retirer
  Foundation RENFORCE la préférence. Cohérent avec l'offset
  Foundation d'Efstathiou (V3). Aucune attribution causale.
- results/m12_loo.json ; 18 fits frais ~75 min ; warning Nelder-Mead
  scipy (inf dans le simplexe initial) identique au comportement des
  runs M5/M7 gelés, sans effet.

## 2026-06-12 — M13 : V3 SNe communes appariées (terminé)

- Runner committé AVANT le run (a53e968) ; P11 gelé au premier run.
- Tier R (gates d'ancrage, non-aveuglement déclaré P11.2) : G13.1
  comptes 145/118/14/27/18/3/7 + all-low-z 187 EXACTS ; G13.2 les
  8 moyennes à ±0.001 de la Table 1 (toutes au 4e chiffre) ; G13.3
  différentiel −0.0360 (cible −0.0360 ± 0.002) — 8/8 VERTS.
- Tier P (AVEUGLE, jamais calculé avant ce run) : S = mean(Δμ low-z)
  − mean(Δμ high-z) avec Δμ = MU_SH0ES − MU_DES sur 334 objets
  (1304442 exclu pré-enregistré) : S = −0.0358 ± 0.0080 mag (SEM
  empiriques en quadrature — l'incertitude PRIMAIRE, GO A2).
  Sensibilité avec 1304442 : −0.0363 ± 0.0080. Règle des doublons :
  304 même-survey / 31 plus-petite-erreur. Secondaire
  covariance-aware : σ_S = 0.0334 (les covariances publiées sont
  dominées par les systématiques corrélées ; corrélation cross-release
  inconnue NON modélisée — la dispersion empirique reste la mesure).
- Lecture : les modules de distance des MÊMES SNe diffèrent de
  −0.036 mag (low-z vs high-z) entre les deux compilations — la
  quantité d'Efstathiou (~0.04 mag), répliquée puis confirmée en
  aveugle sur la définition MU. Aucune attribution causale.
- results/m13_pairs.json ; rituel de fermeture : ruff/format/pyright/
  pytest 119 verts (non-régression v1.0.0 incluse).
- STOP fin M13 : rapport chiffré des 3 volets présenté à Téo ;
  M14 (§11 + v1.1.0) attend son GO.

## 2026-06-12 — Correction d'une entrée M13 (append-only)

- L'entrée « M13 » ci-dessus écrit « Règle des doublons : 304
  même-survey / 31 plus-petite-erreur ». C'est FAUX : ces nombres
  venaient d'une note exploratoire M10 (objets à lignes P+ multiples).
  Les compteurs MESURÉS du run (results/m13_pairs.json,
  duplicate_rule_counts) sont : 332 paires résolues par la branche
  même-survey, 3 par la branche plus-petite-erreur (les 3 objets
  cross-survey 2005hj/2005ir/2006ev). Aucun chiffre scientifique
  affecté ; le JSON a toujours fait foi.

## 2026-06-12 — M14 : RESULTS §11 + préparation v1.1.0 (STOP avant push)

- RESULTS.md §11 rédigé (EN) selon le GO M14 : 3 chiffres en tête
  (p_DES = 6×10⁻⁴ étalonné par G11.2 vert ; Foundation −1.34σ/+0.37σ,
  signe opposé entre bras = LE résultat ; S = −0.0358 ± 0.0080) ;
  11.1 V1 avec l'étalon P+ AVANT le verdict DES ; 11.2 tableaux LOO
  des deux bras au même format (σ_curv inclus, ligne DES-retiré
  « withheld » P10.4) ; 11.3 Tier R/Tier P distincts, non-aveuglement
  Tier R déclaré, les DEUX incertitudes de S avec explication de leur
  facteur 4 (budget d'erreur commun annulé dans la différence vs
  double comptage sans corrélation croisée) ; 11.4 cohérence
  descriptive des 3 volets ; 11.5 limites (cross-release : « valeur
  centrale robuste, significativité dépendante du traitement des
  corrélations » dit tel quel, S/σ 4.5 vs 1.1 ; V1c indice descriptif ;
  Dovekie « le terrain bouge » ; typos Table 1 « apparent decimal
  typos » avec démonstration SEM complète) ; 11.6 ce que ça ne montre
  pas (Foundation-pivot ≠ Foundation-fautif ; offset n'identifie pas
  la chaîne de traitement ; rien ne tranche évolution vs
  systématiques ; §10 inchangé).
- Miroir RESULTS.fr.md §11 (mêmes chiffres, mêmes tableaux).
- Traçabilité étendue : 4 nouveaux tests permanents (§11.1 mocks,
  §11.2 LOO deux bras + lignes reprises pointant m7_cuts.json,
  §11.3 Tier R et Tier P) — 123 tests verts. Le nouveau test a
  immédiatement attrapé un écart d'arrondi dans le tableau §11.2
  (w0_MAP P+/Foundation écrit −0.825, JSON → −0.824) : corrigé dans
  les deux documents AVANT tout commit, le JSON fait foi.
- STOP M14 : relecture du §11 complet par Téo ; le tag v1.1.0, la
  release et le push n'auront lieu qu'après son GO de push explicite.

## 2026-06-12 — M14 : publication (terminé) — v1.1.0

- GO de push de Téo reçu (texte de release accepté tel quel, aucune
  retouche aux résultats ni aux tests au moment de publier).
- Compte gh vérifié Flasher1717 ; main poussé (67d5522..93c8dcc).
- CI run 27443759397 : matrice complète VERTE (4/4 : ubuntu/windows ×
  3.11/3.13) AVANT le tag. Annotations non bloquantes inchangées
  (dépréciation Node 20 de checkout@v4 / setup-uv@v5, bascule forcée
  2026-06-16 ; redirection windows-latest → windows-2025-vs2026) —
  maintenance future, hors v1.1.0.
- Tag annoté v1.1.0 poussé ; release factuelle publiée :
  https://github.com/Flasher1717/desi-w0wa-refit/releases/tag/v1.1.0
  (contenu : les 3 chiffres — p_DES = 6×10⁻⁴ avec étalon P+ vert,
  Foundation −1.34σ/+0.37σ, S = −0.0358 ± 0.0080 — renvoi RESULTS.md
  §11.5/§11.6, datasets épinglés inchangés).
- Extension P2.1 (v1.1) CLOSE. Projet en veille.
