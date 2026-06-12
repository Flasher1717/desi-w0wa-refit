# PROGRESS

> État courant pour la continuité multi-sessions. Mis à jour à chaque fin de
> session (et aux points clés en cours de session).

## Jalon en cours

**STOP fin M13 atteint le 2026-06-12 — rapport des 3 volets présenté,
EN ATTENTE DU GO de Téo pour M14** (RESULTS.md §11 EN + v1.1.0, push
après GO explicite séparé). M10 (GO reçu, P9-P11 gelés), M11, M12, M13
TERMINÉS — voir MILESTONES.md du 2026-06-12. JAMAIS pushé depuis
v1.0.0 (commits locaux : 16ce76f, 40d03a5, a1d1f43, a53e968 + résultats).

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
