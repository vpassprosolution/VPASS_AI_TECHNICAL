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
    """Generates and saves a chart based on instrument and timeframe."""
    
    # Define Yahoo Finance symbols
    symbol_map = {
        "gold": "GC=F",
        "bitcoin": "BTC-USD",
        "ethereum": "ETH-USD",
        "dow jones": "^DJI",
        "nasdaq": "^IXIC",
        "eur/usd": "EURUSD=X",
        "gbp/usd": "GBPUSD=X"
    }
    
    # Define valid timeframes
    valid_timeframes = {
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1h",
        "4h": "1h",  # Yahoo does not support 4H, using 1H instead
        "1d": "1d"
    }

    # Validate instrument and timeframe
    if instrument.lower() not in symbol_map or timeframe not in valid_timeframes:
        print(f"❌ ERROR: Invalid instrument ({instrument}) or timeframe ({timeframe})")
        return None  

    symbol = symbol_map[instrument.lower()]
    yf_timeframe = valid_timeframes[timeframe]
    period = "7d" if timeframe == "1d" else "5d"

    try:
        # Fetch historical data
        data = yf.download(symbol, period=period, interval=yf_timeframe)
        
        if data.empty:
            print(f"❌ ERROR: No data available for {instrument} ({timeframe}).")
            return None

        # ✅ Ensure correct column names
        required_columns = ["Open", "High", "Low", "Close", "Volume"]
        missing_columns = [col for col in required_columns if col not in data.columns]

        if missing_columns:
            print(f"❌ ERROR: Missing columns {missing_columns} for {instrument} ({timeframe})")
            return None

        # ✅ Generate and Save Chart
        chart_filename = f"static/{instrument}_{timeframe}.png"

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
