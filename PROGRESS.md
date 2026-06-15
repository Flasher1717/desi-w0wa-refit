# PROGRESS

> État courant pour la continuité multi-sessions. Mis à jour à chaque fin de
> session (et aux points clés en cours de session).

## Jalon en cours

Maintenance CI — bump des actions GitHub vers Node 24 (branche `chore/ci-node24`).
v1.2.0 SHIPPÉE le 2026-06-14 : M16 (V4) ✅, M17 (V5) ✅ et M18 (doc §12) ✅ clos ;
projet de nouveau en veille hormis cette maintenance d'outillage.

Fait (v1.2.0 publiée) : GO de push de Téo donné ; `main` poussé (à ab613a0) ;
CI run 27488929240 VERTE 4/4 (ubuntu/windows × py3.11/3.13) AVANT le tag ; tag
`v1.2.0` → ab613a0 ; release factuelle « v1.2.0 — SN covariance & cross-release
sensitivity » marquée *Latest* (2026-06-14). Convention de version inchangée
(pyproject/__init__ restent 0.1.0, comme v1.0.0/v1.1.0). Détail M18 archivé dans
MILESTONES.md (RESULTS §12 EN + miroir fr, 138 → 142 tests, revue ultracode).

Fait (maintenance CI, en cours) : `.github/workflows/ci.yml` — `actions/checkout`
@v4 → @v6 et `astral-sh/setup-uv` @v5 → @v8.2.0 (les deux sur node24 vérifié à la
source ; checkout garde un tag flottant @v6, setup-uv v8 a supprimé les tags
flottants → pin figé @v8.2.0). Aucune autre modif (mêmes jobs, même matrice,
même bloc python-version). Local vert : ruff + format + pyright strict 0/0/0 +
pytest 142. Aucun results/*.json, aucun src/, aucun test touché.

Prochain pas concret : APRÈS GO de push de Téo — pousser `chore/ci-node24`, ouvrir
la PR, confirmer la CI 4/4 VERTE **et zéro annotation de dépréciation Node 20**
(critère du bump), puis STOP en attente du GO de merge (pas de merge auto). Tant
qu'il n'y a pas de GO : STOP, aucun push.

## M17 (V5) — résultats (results/m17_dovekie.json, ancrage G17.1 PASS)

- Baseline Dovekie FRAÎCHE : Nσ = 2.838 (Δχ²=−10.79, w0=−0.821, wa=−0.642) ∈
  [2.4,3.4] (= 3.2 − 0.36 offset compression, comme v1.2). Gate H confirmé
  (χ² droit, aucun poids BEAMS). Loader vérifié à la précision machine.
- LOO Dovekie vs v1.2 : Foundation −0.683 (v1.2 −1.335) ; DES −0.599/withheld
  (v1.2 −1.323) ; CfA+CSP −0.471 (v1.2 −0.230) ; CfA seul −0.407 ; CSP seul
  +0.005. RÉPONSE : Foundation PERSISTE mais ~÷2 (atténué, pas résorbé) ;
  levier low-z redistribué vers CfA/CSP (qui augmente). Inter-release, même
  pipeline ; aucune attribution causale.

## M16 (V4) — résultats (results/m16_v4.json, gates verts)

- Gates : G16.3 refit baseline = Nσ gelé à ~1.6e-9 (P+ 2.279 / DES 3.837) ;
  G16.1 contrôles i-κ exact, ii dans 1e-3, i-s non gaté (1.057/1.098).
- Revue adversariale pré-gel : a attrapé la tolérance ii inatteignable (1e-6),
  corrigée en gate par scénario AVANT le run (P12.5 amendé).
- ΔNσ vs baseline : P+ i-κ +0.068, i-s +0.100, ii −0.814 ; DES i-κ +0.158,
  i-s +0.302, ii +0.740. Hypothèse « C plus petite ⇒ renforcée » confirmée
  pour le rescale (i) ; les deux corrections divergent en signe sur P+
  (rescale +, intrinsic-scatter −). Caveat P+ ii : direction propre
  quasi-singulière (6.1e-5).

## Gate de cohérence H (Dovekie, vérifié au setup M17)

- Likelihood officielle DES-Dovekie-SN_Likelihood.py = χ² gaussien à offset
  marginalisé (Goliath A9-A12 : a − b²/c + ln(c/2π)), AUCUN poids BEAMS par-SN
  (PROBIA_BEAMS = diagnostic). Dépaquetage covariance : inv_cov[triu]=cov,
  reflet symétrique, C=inv(inv_cov), subset de C. → notre approche v1.2 (χ²
  droit, N=1820) est fidèle. Gate H PASS.
- SHA256 Dovekie (commit c9a4fcaf) : HD 2f57019d…0aaf (148002) ;
  STAT+SYS.npz ffd3124b…463b (6244951) ; likelihood 78526c0e…45ff (7674).

## Décisions GELÉES au GO M15 (2026-06-13)

- A : V4 scénario (i) en DEUX sous-variantes — (i-κ) PRIMAIRE C·κ, κ=χ²/N
  (whitening plein, control-exact) + (i-s) DESCRIPTIVE C·s_diag² (V1 littéral,
  χ²/dof≈1.05/1.10 rapporté). ⇒ 12 fits (2 bras × 3 sous-scén. × 2 modèles).
- B : facteurs P+ recalculés sur l'arm réel N=1590 (figés au run). DES exact
  (N=1829, κ=0.896710, δ²=0.0020654).
- D : Dovekie = extension inter-release ; v1.2 gelé (m12_loo.json), comparé
  jamais substitué.
- E : épinglage commit c9a4fcaf, SHA256 au premier download.
- G : mapping v1.2 conservé (5=CSP) + LIMITATION (non re-confirmé Dovekie) ;
  doute au setup M17 → STOP.
- H : χ² droit, N=1820 ; GATE de cohérence vs likelihood officielle Dovekie
  AVANT le LOO (setup M17).
- I : ancrage Dovekie [2.4, 3.4] = GATE G17.1 (hors fenêtre = bug → STOP audit).

## Récapitulatif v1.2 en cours (P2.2)

- M15 : extraction multi-agents (3 sources × vérif adversariale +
  recoupement). V4 : Keeley v3 Eq. 1-10 (whitening plein, δ² prose),
  facteurs gelés, métrique ΔNσ, hypothèse « renforcée ? ». V5 : Dovekie
  3.2σ, structure réelle main c9a4fcaf (SNANA 1820 SNe, npz inverse, pas
  de diag, Foundation=150), grille LOO, ancrage. SPEC_V22 + P12-P13 +
  M15 committés au STOP.

## Récapitulatif v1.1.0 (P2.1)

- M10 : extraction multi-agents + vérification indépendante ; P9-P11
  pré-enregistrés, GO de Téo (5 décisions + 2 amendements) consigné.
- M11 (V1) : Keeley-test inédit sur DES-SN5YR — p = 6.0×10⁻⁴
  (« anormalement bas »), étalon Pantheon+ G11.2 vert (1386.405,
  k = 1/10⁴) ; diagnostics 0.904 / δ² +0.00207.
- M12 (V2) : LOO — DES : Foundation −1.335σ (3.84→2.50), CfA+CSP
  −0.230σ, DES-removed −1.32σ (σ_curv retenu P10.4) ; P+ : Foundation
  +0.367σ, DES-in-P+ −0.598σ. Lignes CfA+CSP reprises des C-b gelés
  (hash reproduits).
- M13 (V3) : Tier R 8/8 gates verts (Table 1 Efstathiou au dernier
  chiffre, règle même-survey identifiée, typos SEM ×10 démontrées) ;
  Tier P aveugle S = −0.0358 ± 0.0080 mag (334 objets ; secondaire
  covariance-aware ±0.0334, cross-release non modélisé).
- M14 : RESULTS.md §11 (EN) + miroir RESULTS.fr.md + traçabilité
  étendue (123 tests) ; publication v1.1.0 après GO de push.

## Acquis P2.1 (2026-06-12) — chiffres porteurs

- V1 (M11) : G11.2 VERT (χ² P+ 1386.405, k=1/10⁴) ; DES PRIMAIRE :
  χ² = 1640.08 (N=1829), k=5/10⁴, p=6e-4 → « anormalement bas »
  (z₂ = 3.43σ) ; sans les 75 lignes BEAMS : p=0.0288 ; δ²_DES=+0.00207.
- V2 (M12) : DES — Foundation −1.335σ (3.84→2.50, LE levier), CfA+CSP
  −0.230σ, DES-removed −1.32σ (MAP dégénéré, σ_curv retenu P10.4) ;
  P+ — Foundation +0.367σ (!), DES-in-P+ −0.598σ, misc −0.436σ,
  CfA −0.028σ, CSP −0.006σ. Hash C-b reproduits, fits repris gelés.
- V3 (M13) : Tier R 8/8 gates VERTS (Table 1 exacte) ; Tier P AVEUGLE :
  S = −0.0358 ± 0.0080 mag (334 objets, SEM empirique primaire) ;
  covariance-aware σ=0.0334 (cross-release non modélisé).
- Mémo méthode : règle Efstathiou = paires même-survey ; comptes
  épinglés 335/332/4/3 en pytest ; typos SEM Table 1 (0.0055/0.0070).

## Récapitulatif v1.0.0 (GELÉ)

- M5b : 6/6 gates d'ancrage verts (BAO+CMB exact : Δχ² = −8.023 vs −8.0
  publié) ; pipeline brut et amendement calibré P8 tous deux au dossier.
- M6 : 5 posteriors convergés ; BAO+CMB réplique le margestats officiel.
- M7 : DES 3.84 → 1.46σ sans z < 0.1 ; CfA+CSP seul −0.23σ ; Pantheon+
  2.28 → 2.01σ. Lecture pré-enregistrée inchangée.
- M8 : RESULTS.md final (§0 résumé, §9 limites, §10 périmètre négatif) +
  test de traçabilité permanent (8 tests, chiffres ↔ results/*.json).
- M9 : RESULTS.md + README traduits en anglais (VF = RESULTS.fr.md),
  réserve §2.2 levée aux sources (zHD > 0.01 → 1590 ; 1580 = mode SH0ES
  sans les 10 calibrateurs, compte de Keeley 2024, absent de Brout 2022),
  repo public, CI verte, tag v1.0.0, release factuelle.

## Rappels pour une éventuelle reprise (v2)

- Candidat v2 : θ*/r_d par CAMB (recombinaison complète) — rendrait P8
  caduc (RESULTS.md §9.5). Autres pistes notées : Dovekie comme nouveau
  jeu d'ancrages (§9.6), covariance Pantheon+ / Keeley (§9.4).
- Maintenance CI Node 24 : TRAITÉE (jalon courant, branche chore/ci-node24) —
  checkout @v4→@v6, setup-uv @v5→@v8.2.0 ; la bascule Node 24 forcée du
  2026-06-16 est ainsi anticipée. Vérification CI 4/4 + zéro annotation Node 20
  en Phase C après GO de push.
- uv s'invoque via `python -m uv` sur cette machine (uv.exe hors PATH).
- Compte gh : basculé sur Flasher1717 pendant M9 (l'autre compte du
  trousseau est Kodiaquebec).
- Runs reproductibles : run_m5_fits.py (~25 min), run_m6_mcmc.py (~3 h),
  run_m7_cuts.py (~1 h), calibrate_p8.py (~5 min), run_m3_gates.py (~12 min).
