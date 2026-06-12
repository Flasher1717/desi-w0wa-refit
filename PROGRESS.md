# PROGRESS

> État courant pour la continuité multi-sessions. Mis à jour à chaque fin de
> session (et aux points clés en cours de session).

## Jalon en cours

**M10 — STOP atteint le 2026-06-12, EN ATTENTE DU GO de Téo.**
Extension P2.1 ouverte (SPEC_V21.md committé, immuable ; jalons M10-M14).
Extraction multi-agents + vérification faites ; PREREGISTRATION.md étendu
(P9 V1-mocks, P10 V2-LOO, P11 V3-appariement) ; entrée MILESTONES.md M10.
AUCUN run M11-M13 effectué. Prochain pas : GO M10 de Téo (questions
ouvertes : gate G11.2 Keeley-P+ optionnel ~25-40 min de calcul ;
fiducial primaire V1 = Keeley fixe Ωm 0.3 ; grille DES 3+2 ;
règle doublons Tier P ; acceptation du statut non aveugle du gate
Efstathiou Tier R) → puis M11 (V1), M12 (V2 ~1.5-2 h), M13 (V3, STOP
rapport), M14 (§11 + v1.1.0 après GO push).

## Acquis M10 (2026-06-12)

- Règle d'appariement Efstathiou rétro-ingéniérée et vérifiée 2× :
  paires même-survey → Table 1 reproduite au dernier chiffre
  (332 paires, 145/118/14/27/18/3/7, all-low-z −0.0482, diff −0.0360) ;
  typos ×10 démontrées sur 2 erreurs imprimées (vraies : 0.0055/0.0070).
- Tier P : 335 objets communs ; exclusion pré-enregistrée 1304442
  (zHD révisé) ; 4 absences réelles low-z ; 3 cross-survey CfA3K/CSP.
- DES-SN5YR : pas d'IDSURVEY 61/62/18/50/51/56/57 ; CfA=63-66 (68),
  CSP=5 (8), Foundation=150 (118), DES=10 (1635).
- Keeley Sec. 2 extrait (fiducial fixe Ωm 0.3/H0 70, 10 000 mocks,
  χ²_min refit (H0,Ωm,MB), 0/10⁴ → >3.9σ two-sided non énoncé) ;
  P0 (C:\JJP-JANUS) : χ² réel répliqué 1387.099, AUCUN test mock.

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
