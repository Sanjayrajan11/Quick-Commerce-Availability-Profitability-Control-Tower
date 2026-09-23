"""Auditable deterministic repairs; unexpected irreparable issues fail validation."""

import pandas as pd
from src.validation import KEYS, RELATIONS, validate


def clean(raw: dict) -> tuple[dict, pd.DataFrame]:
    """Deduplicate, normalize, map unknown customer and repair redundant fields."""
    t, rows = {}, []
    for name, frame in raw.items():
        dedup = frame.drop_duplicates(KEYS[name]).copy()
        missing = int(frame.isna().sum().sum())
        duplicate = len(frame) - len(dedup)
        orphan = sum(
            int((~dedup[col].isin(raw[parent][KEYS[parent]])).sum())
            for child, col, parent in RELATIONS
            if child == name
        )
        corrected = set()
        invalid = outliers = 0
        if name == "FACT_ORDERS":
            mask = dedup.payment_method.isna()
            corrected.update(dedup.index[mask])
            dedup.loc[mask, "payment_method"] = "Unknown"
            normalized = dedup.status.str.strip().str.title()
            mask = normalized != dedup.status
            invalid += int(mask.sum())
            corrected.update(dedup.index[mask])
            dedup["status"] = normalized
            mask = ~dedup.customer_id.isin(raw["DIM_CUSTOMER"].customer_id)
            corrected.update(dedup.index[mask])
            dedup.loc[mask, "customer_id"] = -1
            mask = pd.to_datetime(dedup.ordered_at, errors="coerce").isna()
            invalid += int(mask.sum())
            corrected.update(dedup.index[mask])
            dedup.loc[mask, "ordered_at"] = (
                dedup.loc[mask, "date"]
                + " "
                + dedup.loc[mask, "hour"].astype(str).str.zfill(2)
                + ":00:00"
            )
        if name == "DIM_PRODUCT":
            mask = ~dedup.category_id.isin(raw["DIM_CATEGORY"].category_id)
            invalid += int(mask.sum())
            corrected.update(dedup.index[mask])
            dedup.loc[mask, "category_id"] = dedup.loc[mask, "supplier_id"]
        if name == "FACT_DELIVERY":
            mask = (dedup.distance_km > 20) | (dedup.distance_km < 0)
            outliers = int(mask.sum())
            corrected.update(dedup.index[mask])
            dedup.loc[mask, "distance_km"] = dedup.loc[~mask, "distance_km"].median()
        rows.append(
            {
                "table": name,
                "total_records": len(frame),
                "missing_values": missing,
                "duplicate_records": duplicate,
                "invalid_values": invalid,
                "outliers": outliers,
                "referential_integrity_issues": orphan,
                "records_removed": duplicate,
                "records_corrected": len(corrected),
                "records_retained": len(dedup),
                "records_added": 0,
            }
        )
        t[name] = dedup
    if (
        -1 in t["FACT_ORDERS"].customer_id.values
        and -1 not in t["DIM_CUSTOMER"].customer_id.values
    ):
        t["DIM_CUSTOMER"] = pd.concat(
            [
                t["DIM_CUSTOMER"],
                pd.DataFrame({"customer_id": [-1], "segment": ["Unknown"]}),
            ],
            ignore_index=True,
        )
        for row in rows:
            if row["table"] == "DIM_CUSTOMER":
                row["records_added"] = 1
    validate(t)
    return t, pd.DataFrame(rows)
