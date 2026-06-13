# PROGRESS

> État courant pour la continuité multi-sessions. Mis à jour à chaque fin de
> session (et aux points clés en cours de session).

## Jalon en cours

M15 (extension P2.2, SPEC_V22.md) — TERMINÉ, STOP, EN ATTENTE DU GO de Téo.
Extraction + pré-enregistrement P12-P13 committés AVANT tout run. AUCUN run
M16-M17 effectué. Prochain pas : GO de Téo sur les décisions A/B/D/E/G/H/I
(voir MILESTONES 2026-06-13 et PREREGISTRATION P12-P13), puis M16 (V4).

## Décisions ouvertes au STOP M15 (GO requis)

- A (porteuse) : normalisation V4 scénario (i). Keeley = whitening PLEIN
  (Eq. 9), pas la diagonale de V1. Proposition : C·κ avec κ=χ²_min/N
  (fidèle Keeley + contrôle χ²/dof→1 exact) ; s_diag de V1 en contexte.
- B : facteurs P+ recalculés sur l'arm réel N=1590 (fig. au run) vs valeurs
  V1 N=1580 littérales. DES exact (N=1829, κ=0.896710, δ²=0.0020654).
- D : statut Dovekie = EXTENSION inter-release (Dovekie remplace v1.2 sur
  main ; v1.2 reste gelé au tag v1.2/95cf14c).
- E : épinglage Dovekie au commit c9a4fcaf ; SHA256 au premier download.
- G : code IDSURVEY 5 (8 SNe, CSP non documenté dans le README Dovekie) —
  mapping v1.2 conservé (5=CSP) proposé.
- H : BEAMS — χ² droit sans poids par-SN, N=1820 ; à vérifier contre la
  likelihood officielle Dovekie au setup M17.
- I : fenêtre d'ancrage 3.2σ Dovekie. Proposition [2.4, 3.4] (offset CMB
  compressé −0.36σ comme v1.2).

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
- Maintenance CI signalée par GitHub : actions checkout@v4 / setup-uv@v5
  sur Node 20 déprécié (bascule Node 24 forcée à partir du 2026-06-16).
- uv s'invoque via `python -m uv` sur cette machine (uv.exe hors PATH).
- Compte gh : basculé sur Flasher1717 pendant M9 (l'autre compte du
  trousseau est Kodiaquebec).
- Runs reproductibles : run_m5_fits.py (~25 min), run_m6_mcmc.py (~3 h),
  run_m7_cuts.py (~1 h), calibrate_p8.py (~5 min), run_m3_gates.py (~12 min).
