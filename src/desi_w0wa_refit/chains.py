"""Reader for the official DES-SN5YR CosmoSIS chain files (pinned data).

Format (verified on the pinned v1.2 files): first line = tab-separated
column names prefixed with '#', further '#' lines are metadata (sampler
settings and the embedded values/priors ini), then whitespace-separated
rows. Polychord chains carry a ``weight`` column; all statistics here are
weight-aware.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from desi_w0wa_refit.bao import FloatArray


@dataclass(frozen=True)
class CosmosisChain:
    columns: tuple[str, ...]
    samples: FloatArray  # shape (n_rows, n_columns)

    def column(self, name: str) -> FloatArray:
        return self.samples[:, self.columns.index(name)]

    @property
    def weights(self) -> FloatArray:
        if "weight" in self.columns:
            return self.column("weight")
        return np.ones(int(self.samples.shape[0]), dtype=np.float64)

    def weighted_mean(self, name: str) -> float:
        weights = self.weights
        return float(np.sum(weights * self.column(name)) / np.sum(weights))

    def weighted_std(self, name: str) -> float:
        weights = self.weights
        values = self.column(name)
        mean = np.sum(weights * values) / np.sum(weights)
        variance = np.sum(weights * (values - mean) ** 2) / np.sum(weights)
        return float(np.sqrt(variance))


def read_cosmosis_chain(path: Path) -> CosmosisChain:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith("#"):
        raise ValueError(f"{path}: missing CosmoSIS header line")
    columns = tuple(
        name.strip().removeprefix("cosmological_parameters--")
        for name in lines[0].removeprefix("#").split("\t")
    )
    rows = [line.split() for line in lines if line.strip() and not line.startswith("#")]
    samples = np.asarray(rows, dtype=np.float64)
    if samples.ndim != 2 or samples.shape[1] != len(columns):
        raise ValueError(
            f"{path}: parsed shape {samples.shape} does not match {len(columns)} columns"
        )
    return CosmosisChain(columns=columns, samples=samples)
