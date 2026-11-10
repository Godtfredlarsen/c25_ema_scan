import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

import pandas as pd
import yfinance as yf

TICKERS = {
    "Novo Nordisk": "NOVO-B.CO",
    "DSV": "DSV.CO",
    "Vestas": "VWS.CO",
    "Coloplast": "COLO-B.CO",
    "Genmab": "GMAB.CO",
    "Carlsberg": "CARL-B.CO",
    "Danske Bank": "DANSKE.CO",
    "Demant": "DEMANT.CO",
    "Ørsted": "ORSTED.CO",
    "Pandora": "PNDORA.CO",
    "Tryg": "TRYG.CO",
    "Rockwool": "ROCK-B.CO",
    "GN Store Nord": "GN.CO",
    "Jyske Bank": "JYSK.CO",
    "Netcompany": "NETC.CO",
    "Sydbank": "ALSYDB.CO",
    "NKT": "NKT.CO",
    "Ambu": "AMBU-B.CO",
    "Bavarian Nordic": "BAVA.CO",
    "ISS": "ISS.CO",
    "Zealand Pharma": "ZEAL.CO"
}

above_ema50 = []
crossed_today = []
errors = []

for company, ticker in TICKERS.items():

    try:

        df = yf.download(
            ticker,
            period="6mo",
            interval="1d",
            auto_adjust=True,
            progress=False
        )

        if df.empty or len(df) < 60:
            continue

        close = df["Close"]

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        ema50 = close.ewm(span=50, adjust=False).mean()

        close_today = float(close.iloc[-1])
        close_yesterday = float(close.iloc[-2])

        ema_today = float(ema50.iloc[-1])
        ema_yesterday = float(ema50.iloc[-2])

        if ticker == "NOVO-B.CO":
            print(f"NOVO Close={close_today}")
            print(f"NOVO EMA50={ema_today}")

        if close_today > ema_today:
            above_ema50.append(
                f"{company}: Kurs {close_today:.2f} | EMA50 {ema_today:.2f}"
            )

        if (
            close_yesterday <= ema_yesterday
            and close_today > ema_today
        ):
            crossed_today.append(
                f"{company}: Kurs {close_today:.2f} | EMA50 {ema_today:.2f}"
            )

    except Exception as e:
        errors.append(f"{ticker}: {str(e)}")
