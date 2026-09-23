"""SwiftCart synthetic operations control tower. Run with Streamlit."""

import uuid
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from database.database import database_path, read
from src.utils import ROOT, format_inr
from src.kpi_engine import calculate, grouped
from src import (
    inventory,
    profitability,
    forecasting,
    risk_engine,
    recommendations,
    realtime_engine,
)
from src.scenario_engine import simulate

PAGES = [
    "CONTROL TOWER",
    "AVAILABILITY",
    "INVENTORY",
    "PROFITABILITY",
    "STORE OPERATIONS",
    "DEMAND",
    "DELIVERY",
    "PROMOTIONS",
    "OPPORTUNITIES",
    "SCENARIO LAB",
    "ACTION CENTER",
    "DATA EXPLORER",
    "FORECASTING",
    "METHODOLOGY",
]
st.set_page_config(
    page_title="SwiftCart | Operations desk",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(
    """<style>.block-container{padding-top:1.3rem;max-width:1560px} h1{letter-spacing:-1.5px} h2{border-top:2px solid #233d38;padding-top:16px} [data-testid="stMetric"]{border-left:3px solid #a44a30;padding-left:12px} [data-testid="stDataFrame"]{border:1px solid #c7cec4} .stButton button{border-radius:2px} </style>""",
    unsafe_allow_html=True,
)
st.caption("SWIFTCART / SYNTHETIC PORTFOLIO SIMULATION / INDIA")
st.title("Availability & profitability · Operations desk")
st.caption(
    "All data in this project is synthetic and simulated for educational and portfolio purposes. All monetary values use INR."
)


@st.cache_data(show_spinner="Reading the analytical store…", max_entries=4)
def dataset(path: str, version: float):
    return {
        name: read(name, path)
        for name in [
            "item_analytics",
            "FACT_INVENTORY_SNAPSHOTS",
            "FACT_DELIVERY",
            "DIM_PRODUCT",
            "DIM_SUPPLIER",
            "DIM_STORE",
            "DIM_CITY",
            "DIM_CATEGORY",
            "DIM_STORE_OPERATIONS",
            "DIM_DATE",
        ]
    }


def table(frame: pd.DataFrame, key: str, limit=250):
    """Display central INR formatting while preserving numeric CSV exports."""
    shown = frame.head(limit).copy()
    for column in shown:
        if column.endswith("_inr"):
            shown[column] = shown[column].map(lambda x: format_inr(x, 2))
    st.dataframe(shown, width="stretch", hide_index=True)
    st.caption(
        f"Showing {min(len(frame), limit):,} of {len(frame):,} rows. CSV exports the first 10,000 rows with numeric INR amounts. Use SQLite or Parquet for full extracts."
    )
    st.download_button(
        "Download CSV",
        frame.head(10000).to_csv(index=False).encode("utf-8-sig"),
        file_name=f"{key}.csv",
        mime="text/csv",
        key=f"download_{key}",
    )


def chart(frame, x, y, title, money=False, line=False):
    fig = go.Figure()
    custom = [format_inr(v) if money else f"{v:,.2f}" for v in frame[y]]
    trace = (
        go.Scatter(
            x=frame[x],
            y=frame[y],
            mode="lines+markers",
            line={"color": "#386A61"},
            customdata=custom,
            hovertemplate="%{x}<br>%{customdata}<extra></extra>",
        )
        if line
        else go.Bar(
            x=frame[x].astype(str),
            y=frame[y],
            marker_color="#A44A30",
            customdata=custom,
            hovertemplate="%{x}<br>%{customdata}<extra></extra>",
        )
    )
    fig.add_trace(trace)
    fig.update_layout(
        title=title,
        height=330,
        margin={"l": 20, "r": 20, "t": 45, "b": 20},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title=x.replace("_", " "),
        yaxis_title="INR" if money else y.replace("_", " "),
    )
    if money and len(frame):
        ticks = np.linspace(min(0, frame[y].min()), max(0, frame[y].max()), 5)
        fig.update_yaxes(tickvals=ticks, ticktext=[format_inr(v) for v in ticks])
    st.plotly_chart(fig, width="stretch")


def metrics(k):
    a, b, c, d = st.columns(4)
    a.metric("Fill rate", f"{k['fill_rate']:.1%}")
    b.metric("Net sales", format_inr(k["net_sales_inr"]))
    c.metric("Contribution before write-offs", format_inr(k["contribution_profit_inr"]))
    d.metric("ESTIMATED lost revenue", format_inr(k["estimated_lost_revenue_inr"]))


def render_workspace(path, page):
    t = dataset(str(path), path.stat().st_mtime)
    all_items = t["item_analytics"]
    snap = t["FACT_INVENTORY_SNAPSHOTS"]
    with st.expander("Scope · City → Store → Category → Product / SKU", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        city = c1.selectbox("City", ["All"] + t["DIM_CITY"].city.tolist())
        cities = t["DIM_CITY"] if city == "All" else t["DIM_CITY"].query("city==@city")
        stores = t["DIM_STORE"][t["DIM_STORE"].city_id.isin(cities.city_id)]
        store = c2.selectbox(
            "Store",
            ["All"] + stores.store_id.tolist(),
            format_func=lambda x: x if x == "All" else f"Store {x + 1:02}",
        )
        category = c3.selectbox(
            "Category",
            ["All"] + t["DIM_CATEGORY"].category_id.tolist(),
            format_func=lambda x: (
                x
                if x == "All"
                else t["DIM_CATEGORY"].set_index("category_id").loc[x, "category"]
            ),
        )
        products = (
            t["DIM_PRODUCT"]
            if category == "All"
            else t["DIM_PRODUCT"].query("category_id==@category")
        )
        product = c4.selectbox(
            "Product / SKU",
            ["All"] + products.product_id.tolist(),
            format_func=lambda x: (
                x
                if x == "All"
                else f"{products.set_index('product_id').loc[x, 'sku']} · {products.set_index('product_id').loc[x, 'product']}"
            ),
        )
        ds = pd.to_datetime(t["DIM_DATE"].date)
        date_range = st.date_input(
            "Date range",
            value=(ds.min().date(), ds.max().date()),
            min_value=ds.min().date(),
            max_value=ds.max().date(),
        )
    if len(date_range) != 2:
        st.info("Choose a start and end date.")
        return
    start, end = map(str, date_range)
    selected_stores = stores.store_id.tolist() if store == "All" else [store]
    selected_products = products.product_id.tolist() if product == "All" else [product]
    items = all_items[
        all_items.store_id.isin(selected_stores)
        & all_items.product_id.isin(selected_products)
        & all_items.date.between(start, end)
    ]
    snapshots = snap[
        snap.store_id.isin(selected_stores)
        & snap.product_id.isin(selected_products)
        & snap.date.between(start, end)
    ]
    k = calculate(items, snapshots, t["FACT_DELIVERY"])
    inv = inventory.analyze(snapshots, t["DIM_PRODUCT"], t["DIM_SUPPLIER"])
    risks = risk_engine.score(inv)
    actions = (
        recommendations.generate(
            items, risks, t["FACT_DELIVERY"], t["DIM_STORE_OPERATIONS"]
        )
        if len(risks)
        else pd.DataFrame(columns=recommendations.COLUMNS)
    )
    st.caption(
        f"{start} → {end} · {k['orders']:,} attempted orders in scope · INR numeric exports · snapshot availability differs from unit fill rate"
    )
    if page == "METHODOLOGY":
        st.markdown((ROOT / "docs/METHODOLOGY.md").read_text(encoding="utf-8"))
        return
    if page == "DATA EXPLORER":
        name = st.selectbox(
            "Dataset",
            [
                "Filtered item analytics",
                "Filtered inventory snapshots",
                "DIM_PRODUCT",
                "DIM_STORE",
                "DIM_CITY",
                "DIM_CATEGORY",
                "DIM_SUPPLIER",
                "FACT_DELIVERY",
            ],
        )
        frame = (
            items
            if name == "Filtered item analytics"
            else snapshots
            if name == "Filtered inventory snapshots"
            else t[name]
        )
        st.caption(
            "Scope filters apply to the two filtered datasets. Reference tables show the full dimension. Delivery is restricted to selected orders."
        )
        if name == "FACT_DELIVERY":
            frame = frame[frame.order_id.isin(items.order_id)]
        search = st.text_input("Search displayed dataset")
        if search:
            frame = frame[
                frame.astype(str)
                .apply(lambda col: col.str.contains(search, case=False, regex=False))
                .any(axis=1)
            ]
        sort = st.selectbox("Sort column", frame.columns.tolist())
        descending = st.checkbox("Descending", value=False)
        rows = st.slider("Preview rows", 10, 1000, 100)
        table(frame.sort_values(sort, ascending=not descending), "explorer", rows)
        st.write("Numeric summary (monetary columns labeled INR)")
        summary = (
            frame.select_dtypes("number").describe().drop(index="count").reset_index()
        )
        table(summary, "summary")
        return
    if page in ["INVENTORY", "ACTION CENTER", "OPPORTUNITIES"]:
        if page == "INVENTORY":
            st.subheader("Inventory position · coverage before commitment")
            if inv.empty:
                st.info("No inventory observations for this scope.")
                return
            a, b, c = st.columns(3)
            a.metric("Inventory at cost", format_inr(inv.inventory_value_inr.sum()))
            b.metric("Reorder candidates", int((inv.reorder_quantity > 0).sum()))
            c.metric(
                "Expiry / dead-stock exposure",
                format_inr(inv.inventory_at_risk_inr.sum()),
            )
            chart(
                inv.groupby("health", as_index=False).closing_stock.sum(),
                "health",
                "closing_stock",
                "Units by inventory condition",
            )
            table(
                risks[
                    [
                        "store_id",
                        "sku",
                        "health",
                        "velocity",
                        "closing_stock",
                        "average_demand",
                        "demand_trend",
                        "days_of_inventory",
                        "lead_days",
                        "safety_stock",
                        "reorder_point",
                        "target_stock",
                        "reorder_quantity",
                        "inventory_turnover",
                        "inventory_value_inr",
                        "risk_level",
                    ]
                ],
                "inventory",
            )
        else:
            st.subheader("Review queue · evidence → owner → next action")
            st.warning(
                "Financial exposure is ESTIMATED. Actions overlap; do not sum their impact as a benefit."
            )
            priority = st.multiselect(
                "Priority",
                ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                default=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            )
            table(
                actions[actions.priority.isin(priority)].sort_values(
                    "financial_impact_inr", ascending=False
                ),
                "actions",
            )
        return
    if items.empty:
        st.info(
            "No orders match this scope. Inventory remains available in its workspace."
        )
        return
    if page == "CONTROL TOWER":
        st.subheader("Intervention brief")
        left, right = st.columns([2, 1])
        with left:
            if actions.empty:
                st.success("No configured action rules triggered. Continue monitoring.")
            for r in (
                actions.sort_values("financial_impact_inr", ascending=False)
                .head(3)
                .itertuples()
            ):
                st.markdown(
                    f"**{r.priority} · {r.issue} · Store {r.store_id} / SKU {r.product_id}**"
                )
                st.write(r.evidence)
                st.caption(
                    f"Estimated exposure {format_inr(r.financial_impact_inr)} · {r.recommended_action} · {r.suggested_owner} / {r.suggested_timing}"
                )
        with right:
            st.write("**Operating signals**")
            st.write(f"Opening availability: {k['availability_rate']:.1%}")
            st.write(f"On-time delivery: {k['on_time_rate']:.1%}")
            st.write(f"Contribution margin: {k['contribution_margin']:.1%}")
            st.write(
                f"Critical stock risks: {int((risks.risk_level == 'CRITICAL').sum()) if len(risks) else 0}"
            )
            st.caption(
                "Review replenishment failures and coverage evidence. Scores are rule-based deficit indices, not probabilities."
            )
        metrics(k)
        table(grouped(items, "store_id"), "store_brief")
    elif page == "AVAILABILITY":
        metrics(k)
        a, b, c = st.columns(3)
        a.metric("Opening availability", f"{k['availability_rate']:.1%}")
        b.metric("Unfulfilled units", int(k["quantity_unfulfilled"]))
        c.metric("Accepted replacement rate", f"{k['substitution_rate']:.2%}")
        grouped_items = items.groupby(["store_id", "category_id"])[
            ["quantity_fulfilled", "quantity_ordered"]
        ].sum()
        heat = (
            grouped_items.quantity_fulfilled / grouped_items.quantity_ordered
        ).unstack()
        fig = go.Figure(
            go.Heatmap(
                z=heat.values,
                x=heat.columns.astype(str),
                y=heat.index.astype(str),
                zmin=0,
                zmax=1,
                colorscale=[[0, "#A44A30"], [1, "#386A61"]],
                hovertemplate="Category %{x}<br>Store %{y}<br>Fill %{z:.1%}<extra></extra>",
            )
        )
        fig.update_layout(title="Fulfillment heatmap · store × category", height=330)
        st.plotly_chart(fig, width="stretch")
        table(grouped(items, "product_id"), "availability")
    elif page == "PROFITABILITY":
        metrics(k)
        values = [
            k["gross_sales_inr"],
            -k["discount_inr"],
            -k["cogs_inr"],
            -k["variable_cost_inr"],
            k["contribution_profit_inr"],
        ]
        fig = go.Figure(
            go.Waterfall(
                x=[
                    "Gross sales",
                    "Discount",
                    "COGS",
                    "Variable operations",
                    "Contribution",
                ],
                y=values,
                measure=["absolute", "relative", "relative", "relative", "total"],
                text=[format_inr(v) for v in values],
                hoverinfo="text",
                textposition="outside",
            )
        )
        ticks = np.linspace(0, k["gross_sales_inr"], 5)
        fig.update_yaxes(tickvals=ticks, ticktext=[format_inr(v) for v in ticks])
        fig.update_layout(
            title="Margin bridge · before inventory write-offs", height=400
        )
        st.plotly_chart(fig, width="stretch")
        dimension = st.selectbox(
            "Profitability grain", ["product_id", "category_id", "store_id", "segment"]
        )
        table(profitability.analyze(items, dimension), "profitability")
    elif page == "STORE OPERATIONS":
        st.subheader("Store health · service, stock, economics and workload")
        metrics(k)
        table(grouped(items, "store_id"), "store_operations")
        operations = t["DIM_STORE_OPERATIONS"][
            t["DIM_STORE_OPERATIONS"].store_id.isin(selected_stores)
        ].copy()
        observed = (
            items[["order_id", "store_id", "date"]]
            .drop_duplicates()
            .groupby("store_id")
            .size()
            / k["period_days"]
        )
        operations["average_daily_orders"] = operations.store_id.map(observed).fillna(0)
        operations["capacity_utilization"] = (
            operations.average_daily_orders / operations.daily_capacity
        )
        table(operations, "capacity")
        table(actions, "store_actions")
    elif page == "DEMAND":
        grain = st.selectbox(
            "Time grain", ["Daily", "Weekly", "Monthly", "Hour", "Weekday"]
        )
        x = items.copy()
        dt = pd.to_datetime(x.date)
        x["period"] = (
            x.date
            if grain == "Daily"
            else dt.dt.to_period("W").astype(str)
            if grain == "Weekly"
            else dt.dt.to_period("M").astype(str)
            if grain == "Monthly"
            else x.hour.astype(str)
            if grain == "Hour"
            else dt.dt.day_name()
        )
        demand = x.groupby("period", as_index=False).quantity_ordered.sum()
        chart(demand, "period", "quantity_ordered", "Requested demand", line=True)
        table(grouped(items, "segment"), "customer_segments")
        table(
            inv[["store_id", "sku", "average_demand", "demand_std", "velocity"]],
            "velocity",
        )
    elif page == "DELIVERY":
        a, b, c = st.columns(3)
        a.metric("On-time delivered orders", f"{k['on_time_rate']:.1%}")
        b.metric("Mean duration", f"{k['average_delivery_minutes']:.1f} min")
        c.metric("P90 duration", f"{k['p90_delivery_minutes']:.1f} min")
        order_scope = items[["order_id", "store_id", "hour", "status"]].drop_duplicates(
            "order_id"
        )
        d = t["FACT_DELIVERY"].merge(order_scope, on="order_id")
        delivered = d[d.status == "Delivered"]
        chart(
            delivered.groupby("store_id", as_index=False).actual_minutes.mean(),
            "store_id",
            "actual_minutes",
            "Store delivery duration",
        )
        table(d, "delivery")
        st.caption(
            "Cancelled orders have no delivery duration. This simulation cannot estimate a delivery-delay effect on cancellations; cancellations precede dispatch."
        )
    elif page == "PROMOTIONS":
        st.warning(
            "Observed comparisons and incremental proxies are noncausal; basket mix differs with exposure."
        )
        table(profitability.promotions(items), "promotions")
    elif page == "SCENARIO LAB":
        st.subheader("MODELED ESTIMATE · fixed mix and unit cost")
        a, b, c = st.columns(3)
        growth = a.slider("Demand growth (%)", -100, 100, 10) / 100
        availability = a.slider("Availability cap (%)", 0, 100, 100) / 100
        fill = (
            b.slider("Fulfillment rate (%)", 0, 100, int(round(k["fill_rate"] * 100)))
            / 100
        )
        discount = (
            b.slider(
                "Discount rate (%)",
                0,
                100,
                int(round(k["discount_inr"] / k["gross_sales_inr"] * 100))
                if k["gross_sales_inr"]
                else 0,
            )
            / 100
        )
        price = c.slider("AOV / price change (%)", -100, 100, 0) / 100
        delivery = c.slider("Delivery unit cost change (%)", -100, 100, 0) / 100
        lead = c.number_input(
            "Lead time (days)", min_value=0.0, max_value=60.0, value=3.0
        )
        result = simulate(
            k, growth, fill, discount, price, delivery, lead, availability
        )
        st.caption(
            f"Modeled stockout cap: {1 - availability:.1%}. Delivery cost changes affect delivery cost only. Inventory requirement uses daily demand × lead time."
        )
        table(pd.DataFrame([result]), "scenario")
    elif page == "FORECASTING":
        st.subheader("Demand outlook · chronological holdout")
        horizon = st.slider("Forecast horizon (days)", 7, 28, 14)
        daily = (
            items.groupby("date")
            .quantity_ordered.sum()
            .reindex(pd.date_range(start, end).strftime("%Y-%m-%d"), fill_value=0)
        )
        daily.index = pd.to_datetime(daily.index)
        if len(daily) < 42:
            st.info(
                "At least 42 days are required for training, selection and test periods."
            )
            return
        future, scores, back = forecasting.forecast(daily, horizon)
        selected = scores.loc[scores.selected, "model"].iloc[0]
        fig = go.Figure(
            go.Scatter(
                x=daily.index, y=daily, mode="lines", name="Historical requested units"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=future.date,
                y=future.forecast_units,
                name="Future estimate",
                line={"dash": "dash"},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=future.date,
                y=future.upper_units,
                line={"width": 0},
                name="Upper band",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=future.date,
                y=future.lower_units,
                fill="tonexty",
                line={"width": 0},
                name="Lower band",
            )
        )
        test = back[back.model == selected]
        fig.add_trace(
            go.Scatter(x=test.date, y=test.forecast_units, name="Held-out prediction")
        )
        fig.update_layout(
            height=380,
            title=f"Selected on validation MAE: {selected}",
            yaxis_title="Requested units",
        )
        st.plotly_chart(fig, width="stretch")
        st.caption(
            "Bands use validation residuals and have no guaranteed coverage. WAPE is undefined when total actual demand is zero. Select store/category/SKU in Scope."
        )
        table(scores, "forecast_metrics")
        table(future, "forecast")
        weekly = (
            future.set_index("date")[["forecast_units", "lower_units", "upper_units"]]
            .resample("W")
            .sum()
            .reset_index()
        )
        table(weekly, "weekly_forecast")


if not database_path().exists():
    st.error("Run python run_pipeline.py before launching the application.")
    st.stop()
left, right = st.columns([3, 1])
page = left.selectbox("Workspace", PAGES)
mode = right.radio("Mode", ["HISTORICAL", "LIVE SIMULATION"], horizontal=True)
if mode == "HISTORICAL":
    render_workspace(database_path(), page)
else:
    st.warning(
        "LIVE SIMULATION — SYNTHETIC DATA · accelerated completed-order lifecycles"
    )
    current = realtime_engine.state()
    a, b, c, d, e = st.columns([1, 1, 1, 2, 1])
    speed = d.slider("Orders per refresh", 1, 50, current["speed"])
    if a.button("Start Simulation"):
        realtime_engine.control(True, speed)
    if b.button("Pause Simulation"):
        realtime_engine.control(False, speed)
    if c.button("Reset Simulation"):
        realtime_engine.reset()
        st.cache_data.clear()
    auto = e.checkbox("Auto Refresh", value=True)
    if st.button("Advance one batch"):
        realtime_engine.ingest(str(uuid.uuid4()), force=True)

    @st.fragment(run_every=3 if auto else None)
    def live_panel():
        current = realtime_engine.state()
        if current["running"]:
            realtime_engine.control(True, speed)
            realtime_engine.ingest(str(uuid.uuid4()))
        current = realtime_engine.state()
        st.caption(
            f"Simulation time {current['sim_time']} · Last event {current['last_event_time']} · Events processed {current['events_processed']} · {'RUNNING' if current['running'] else 'PAUSED'}"
        )
        render_workspace(realtime_engine.live_path(), page)
        with st.expander("Persisted event timeline"):
            table(realtime_engine.recent_events(), "live_events")

    live_panel()
