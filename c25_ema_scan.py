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

        # Sikrer at Close bliver en simpel Series
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        ema50 = close.ewm(span=50, adjust=False).mean()

        close_today = float(close.iloc[-1])
        close_yesterday = float(close.iloc[-2])

        ema_today = float(ema50.iloc[-1])
        ema_yesterday = float(ema50.iloc[-2])

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

report = []

report.append(f"C25 EMA50 Scan - {datetime.now():%Y-%m-%d}")
report.append("")

report.append("AKTIER OVER EMA50")
report.append("=================")

if above_ema50:
    report.extend(above_ema50)
else:
    report.append("Ingen aktier fundet")

report.append("")
report.append("KRYDSER OP OVER EMA50 I DAG")
report.append("==========================")

if crossed_today:
    report.extend(crossed_today)
else:
    report.append("Ingen aktier fundet")

if errors:
    report.append("")
    report.append("FEJL")
    report.append("====")
    report.extend(errors)

body = "\n".join(report)

print(body)

# Email
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
 
EMAIL_SENDER = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL")

if (
    SMTP_SERVER
    and EMAIL_SENDER
    and EMAIL_PASSWORD
    and EMAIL_RECEIVER
):

    msg = MIMEText(body)

    msg["Subject"] = "Daglig C25 EMA50 Scan"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)

#    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
#      smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
#      smtp.send_message(msg)

    print("E-mail sendt")
else:
    print("Ingen e-mail konfigureret")
