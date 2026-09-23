"""Persisted live-event contract, including idempotency and stock extremes."""

import pytest
from contextlib import closing
from src.utils import load_config
from src.data_generation import generate
from database.database import load, read, connect
from src import realtime_engine as live
from src.kpi_engine import calculate


@pytest.fixture
def simulation(tmp_path, monkeypatch):
    monkeypatch.setenv("SWIFTCART_DATA_DIR", str(tmp_path))
    c = load_config()
    c.update(dataset_size=100, days=56, stores=2, products=8)
    load(generate(c))
    live.reset()
    return live


def test_pause_blocks(simulation):
    assert simulation.ingest("paused") == 0


def test_speed(simulation):
    simulation.control(True, 7)
    assert simulation.ingest("batch") == 7
    assert len(read("FACT_ORDERS", simulation.live_path())) == 7


def test_duplicate_batch(simulation):
    simulation.control(True, 3)
    simulation.ingest("same")
    before = read(
        "FACT_INVENTORY_SNAPSHOTS", simulation.live_path()
    ).closing_stock.sum()
    assert simulation.ingest("same") == 0
    assert (
        read("FACT_INVENTORY_SNAPSHOTS", simulation.live_path()).closing_stock.sum()
        == before
    )


def test_reset_preserves_history(simulation):
    simulation.control(True, 5)
    simulation.ingest("one")
    simulation.reset()
    assert simulation.state()["events_processed"] == 0
    assert len(read("FACT_ORDERS")) == 100


def test_live_inventory_balance(simulation):
    simulation.control(True, 50)
    simulation.ingest("burst")
    s = read("FACT_INVENTORY_SNAPSHOTS", simulation.live_path())
    assert (s.closing_stock >= 0).all()
    assert (
        s.opening_stock + s.received_units - s.wastage_units - s.sold_units
        == s.closing_stock
    ).all()


def test_live_same_kpis(simulation):
    simulation.control(True, 10)
    simulation.ingest("metrics")
    k = calculate(read("item_analytics", simulation.live_path()))
    assert k["orders"] == 10
    assert k["gross_profit_inr"] - k["variable_cost_inr"] == pytest.approx(
        k["contribution_profit_inr"]
    )


def test_invalid_speed(simulation):
    with pytest.raises(ValueError):
        simulation.control(True, 0)


def test_live_zero_inventory(simulation):
    with closing(connect(simulation.live_path())) as c:
        c.execute("UPDATE FACT_INVENTORY_SNAPSHOTS SET closing_stock=0,opening_stock=0")
        c.commit()
    simulation.control(True, 50)
    simulation.ingest("empty")
    x = read("item_analytics", simulation.live_path())
    assert x.quantity_unfulfilled.sum() > 0
    assert (
        read("FACT_INVENTORY_SNAPSHOTS", simulation.live_path()).closing_stock >= 0
    ).all()


def test_live_fk_rejects(simulation):
    import sqlite3

    with closing(connect(simulation.live_path())) as c:
        with pytest.raises(sqlite3.IntegrityError):
            c.execute("INSERT INTO FACT_PROMOTIONS VALUES(-1,999)")


def test_event_timestamps(simulation):
    simulation.control(True, 2)
    simulation.ingest("timestamps")
    e = simulation.recent_events()
    assert e.event_timestamp.notna().all()
    assert e.ingestion_timestamp.notna().all()
    assert e.event_id.is_unique


def test_invalid_event_batch(simulation):
    with pytest.raises(ValueError):
        simulation.ingest("")
