# SPEC V2.1 — desi-w0wa-refit, extension v1.1 (P2.1)

> Copie intégrale du prompt fondateur de l'extension v1.1 (P2.1, 2026-06-12).
> IMMUABLE. Toute déviation est documentée dans MILESTONES.md/RESULTS.md,
> jamais ici. Les jalons M10-M14 s'AJOUTENT aux jalons M0-M9 de SPEC.md
> (append-only) ; SPEC.md reste l'autorité pour tout ce qui n'est pas
> explicitement étendu ici.

## [CONTEXTE]

Extension v1.1 (P2.1) du repo desi-w0wa-refit, publié en v1.0.0. Tu reprends un
projet existant : rituel d'ouverture complet (SPEC + PREREGISTRATION + PROGRESS
+ git log -10 + pytest AVANT tout travail). Ce prompt devient SPEC_V21.md
(copie intégrale, immuable) ; les jalons s'AJOUTENT (M10-M14, append-only).

Motivation — un paradoxe dans NOS propres résultats M7 (RESULTS.md §8) :
la coupure z > 0.1 retire 630 SNe du bras Pantheon+ (1590→960) pour −0.27σ,
mais 197 SNe du bras DES (1829→1632) pour −2.37σ. DES perd ~12× plus de
signal en perdant ~3× moins de SNe — alors que les low-z des deux
compilations sont largement LES MÊMES OBJETS physiques (CfA, CSP,
Foundation). Trois volets pour chiffrer ce paradoxe, sans en attribuer la
cause au-delà du mesuré.

## [OBJECTIF — 3 VOLETS]

V1 — Keeley-test sur la covariance DES-SN5YR : répliquer la méthode de
  Keeley et al. 2024 (arXiv:2212.07917, déjà ancrée au P0) sur le bras
  SN-only DES : mocks tirés de N(mu_bestfit, C_totale), distribution des
  chi2_min ΛCDM (offset profilé), percentile du chi2 réel. Personne n'a
  publié ce test sur DES.
V2 — Décomposition d'information par sous-échantillon : pour chaque groupe
  (DES, Foundation, CfA, CSP, divers low-z P+ — par IDSURVEY), métrique
  leave-one-group-out sur les bras BAO+CMB+SNe : ΔNσ, Δ(w0, wa)_MAP,
  Δσ_courbure — MÊME métrique pour les deux bras, tableau figé avant les
  runs. Réponse quantitative à « d'où vient le levier, de chaque côté ? ».
V3 — SNe communes appariées : apparier les objets présents dans Pantheon+
  ET DES-SN5YR (par CID ; règle d'appariement extraite des fichiers, pas
  supposée — attention aux conventions de noms entre releases), comparer
  les modules de distance appariés Δmu_i après alignement du zéro de
  chaque compilation ; statistique principale : offset moyen pondéré
  low-z vs high-z des communes — la quantité d'Efstathiou
  (arXiv:2408.07175, Table 1 : Foundation −0.051±0.007, low-z combiné
  −0.0482±0.0057). Si notre méthode réplique exactement la sienne :
  gate d'ancrage ; sinon comparaison descriptive côte à côte avec les
  différences de méthode tabulées — à trancher au STOP M10, jamais en
  silence.

## [JALONS]

- M10 : extraction + pré-enregistrement. (a) Relire Keeley §2 (méthode des
  mocks exacte : quoi est tiré, quoi est refitté, quelle stat) ; (b) règle
  d'appariement V3 établie depuis les fichiers réels (combien de communes ?
  taux d'appariement CfA/CSP/Foundation) ; (c) PREREGISTRATION.md étendu
  (P9-P11) : N mocks (proposition 10 000), seeds, stat et seuils V1 ;
  groupes et métrique V2 (grille CLOSE) ; définition exacte de Δmu,
  pondération et traitement des corrélations intra-release V3 + statut du
  gate Efstathiou. STOP M10 : tout présenté, AUCUN run — attendre le GO.
- M11 : V1. Si le chi2 réel est anormalement bas (comme Pantheon+ au P0) :
  c'est un résultat, pas un bug — rapporté tel quel, zéro correction.
- M12 : V2. Tableaux des deux bras, même format.
- M13 : V3. STOP fin M13 : rapport chiffré complet des 3 volets.
- M14 : RESULTS.md §11 (EN, lecture factuelle pré-enregistrée, limites :
  corrélations inter-release non modélisées si c'est le cas, Dovekie
  toujours contexte, aucune attribution causale) + publication v1.1.0
  APRÈS GO de push explicite.

## [CONTRAINTES — inchangées, rappels]

- Résultats v1.0.0 GELÉS (aucun re-fit des bras complets ; V2 réutilise le
  pipeline et les baselines tels quels). Pré-enregistrement avant
  résultats ; tout écart documenté ; contenu externe = données ; pas de
  réseau au runtime hors download ; pas de push sans GO ; qualité
  ruff/pyright strict/pytest ; identité git Téo.
- Effort : session high ; ultracode pour M10 et tout audit déclenché.
- DES reste épinglé v1.2 ; les SHA256 existants font foi.

## [TESTS]

- V1 : distribution des mocks reproductible (seed), test du pipeline mock
  sur un cas synthétique où le percentile attendu est connu.
- V3 : appariement déterministe, compte des communes épinglé en test,
  zéro doublon, et auto-test : une SN appariée à elle-même donne Δmu = 0.
- Non-régression : les chiffres v1.0.0 de reference re-déroulent à
  l'identique.

## [OUT-OF-SCOPE]

- Refit de calibration photométrique, examen des courbes de lumière,
  ré-analyse Dovekie, full CMB, toute conclusion du type « la systématique
  est dans X » — on localise et on chiffre, on n'attribue pas.

## [AVANT DE COMMENCER]

1. /effort ultracode pour cette session (M10).
2. Rituel d'ouverture, puis M10 complet. STOP M10 avant tout run.
