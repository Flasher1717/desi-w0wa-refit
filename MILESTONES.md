# MILESTONES — append-only

Journal des jalons et décisions. Une fois committée, une entrée ne s'édite
jamais ; toute correction est une nouvelle entrée datée.

---

## 2026-06-11 — M0 : bootstrap

- Création du repo `desi-w0wa-refit` (nom par défaut du SPEC) dans
  `C:\Users\flash\dev\desi-w0wa-refit`. Note : le dossier courant de la
  session était `C:\windows\system32` (non utilisable comme dossier de
  travail) ; emplacement choisi et signalé au STOP M1.
- Le prompt fondateur a été ajusté par Téo en cours de M0 (avant le premier
  commit) ; SPEC.md = copie intégrale de la version ajustée. Ajouts notables :
  réponse DES arXiv:2511.07517, politique d'effort, identité git, Keeley 2024
  (covariance Pantheon+) en limitation M8, download atomique/idempotent.
- SPEC.md (immuable), CLAUDE.md (<200 lignes), MILESTONES.md, PROGRESS.md.
- git init ; identité locale `Téo Alletz <teo.alletz@gmail.com>` configurée
  avant le premier commit.
- pyproject (uv, src layout, package `desi_w0wa_refit`), ruff, pyright
  strict, pytest (marker `requires_data`), CI GitHub Actions matrice
  ubuntu/windows. Licence MIT (défaut du SPEC).
- M1 lancé en parallèle (ultracode, conformément au SPEC) : 7 extractions
  sourcées — DESI DR2 (2503.14738), bao_data, DES-SN5YR, Union3,
  compression CMB, coupures low-z (2408.07175, 2502.04212) + ancrage
  Pantheon+ (2202.04077), réponse DES (2511.07517) + Keeley 2024.
  Recoupement croisé prévu avant le STOP M1.
