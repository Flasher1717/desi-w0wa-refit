# desi-w0wa-refit

Reproduction indépendante pré-enregistrée de la préférence pour une énergie
noire évolutive (w0waCDM, CPL) dans DESI DR2 BAO + CMB compressé + supernovae
(Pantheon+, DES-SN5YR, Union3), suivie d'un profil de sensibilité
pré-enregistré aux coupures low-z des SNe — le cœur des critiques publiées
(Efstathiou arXiv:2408.07175 ; arXiv:2502.04212 ; réponse DES
arXiv:2511.07517).

Projet de science ouverte personnel. Les résultats sont publiés tels quels,
dans les deux sens. Aucune conclusion physique au-delà de : « la préférence
publiée se reproduit (ou non) et voici son profil de sensibilité ».

- **SPEC.md** — cahier des charges immuable du projet.
- **RESULTS.md** — conventions extraites des papiers, méthodologie, résultats,
  limites.
- **MILESTONES.md** — journal append-only des jalons et décisions.

Suite de [janus-pantheon-refit](https://github.com/Flasher1717/janus-pantheon-refit)
(mêmes règles : pré-enregistrement, gates chiffrés, données épinglées SHA256,
zéro tuning post-hoc).

## Utilisation

```bash
uv sync
uv run python scripts/download_data.py   # seule étape réseau (SHA256 épinglés)
uv run pytest -q
```

Licence MIT.
