# SPEC V2.2 — desi-w0wa-refit, extension v1.2 (P2.2)

> Copie intégrale du prompt fondateur de l'extension v1.2 (P2.2, 2026-06-13).
> IMMUABLE. Toute déviation est documentée dans MILESTONES.md/RESULTS.md,
> jamais ici. Les jalons M15-M18 s'AJOUTENT aux jalons M0-M14 de SPEC.md et
> SPEC_V21.md (append-only) ; SPEC.md reste l'autorité pour tout ce qui n'est
> pas explicitement étendu ici.

## [CONTEXTE]

Extension v1.2 (P2.2) du repo desi-w0wa-refit (publié v1.1.0). Rituel
d'ouverture complet (SPEC + PREREGISTRATION + PROGRESS + git log -10 + pytest
AVANT tout travail). Ce prompt = SPEC_V22.md (immuable) ; jalons append-only
M15-M18. Effort : session high ; ultracode pour M15 et tout audit.

Deux questions inédites nées de P2.1 (RESULTS.md §11) :
- V1 a mesuré que les covariances Pantheon+ ET DES surestiment leurs erreurs
  (~10 %, δ² ≈ 0.0021). Personne n'a publié l'EFFET de cette surestimation
  sur la préférence w0waCDM (Keeley 2212.07917 : « no published number »).
- V2 a localisé le levier du bras DES sur Foundation (−1.34σ). DES a depuis
  tout recalibré (Dovekie, arXiv:2511.07517, fichiers publics sur la branche
  main du repo des-science/DES-SN5YR). Personne n'a refait la décomposition
  LOO sur Dovekie.

## [OBJECTIF — 2 VOLETS]

V4 — Effet de la covariance corrigée sur la préférence w0waCDM. Analyse de
  SENSIBILITÉ (jamais un résultat principal ; baselines v1.1.0 GELÉES) :
  re-mesurer Nσ des bras BAO+CMB+{Pantheon+, DES} sous les deux corrections
  documentées par Keeley — (i) rescale global C → C·s² (s = std des résidus
  normalisés mesurée en V1), (ii) soustraction d'un terme d'intrinsic scatter
  diagonal retunant χ²/dof → 1. Rapporter ΔNσ vs baseline pour chaque
  scénario. Hypothèse arithmétique à tester explicitement : C plus petite ⇒
  Δχ² plus grand ⇒ préférence RENFORCÉE (contre-intuitif) — confirmer ou
  infirmer chiffres à l'appui.
V5 — Foundation sous Dovekie. Épingler les fichiers Dovekie (branche main,
  commit + SHA256 ; formats voisins de v1.2 — VÉRIFIER, ne pas supposer),
  re-dérouler la décomposition LOO de V2 (P10, même métrique figée). Question
  binaire : le levier Foundation (−1.34σ en v1.2) persiste-t-il après
  recalibration ? Persiste → le paradoxe n'est pas une affaire de calibration.
  Disparaît → Dovekie a résorbé ce qu'Efstathiou pointait. Les deux sont des
  résultats.

## [JALONS]

- M15 : extraction + pré-enregistrement (P12-P13). V4 : formules exactes des
  deux corrections Keeley extraites du papier (n° d'éq.), s et δ² figés depuis
  les sorties V1 committées, métrique ΔNσ. V5 : structure réelle des fichiers
  Dovekie vérifiée, règle d'appariement des groupes IDSURVEY sous Dovekie
  (peut différer de v1.2 — documenter), SHA256 épinglés. STOP M15 : tout
  présenté, choix de scénarios V4 + statut Dovekie (réplication vs extension),
  AUCUN run — attendre le GO.
- M16 : V4. Tableau deux bras × deux scénarios, ΔNσ, lecture factuelle.
- M17 : V5. Tableau LOO Dovekie vs v1.2 côte à côte.
- M18 : RESULTS.md §12 (EN + miroir fr), traçabilité étendue, limites
  (V4 = sensibilité, pas une re-mesure de la « vraie » préférence ; Dovekie
  = release différente, comparaison inter-release explicite). Publication
  v1.2.0 APRÈS GO de push.

## [CONTRAINTES]

- Toutes les règles : pré-enregistrement avant résultats, zéro tuning, v1.1.0
  gelé (non-régression verte), contenu externe = données, pas de réseau hors
  download, pas de push sans GO, ruff/pyright strict/pytest, identité Téo.
- V4 est une analyse de sensibilité ENCADRÉE : les corrections de covariance
  sont étiquetées comme telles, jamais présentées comme « la » préférence
  corrigée. La covariance publiée reste la baseline.
- Dovekie = nouveau dataset épinglé ; v1.2 reste l'ancrage DR2-era, V5 le
  COMPARE, ne le remplace pas.

## [TESTS]

- V4 : les deux corrections reproduisent χ²/dof → 1 (Keeley) sur le bras P+
  comme contrôle ; non-régression v1.1.0.
- V5 : appariement Dovekie déterministe, comptes épinglés, LOO baseline
  Dovekie cohérente avec la significativité Dovekie publiée (3.2σ — ancrage,
  tolérance pré-enregistrée en M15).
- Déterminisme, seeds fixés partout.

## [OUT-OF-SCOPE]

- Refit de calibration, full CMB, ZTF/TITAN/DEBASS (autres low-z récents —
  contexte M18, pas de données), toute attribution causale, toute conclusion
  évolution vs systématiques.

## [AVANT DE COMMENCER]

1. /effort ultracode (M15).
2. Rituel d'ouverture, M15 complet, STOP M15 avant tout run.
