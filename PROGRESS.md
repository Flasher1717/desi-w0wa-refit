# PROGRESS

> État courant pour la continuité multi-sessions. Mis à jour à chaque fin de
> session (et aux points clés en cours de session).

## Jalon en cours

M1 — extraction terminée, RESULTS.md §1-2 rédigé. Vérification adversariale
des équations critiques DESI DR2 (Eq. 22, Eqs. 35-36, priors, Tables 5-6)
en cours. Ensuite : STOP M1 (plan + choix CMB + traitement r_d + tolérances
de gates) → GO de Téo.

## Fait

- 2026-06-11 : M0 complet et committé (5 commits) : SPEC (prompt ajusté),
  CLAUDE, MILESTONES, PROGRESS, pyproject uv, ruff/pyright strict/pytest
  verts, CI matrice, MIT, .gitattributes. Identité git locale vérifiée.
- 2026-06-11 : M1 extractions — 7 sous-agents rentrés (DESI DR2 2503.14738,
  bao_data, DES-SN5YR, Union3, compression CMB, low-z/Pantheon+,
  réponse DES 2511.07517 + Keeley). Recoupement croisé BAO Table 4 vs
  fichiers bao_data : concordance chiffre à chiffre.
- 2026-06-11 : RESULTS.md §1-2 rédigé avec références précises.

## Découvertes critiques (à ne pas perdre)

- DES-SN5YR : épingler le tag v1.2 (`95cf14c…`), PAS main (passé à Dovekie).
- bao_data : tag v2.6 (`b7b8a36…`) ; ordre Lyα inversé (DH avant DM).
- DES covariance totale = STAT+SYS + diag(MUERR_FINAL²) (STATONLY ~ 0).
- DESI publie l'ancrage exact du pipeline compressé : DESI+(θ*,ωb,ωbc)_CMB
  = 2.4σ [Table 6] vs 3.1σ full CMB → à intégrer dans les gates M5.
- Pantheon+ : coupure cosmologie zHD > 0.01 (1590 SNe).

## En attente

- Vérification adversariale Eqs. (22)/(35)/(36) → puis STOP M1, GO de Téo.

## Prochain pas concret

Après GO M1 : M2 — scripts/download_data.py (bao_data v2.6, SHA256,
atomique, idempotent) + likelihood BAO gaussienne + tests covariance.
