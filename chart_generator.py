import yfinance as yf
import mplfinance as mpf
import pandas as pd
import os
import matplotlib.pyplot as plt

# Ensure Matplotlib runs in non-GUI mode
import matplotlib
matplotlib.use("Agg")

# Ensure the 'static' directory exists
if not os.path.exists("static"):
    os.makedirs("static")

def generate_chart(instrument: str, timeframe: str):
    """Generates and saves a chart image while ensuring all data is numeric."""

    # ✅ Define Yahoo Finance symbols
    symbol_map = {
        "Gold (XAUUSD)": "GC=F",
        "Bitcoin (BTC)": "BTC-USD",
        "Ethereum (ETH)": "ETH-USD",
        "Dow Jones (DJI)": "^DJI",
        "Nasdaq (IXIC)": "^IXIC",
        "EUR/USD (EURUSD)": "EURUSD=X",
        "GBP/USD (GBPUSD)": "GBPUSD=X"
    }

    # ✅ Define valid timeframes
    valid_timeframes = ["5m", "15m", "30m", "1h", "4h", "1d"]

    # ✅ Validate instrument and timeframe
    if instrument not in symbol_map or timeframe not in valid_timeframes:
        print(f"❌ ERROR: Invalid instrument ({instrument}) or timeframe ({timeframe})")
        return None  

    symbol = symbol_map[instrument]
    period = "7d" if timeframe == "1d" else "5d"

    try:
        # ✅ Fetch market data
        data = yf.download(symbol, period=period, interval=timeframe)
        
        if data.empty:
            print(f"❌ ERROR: No data available for {instrument} ({timeframe}).")
            return None

        # ✅ Convert all data to float (force numeric conversion)
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors="coerce")

        # ✅ Drop rows with NaN values
        data.dropna(inplace=True)

        if data.empty:
            print(f"❌ ERROR: No valid numerical data available for {instrument} ({timeframe}).")
            return None

        # ✅ Save Chart
        chart_filename = f"static/{instrument.replace(' ', '_')}_{timeframe}.png"

        mpf.plot(
            data,
            type="candle",
            style="charles",
            ylabel="Price (USD)",
            savefig=chart_filename
        )

        print(f"✅ SUCCESS: Chart saved at {chart_filename}")
        return chart_filename

    except Exception as e:
        print(f"❌ ERROR: Failed to generate chart for {instrument} ({timeframe}). Exception: {e}")
        return None
