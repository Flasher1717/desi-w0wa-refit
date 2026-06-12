# PROGRESS

> État courant pour la continuité multi-sessions. Mis à jour à chaque fin de
> session (et aux points clés en cours de session).

## Jalon en cours

STOP fin M7 atteint — EN ATTENTE DU GO DE TÉO pour M8 (RESULTS.md final :
méthodo, tableaux, limites, « ce que ça ne montre pas »). M3→M7 exécutés
le 2026-06-11 (GO M3→M5 d'une traite, puis GO P8/M6/M7 après l'audit
G5.2).

## Fait (2026-06-11, sessions M3-M7)

- M3 : likelihoods SNe + gates G3.1-G3.4 tous PASS.
- M4 : modèles (CPL < 1e-12, oracles astropy < 1e-6) + prior CMB compressé.
- M5 (brut) : 5/6 gates, G5.2 ÉCHOUÉ → audit ultracode 5 sondes : cause
  = biais θ* analytique HS96 (~−5σ prior), limitation pré-enregistrée
  P2, aucun bug (minimiseur parfait, constantes exactes, BAO innocenté).
- P8 (GO Téo, option b) : correction calibrée κ_r = 1.000279376,
  κ_θ = 1.001314308 (chaînes officielles épinglées, scatter résiduel
  7.6e-6), committée avant re-run.
- M5b : 6/6 gates verts. G5.2b : Δχ² = −8.023 vs −8.0 publié (2.363σ).
  Effet compression : −0.52/−0.51/−0.36σ vs −0.7σ DESI.
- M6 : 5 posteriors MCMC convergés (50τ) ; BAO+CMB réplique le
  margestats officiel à la 2e décimale ; corner plots + chaînes commitées.
- M7 : profil low-z — DES s'effondre sans z < 0.1 (3.84 → 1.46σ),
  Pantheon+ robuste (2.28 → 2.01σ) ; CfA+CSP seul : −0.23σ.
- RESULTS.md §3-§8 ; MILESTONES à jour ; results/*.json + audit + figures
  committés. JAMAIS pushé (pas de GO push).

## Rappels critiques pour la suite

- M8 : limites à documenter — CMB compressé (effet mesuré), P8 (statut
  amendement calibré assumé, transparence totale), Union3 format
  posterior-spline (Kim 2412.14181), covariance P+ (Keeley 2024),
  z* HS96 (raffinement futur : CAMB, hors périmètre v1), Dovekie 3.2σ
  (contexte, jamais ancrage). AUCUNE conclusion « l'énergie noire
  évolue/n'évolue pas » — reproductibilité + profil de sensibilité
  uniquement.
- M9 (publication) : UNIQUEMENT après GO de push explicite ; tag v1.0.0,
  CI verte, release factuelle zéro adjectif.
- uv s'invoque via `python -m uv` sur cette machine (uv.exe hors PATH).
- Runs reproductibles : run_m5_fits.py (~25 min), run_m6_mcmc.py (~3 h),
  run_m7_cuts.py (~1 h), calibrate_p8.py (~5 min), run_m3_gates.py (~12 min).

## Prochain pas concret (après le GO M8)

1. Rituel d'ouverture (SPEC + PROGRESS + git log -10 + pytest).
2. M8 : rédaction RESULTS.md final (méthodo complète, tableaux, limites,
   out-of-scope), revue de cohérence interne, puis STOP avant M9.
