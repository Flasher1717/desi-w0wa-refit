# PROGRESS

> État courant pour la continuité multi-sessions. Mis à jour à chaque fin de
> session (et aux points clés en cours de session).

## Jalon en cours

STOP fin M8 atteint — EN ATTENTE de la relecture de RESULTS.md complet
par Téo, puis de son GO M9 explicite (publication : tag v1.0.0, CI verte,
release factuelle zéro adjectif, push). M3→M8 exécutés le 2026-06-11.

## Fait (2026-06-11, sessions M3-M8)

- M3 : likelihoods SNe + gates G3.1-G3.4 tous PASS.
- M4 : modèles (CPL < 1e-12, oracles astropy < 1e-6) + prior CMB compressé.
- M5 (brut) : 5/6 gates, G5.2 ÉCHOUÉ → audit ultracode 5 sondes : cause
  = biais θ* analytique HS96 (~−5σ prior), limitation pré-enregistrée
  P2, aucun bug. P8 (GO Téo, option b) : κ_r = 1.000279376,
  κ_θ = 1.001314308, committés avant re-run → M5b 6/6 gates verts
  (Δχ² = −8.023 vs −8.0 publié).
- M6 : 5 posteriors MCMC convergés (50τ) ; BAO+CMB réplique le
  margestats officiel à la 2e décimale.
- M7 : profil low-z — DES s'effondre sans z < 0.1 (3.84 → 1.46σ),
  Pantheon+ robuste (2.28 → 2.01σ) ; CfA+CSP seul : −0.23σ.
- M8 : RESULTS.md final — §0 résumé exécutif (3 chiffres), §9 limites
  (compression mesurée, statut P8 + incident de racine, Union3/Kim,
  Keeley, z* HS96 → CAMB, Dovekie en contexte), §10 « ce que ça ne
  montre pas ». Test de traçabilité permanent
  (tests/test_results_traceability.py) : chaque chiffre porteur recoupé
  contre results/*.json ; 4 écarts d'arrondi du texte corrigés (détail
  dans MILESTONES.md, entrée M8). 98 tests verts.
- JAMAIS pushé (pas de GO push).

## Rappels critiques pour la suite

- M9 (publication) : UNIQUEMENT après relecture de RESULTS.md par Téo ET
  GO de push explicite ; tag v1.0.0, CI verte, release factuelle zéro
  adjectif (SPEC). README à vérifier avant release.
- uv s'invoque via `python -m uv` sur cette machine (uv.exe hors PATH).
- Runs reproductibles : run_m5_fits.py (~25 min), run_m6_mcmc.py (~3 h),
  run_m7_cuts.py (~1 h), calibrate_p8.py (~5 min), run_m3_gates.py (~12 min).

## Prochain pas concret (après relecture + GO M9)

1. Rituel d'ouverture (SPEC + PROGRESS + git log -10 + pytest).
2. M9 : intégrer les retours de relecture éventuels, README final,
   vérifier CI verte, tag v1.0.0, release factuelle, push (sur GO).
