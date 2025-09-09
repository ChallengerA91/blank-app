#!/usr/bin/env python3
"""Fetch cryptocurrency prices and store them in a SQLite database."""

import sqlite3
from datetime import datetime

import requests

DB_NAME = "crypto.db"
TABLE_NAME = "prices"
COINS = {
    "bitcoin": "btc",
    "ethereum": "eth",
    "litecoin": "ltc",
    "dogecoin": "doge",
}
API_URL = "https://api.coingecko.com/api/v3/simple/price"


def fetch_prices():
    """Fetch latest prices for supported cryptocurrencies in USD."""
    ids = ",".join(COINS.keys())
    params = {"ids": ids, "vs_currencies": "usd"}
    resp = requests.get(API_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return {abbr: data[name]["usd"] for name, abbr in COINS.items()}


def init_db():
    """Create the prices table if it does not exist and return a connection."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            btc REAL,
            eth REAL,
            ltc REAL,
            doge REAL
        )
        """
    )
    conn.commit()
    return conn


def insert_prices(conn, prices):
    """Insert a new row with the current timestamp and price data."""
    timestamp = datetime.utcnow().isoformat()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO prices (timestamp, btc, eth, ltc, doge)
        VALUES (?, ?, ?, ?, ?)
        """,
        (timestamp, prices["btc"], prices["eth"], prices["ltc"], prices["doge"]),
    )
    conn.commit()


def get_last_entries(n=5):
    """Print the last ``n`` rows from the prices table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT timestamp, btc, eth, ltc, doge
        FROM {TABLE_NAME}
        ORDER BY id DESC
        LIMIT ?
        """,
        (n,),
    )
    rows = cursor.fetchall()
    conn.close()
    for row in reversed(rows):
        ts, btc, eth, ltc, doge = row
        print(f"{ts}: BTC={btc}, ETH={eth}, LTC={ltc}, DOGE={doge}")


def main():
    conn = init_db()
    prices = fetch_prices()
    insert_prices(conn, prices)
    conn.close()
    get_last_entries()


if __name__ == "__main__":
    main()
