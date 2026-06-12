# desi-w0wa-refit

Pre-registered independent reproduction of the preference for evolving
dark energy (w0waCDM, CPL) in DESI DR2 BAO + compressed CMB + supernovae
(Pantheon+, DES-SN5YR, Union3), followed by a pre-registered sensitivity
profile against the SNe low-z cuts — the core of the published critiques
(Efstathiou arXiv:2408.07175; arXiv:2502.04212; DES response
arXiv:2511.07517).

A personal open-science project. Results are published as they come, in
both directions. No physics conclusion beyond: "the published preference
reproduces (or not), and here is its sensitivity profile".

- **RESULTS.md** — conventions extracted from the papers, methodology,
  results, limitations (original French version: RESULTS.fr.md).
- **SPEC.md** — the project's immutable specification (in French).
- **MILESTONES.md** — append-only log of milestones and decisions (in
  French).

Follow-up to [janus-pantheon-refit](https://github.com/Flasher1717/janus-pantheon-refit)
(same rules: pre-registration, numeric gates, SHA256-pinned data, zero
post-hoc tuning).

## Usage

```bash
uv sync
uv run python scripts/download_data.py   # the only network step (pinned SHA256)
uv run pytest -q
```

MIT license.
