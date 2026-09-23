"""Application navigation and controls against an isolated small pipeline."""

from datetime import date
import os
import pytest
from streamlit.testing.v1 import AppTest
from src.utils import ROOT, load_config
from src.data_generation import generate
from database.database import load


@pytest.fixture(scope="module")
def app(tmp_path_factory):
    sandbox = tmp_path_factory.mktemp("appdata")
    prior = os.environ.get("SWIFTCART_DATA_DIR")
    os.environ["SWIFTCART_DATA_DIR"] = str(sandbox)
    c = load_config()
    c.update(dataset_size=100, days=56, stores=2, products=8)
    load(generate(c))
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    yield at
    if prior is None:
        os.environ.pop("SWIFTCART_DATA_DIR", None)
    else:
        os.environ["SWIFTCART_DATA_DIR"] = prior


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


@pytest.mark.parametrize("page", PAGES)
def test_workspace(app, page):
    app.selectbox[0].set_value(page).run()
    assert not app.exception


def test_city_store_product_drilldown(app):
    app.selectbox[0].set_value("AVAILABILITY").run()
    app.selectbox[1].set_value("Chennai").run()
    app.selectbox[2].set_value(0).run()
    app.selectbox[3].set_value(0).run()
    app.selectbox[4].set_value(0).run()
    assert not app.exception
    app.selectbox[1].set_value("All").run()
    app.selectbox[2].set_value("All").run()
    app.selectbox[3].set_value("All").run()
    app.selectbox[4].set_value("All").run()


def test_empty_city(app):
    app.selectbox[0].set_value("CONTROL TOWER").run()
    app.selectbox[1].set_value("Mumbai").run()
    assert not app.exception
    assert any("No orders" in i.value for i in app.info)
    app.selectbox[1].set_value("All").run()


def test_scenario_controls(app):
    app.selectbox[0].set_value("SCENARIO LAB").run()
    before = app.dataframe[0].value.copy()
    app.slider[0].set_value(50).run()
    after = app.dataframe[0].value
    assert not app.exception
    assert before.iloc[0]["net_sales_inr"] != after.iloc[0]["net_sales_inr"]


def test_forecast_horizon(app):
    app.selectbox[0].set_value("FORECASTING").run()
    app.slider[0].set_value(28).run()
    assert not app.exception
    assert len(app.dataframe[1].value) == 28


def test_forecast_insufficient_history(app):
    app.date_input[0].set_value((date(2026, 1, 1), date(2026, 1, 10))).run()
    assert not app.exception
    assert any("42 days" in i.value for i in app.info)
    app.date_input[0].set_value((date(2026, 1, 1), date(2026, 2, 25))).run()


def test_explorer_search(app):
    app.selectbox[0].set_value("DATA EXPLORER").run()
    app.text_input[0].set_value("does-not-exist").run()
    assert not app.exception
    app.text_input[0].set_value("").run()


def test_download_present(app):
    app.selectbox[0].set_value("INVENTORY").run()
    assert len(app.get("download_button")) > 0


def test_live_controls(app):
    app.selectbox[0].set_value("CONTROL TOWER").run()
    app.radio[0].set_value("LIVE SIMULATION").run()
    assert not app.exception
    [b for b in app.button if b.label == "Start Simulation"][0].click().run()
    assert not app.exception
    [b for b in app.button if b.label == "Pause Simulation"][0].click().run()
    assert not app.exception
    [b for b in app.button if b.label == "Reset Simulation"][0].click().run()
    assert not app.exception
    app.radio[0].set_value("HISTORICAL").run()
