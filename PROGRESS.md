# PROGRESS

> État courant pour la continuité multi-sessions. Mis à jour à chaque fin de
> session (et aux points clés en cours de session).

## Jalon en cours

STOP fin M5 atteint — EN ATTENTE DU GO DE TÉO. M3, M4, M5 exécutés
d'une traite (GO du 2026-06-11). Gates M3 : 4/4 PASS. Gates M5 : 5/6
PASS, G5.2 ÉCHOUÉ avec cause auditée et attribuée (biais θ* HS96,
limitation pré-enregistrée P2) — voir RESULTS.md §4-§5 et MILESTONES.

## Fait

- 2026-06-11 : M0-M2 (voir MILESTONES). M3 complet : données SNe
  épinglées (P+ c447f0f, DES v1.2 95cf14c, Union3 61d9643), sne.py,
  gates G3.1-G3.4 tous PASS (Ωm P+ 0.3316/0.334 ; DES 0.3520/0.352 ;
  G3.3 pulls ≤ 0.11σ_chaîne ; Union3 22 nœuds). M4 complet :
  cosmology.py (CPL fermé vs intégral < 1e-12, oracles astropy < 1e-6),
  cmb.py (r_d Aubourg 146.855 vs 147.05 = 0.13 % ; prior P1 = yaml
  officiel exact). M5 complet : moteur committé avant runs, 10 fits,
  résultats results/m5_fits.json.
- 2026-06-11 : AUDIT G5.2 (ultracode, 5 sondes, results/audit/) :
  aucun bug ; minimiseur parfait ; cause = θ* analytique bas de ~0.1 %
  (−5σ prior) vs θ* CAMB officiel ; diagnostic : prior décalé du biais
  → 2.27σ (fenêtre [2.1, 2.7]). Chaînes officielles DESI épinglées au
  manifest (audit pointwise par colonnes chi2__*).

## Décision attendue de Téo (STOP M5)

Sort de G5.2 avant M6 :
(a) accepter en limitation documentée (pipeline gelé, G5.2 rapporté
    échoué-avec-attribution) ;
(b) pré-enregistrer un amendement θ* (correction calibrée transparente
    OU θ* via CAMB — attention : CLASS/CAMB listés out-of-scope au SPEC) ;
(c) autre instruction.

## Rappels critiques pour la suite

- JAMAIS de push sans GO explicite. M6 (MCMC) : nwalkers/longueurs à
  committer AVANT les runs (P7) ; convergence ≥ 50·τ ; seeds dérivés de
  20260611. M7 : coupures CLOSES (P5), métrique de tableau figée.
- Les fits M5 sont déterministes et re-exécutables :
  `uv run python scripts/run_m5_fits.py` (~25 min) ;
  gates M3 : `uv run python scripts/run_m3_gates.py` (~12 min, emcee).
- uv s'invoque via `python -m uv` sur cette machine (uv.exe pas dans PATH).
- Suite : 100+ tests verts, ruff/pyright stricts zéro erreur, CI verte
  attendue (matrice sans data/ → ancrages auto-skip).

## Prochain pas concret (après le GO)

1. Rituel d'ouverture (SPEC + PROGRESS + git log -10 + pytest).
2. Selon décision G5.2 : amendement pré-enregistré committé avant tout
   nouveau run, OU passage direct à M6 (MCMC + corner plots).
