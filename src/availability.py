"""Availability decomposition, using canonical definitions."""

from src.kpi_engine import grouped


def analyze(items):
    return {
        dimension: grouped(items, dimension)
        for dimension in [
            "city",
            "store_id",
            "region_id",
            "category_id",
            "product_id",
            "date",
            "hour",
            "segment",
        ]
    }
