"""Transparent modeled estimates, holding product mix and unit costs fixed."""

from src.utils import ratio


def simulate(
    kpi,
    growth=0.0,
    fill_rate=None,
    discount_rate=None,
    aov_change=0.0,
    delivery_cost_change=0.0,
    lead_days=3.0,
    availability=1.0,
):
    if (
        growth < -1
        or aov_change < -1
        or delivery_cost_change < -1
        or lead_days < 0
        or not 0 <= availability <= 1
    ):
        raise ValueError("Scenario outside valid domain")
    fill = kpi["fill_rate"] if fill_rate is None else fill_rate
    discount = (
        ratio(kpi["discount_inr"], kpi["gross_sales_inr"])
        if discount_rate is None
        else discount_rate
    )
    if not 0 <= fill <= 1 or not 0 <= discount <= 1:
        raise ValueError("Rates must be between zero and one")
    demand = kpi["quantity_ordered"] * (1 + growth)
    effective_fill = min(fill, availability)
    units = demand * effective_fill
    unit_price = ratio(kpi["gross_sales_inr"], kpi["quantity_fulfilled"]) * (
        1 + aov_change
    )
    unit_cost = ratio(kpi["cogs_inr"], kpi["quantity_fulfilled"])
    gross = units * unit_price
    revenue = gross * (1 - discount)
    gross_profit = revenue - units * unit_cost
    variable = (
        kpi["variable_cost_inr"]
        + kpi.get("delivery_cost_inr", 0) * delivery_cost_change
    ) * (1 + growth)
    contribution = gross_profit - variable
    return {
        "label": "MODELED ESTIMATE",
        "net_sales_inr": revenue,
        "gross_profit_inr": gross_profit,
        "contribution_profit_inr": contribution,
        "contribution_margin": ratio(contribution, revenue),
        "estimated_lost_revenue_inr": (demand - units) * unit_price * (1 - discount),
        "revenue_impact_inr": revenue - kpi["net_sales_inr"],
        "profit_impact_inr": contribution - kpi["contribution_profit_inr"],
        "inventory_requirement_units": demand * lead_days / kpi.get("period_days", 1),
        "fulfilled_units": units,
        "stockout_assumption": 1 - availability,
    }
