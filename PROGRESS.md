# PROGRESS

> État courant pour la continuité multi-sessions. Mis à jour à chaque fin de
> session (et aux points clés en cours de session).

## Jalon en cours

M9 (publication) EN COURS sur GO conditionnel de Téo (2026-06-11) —
conditions levées (traduction EN + réserve §2.2). Étapes restantes au
moment de cette écriture : push initial → CI verte matrice complète →
tag v1.0.0 → release factuelle. Voir MILESTONES.md (entrée GO M9).

## Fait (2026-06-11, sessions M3-M9)

- M3-M5 : likelihoods + gates ; G5.2 échoué/audité → P8 calibré →
  M5b 6/6 gates verts (Δχ² = −8.023 vs −8.0 publié).
- M6 : 5 posteriors MCMC convergés ; M7 : profil low-z (DES 3.84 → 1.46σ
  sans z < 0.1 ; CfA+CSP seul −0.23σ ; Pantheon+ robuste 2.28 → 2.01σ).
- M8 : RESULTS.md final (§0 résumé, §9 limites, §10 périmètre négatif),
  test de traçabilité permanent (8 tests), 4 écarts d'arrondi corrigés.
- M9 conditions : RESULTS.md + README traduits en anglais (VF =
  RESULTS.fr.md, chiffres verrouillés, 8/8 traçabilité re-vérifiés) ;
  réserve §2.2 levée aux sources (cobaya + cosmosis release : zHD > 0.01
  → 1590 ; 1580 = mode SH0ES sans les 10 calibrateurs ; « 1580 » absent
  de Brout 2022, c'est le compte de Keeley 2024).
- gh basculé sur Flasher1717 (jamais Kodia) ; identité git locale
  Téo Alletz vérifiée ; branche renommée main (CI déclenchée sur main).

## Rappels critiques pour la suite

- Publication : CI verte matrice complète (ubuntu/windows × 3.11/3.13)
  AVANT le tag v1.0.0 ; release factuelle zéro adjectif (5 ancrages,
  profil M7 3.84→1.46 / −0.23, effet compression mesuré, lien RESULTS.md
  au tag).
- uv s'invoque via `python -m uv` sur cette machine (uv.exe hors PATH).
- Runs reproductibles : run_m5_fits.py (~25 min), run_m6_mcmc.py (~3 h),
  run_m7_cuts.py (~1 h), calibrate_p8.py (~5 min), run_m3_gates.py (~12 min).

## Prochain pas concret

1. Si la publication s'est terminée dans la session M9 : v1.0.0 publiée,
   projet en veille (v2 candidate : θ*/r_d par CAMB, rendrait P8 caduc).
2. Sinon : reprendre à l'étape restante (push / CI / tag / release) —
   l'ordre est impératif.
