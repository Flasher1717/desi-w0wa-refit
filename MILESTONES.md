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

## 2026-06-11 — M1 : extraction des conventions (terminée, en attente du GO)

- 7 extractions rentrées ; RESULTS.md §1-2 rédigé avec n° de
  section/équation/table pour chaque fait.
- Recoupement croisé : Table 4 (DESI DR2) vs fichiers bao_data — concordance
  chiffre à chiffre sur les 13 points et covariances (deux agents, deux
  sources indépendantes).
- Contre-vérification adversariale (agent indépendant, LaTeX brut) des
  Eqs. (22), (35), (36), priors, Tables 5-6 : 6/6 confirmés. Trouvaille :
  θ* imprimé à 5 décimales dans le papier (troncature source) vs
  σ(θ*) ≈ 2.6×10⁻⁶ — à traiter au GO M1.
- Découvertes critiques : DES-SN5YR à épingler au tag v1.2 (main = Dovekie
  2026, 1820 SNe ≠ papier 2024) ; bao_data tag v2.6, ordre Lyα inversé
  (DH avant DM) ; covariance DES totale = STAT+SYS + diag(MUERR_FINAL²) ;
  ancrage exact publié du pipeline compressé DESI+(θ*,ωb,ωbc)_CMB = 2.4σ
  [Table 6].
- Union3 : décision best-effort → INCLUS (fichiers cobaya sn_data, usage
  identique à DESI ; limite Kim arXiv:2412.14181 documentée en M8).
- STOP M1 présenté à Téo : plan M2-M9, choix CMB (Option A = compression
  DESI Eqs. 35-36 recommandée), traitement r_d, tolérances de gates,
  coupures M7 candidates. En attente du GO.

## 2026-06-11 — GO M1 GLOBAL de Téo (4 décisions validées, avec conditions)

1. CMB : Option A (compression DESI, Eqs. 35-36, Lemos & Lewis 2023).
   Conditions : (a) formules de fitting r_s(z_drag)/z*/r_s(z*) extraites des
   papiers (n° d'équations), pré-enregistrées et committées en DÉBUT de M2,
   avant tout code CMB ; (b) oracle permanent : la formule reproduit le r_d
   fiducial du papier DESI (valeur extraite, jamais de mémoire) à la
   précision documentée de la formule ; (c) θ* tronqué : effort borné
   (≤ 1 session) pour trouver la valeur complète dans les produits publics
   DESI (desilike, chaînes, notebooks App. A) ; sinon 0.01041 + test de
   sensibilité pré-enregistré (θ* ± 5e-6, effet rapporté en Nσ par bras).
2. Gates deux niveaux : validés tels quels. Précisions : (a) sur les bras
   +SNe, l'écart mesuré vs publié est RAPPORTÉ comme mesure de l'effet de
   compression (référence : −0.7σ mesuré par DESI sur BAO+CMB) ; (b) gate
   échoué pour cause plausible de minimiseur (scipy vs iminuit) : audit
   documenté, jamais de relâchement silencieux ; l'ordre P+ < Union3 < DESY5
   est un gate à part entière.
3. Coupures M7 (a)-(d) : validées et CLOSES — aucune coupure ajoutée après
   les premiers chiffres. Métrique de rapport pré-enregistrée avant tout
   run M7 : ΔNσ par coupure + déplacement du best-fit (w0, wa), format de
   tableau figé.
4. Repo : C:\Users\flash\dev\desi-w0wa-refit conservé. Ancrages = ère DR2
   exclusivement (DES v1.2/Zenodo, Tables 5-6) ; Dovekie (3.2σ) = contexte
   M8 uniquement, jamais un ancrage.

Périmètre inchangé : M2 ne démarre qu'avec les formules r_s committées.
Prochain STOP : fin M5 (gates d'ancrage), rapport chiffré complet avant M6.

## 2026-06-11 — Conditions du GO M1 levées, pré-enregistrement committé

- (1a) Formules extraites des papiers, constantes verbatim : Aubourg 2015
  Eq. (16) (r_d, précision 0.021 %), HS96 Eq. (E-1) (z*), EH98 Eq. (4)
  (z_d, information), r_s intégral [EH98 Eqs. (5)-(6)] ; cross-check :
  formule du papier DESI lui-même [2503.14738v3, Eq. (2)].
- (1b) Oracle r_d : point d'ancrage publié Eq. (2) = 147.05 Mpc au point
  Planck (le papier ne publie pas de r_d fiduciel isolé) ; tolérance 0.3 %.
- (1c) θ* complet TROUVÉ dans les produits officiels (yaml des chaînes
  DESI DR2, data.desi.lbl.gov, contre-vérifié sur 2 fichiers) :
  (0.01041027, 0.02223208, 0.14207901) + covariance complète. Test de
  sensibilité P6 caduc (clause conditionnelle non déclenchée).
- Conventions neutrinos baseline extraites (Σmν = 0.06 eV un état massif,
  Neff = 3.044, Ωm inclut ν non relativistes, ωbc les exclut).
- Limitation pré-enregistrée : précision percent-level de z* HS96 vs
  σ(θ*)/θ* ≈ 2.5e-4 — bornée par le gate G5.2, jamais recalibrée en
  silence.
- PREREGISTRATION.md committé → M2 ouvert.
