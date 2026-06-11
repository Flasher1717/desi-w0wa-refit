# PROGRESS

> État courant pour la continuité multi-sessions. Mis à jour à chaque fin de
> session (et aux points clés en cours de session).

## Jalon en cours

M3 — likelihoods SNe (Pantheon+ d'abord, puis DES-SN5YR, Union3
best-effort). PAS ENCORE COMMENCÉ. Session précédente close à la fin de M2.

## Fait

- 2026-06-11 : M0 complet (bootstrap, outillage, CI). M1 complet :
  7 extractions sourcées + recoupement croisé + vérification adversariale
  6/6 → RESULTS.md §1-2. STOP M1 présenté, GO M1 GLOBAL reçu avec
  conditions (voir MILESTONES) — toutes levées et committées
  (PREREGISTRATION.md : compression CMB Option A avec valeurs complètes
  trouvées dans les yaml officiels DESI, formules Aubourg Eq. 16 / HS96
  E-1 / EH98 Eq. 4, gates deux niveaux, coupures M7 closes).
- 2026-06-11 : M2 complet (download SHA256 atomique idempotent + likelihood
  BAO gaussienne validée + 20 tests verts). Détails : MILESTONES.md.

## Rappels critiques pour la suite

- M3 : Pantheon+ zHD > 0.01 (1590 SNe) ; cov 1ʳᵉ ligne = N=1701.
  DES : épingler tag v1.2 (`95cf14c…`), JAMAIS main (Dovekie) ; cov totale
  = STAT+SYS + diag(MUERR_FINAL²) ; chaînes `fw0wacdm_SN.txt` pondérées
  (colonne weight) = ancrage G3.3. Union3 : fichiers cobaya sn_data.
- Gates pré-enregistrés : PREREGISTRATION.md P3 (M3), P4 (M5), P5 (M7).
- Prochain STOP utilisateur : fin M5 (rapport chiffré des gates).
- Politique d'effort : M2-M4 high ; ultracode ponctuel si audit de gate.

## Prochain pas concret (ouverture de session M3)

1. Rituel d'ouverture (SPEC + PROGRESS + git log -10 + pytest).
2. Étendre data_manifest.json : Pantheon+ (dat + cov, commit DataRelease
   épinglé), DES v1.2 (HD.csv + STAT+SYS.txt.gz + chaînes fw0wacdm/flcdm),
   Union3 (lcparam_full.txt + mag_covmat.txt, commit sn_data épinglé) —
   SHA256 au premier download.
3. MarginalizedChi2 (machinerie P0 re-testée ici) puis likelihood Pantheon+.
