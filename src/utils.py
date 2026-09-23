"""Configuration, safe arithmetic and centralized Indian Rupee presentation."""

from __future__ import annotations

import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def format_inr(value: float, decimals: int = 0) -> str:
    """Format numeric INR using Indian digit grouping; undefined is explicit."""
    if value is None or not math.isfinite(float(value)):
        return "Not available"
    sign = "-" if value < 0 else ""
    number = f"{abs(value):.{decimals}f}"
    whole, dot, fraction = number.partition(".")
    tail = whole[-3:]
    head = whole[:-3]
    groups = []
    while head:
        groups.insert(0, head[-2:])
        head = head[:-2]
    grouped = ",".join(groups + [tail])
    return f"{sign}₹{grouped}{dot}{fraction}"


def ratio(numerator: float, denominator: float) -> float:
    """Return zero for an empty denominator, as documented for empty slices."""
    return float(numerator / denominator) if denominator else 0.0


def data_root() -> Path:
    """Allow large generated artifacts on another drive without code edits."""
    return Path(os.environ.get("SWIFTCART_DATA_DIR", str(ROOT / "data")))


def load_config() -> dict:
    """Read YAML and validated environment overrides."""
    import yaml

    with (ROOT / "config" / "config.yaml").open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    config["dataset_size"] = int(os.environ.get("DATASET_SIZE", config["dataset_size"]))
    config["seed"] = int(os.environ.get("SEED", config["seed"]))
    if config["dataset_size"] < 0:
        raise ValueError("DATASET_SIZE must be non-negative")
    if config["days"] < 42:
        raise ValueError(
            "At least 42 calendar days are required for temporal evaluation"
        )
    return config
