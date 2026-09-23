import yfinance as yf
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText

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
    "Sydbank": "SYDB.CO",
    "NKT": "NKT.CO",
    "Ambu": "AMBU-B.CO",
    "Bavarian Nordic": "BAVA.CO",
    "ISS": "ISS.CO",
    "Zealand Pharma": "ZEAL.CO"
}

above_ema50 = []
crossed_today = []

for name, ticker in TICKERS.items():

    df = yf.download(
        ticker,
        period="6mo",
        interval="1d",
        auto_adjust=True,
        progress=False
    )

    if len(df) < 50:
        continue

    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()

    close_today = float(df["Close"].iloc[-1])
    ema_today = float(df["EMA50"].iloc[-1])

    close_yesterday = float(df["Close"].iloc[-2])
    ema_yesterday = float(df["EMA50"].iloc[-2])

    if close_today > ema_today:
        above_ema50.append(
            f"{name} | Kurs {close_today:.2f} | EMA50 {ema_today:.2f}"
        )

    if close_yesterday <= ema_yesterday and close_today > ema_today:
        crossed_today.append(
            f"{name} | Kurs {close_today:.2f} | EMA50 {ema_today:.2f}"
        )

report = []
report.append(f"C25 EMA50 Scan - {datetime.now():%Y-%m-%d}")
report.append("")
report.append("AKTIER OVER EMA50")
report.append("=================")

for stock in above_ema50:
    report.append(stock)

report.append("")
report.append("KRYDSER OP OVER EMA50 I DAG")
report.append("==========================")

for stock in crossed_today:
    report.append(stock)

body = "\n".join(report)

print(body)

SMTP_SERVER = os.environ["SMTP_SERVER"]
SMTP_PORT = int(os.environ["SMTP_PORT"])
EMAIL_SENDER = os.environ["EMAIL_SENDER"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_RECEIVER = os.environ["EMAIL_RECEIVER"]

msg = MIMEText(body)
msg["Subject"] = "Daglig C25 EMA50 Scan"
msg["From"] = EMAIL_SENDER
msg["To"] = EMAIL_RECEIVER

with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
    smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
    smtp.send_message(msg)
