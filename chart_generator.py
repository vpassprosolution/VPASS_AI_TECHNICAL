import yfinance as yf
import mplfinance as mpf
import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import numpy as np
import time

# Ensure Matplotlib runs in non-GUI mode
import matplotlib
matplotlib.use("Agg")

# Ensure the 'static' directory exists
if not os.path.exists("static"):
    os.makedirs("static")

def delete_old_images():
    """Delete only images older than 10 minutes before saving a new one."""
    old_images = glob.glob("static/*.png")
    current_time = time.time()

    for image in old_images:
        if os.path.getmtime(image) < current_time - 600:  # 600 seconds = 10 minutes
            os.remove(image)

def generate_chart(instrument: str, timeframe: str):
    """Generates a candlestick chart for the selected instrument and timeframe."""
    
    # Define valid timeframes
    valid_timeframes = {
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1h",
        "4h": "1h",  # Yahoo does not have 4h, using 1h instead
        "1d": "1d",
    }

    # Yahoo Finance Symbol Mapping
    symbol_map = {
        "gold": "GC=F",
        "bitcoin": "BTC-USD",
        "ethereum": "ETH-USD",
        "dow jones": "^DJI",
        "nasdaq": "^IXIC",
        "eur/usd": "EURUSD=X",
        "gbp/usd": "GBPUSD=X"
    }

    if instrument.lower() not in symbol_map or timeframe not in valid_timeframes:
        print(f"❌ ERROR: Invalid instrument ({instrument}) or timeframe ({timeframe})")
        return None  # Return None if invalid input

    symbol = symbol_map[instrument.lower()]
    yf_timeframe = valid_timeframes[timeframe]
    period = "7d" if timeframe == "1d" else "5d"

    # Fetch historical data
    try:
        data = yf.download(symbol, period=period, interval=yf_timeframe)
        
        if data.empty:
            print(f"❌ ERROR: No data available for {instrument} ({timeframe}).")
            return None  # Stop execution if no data is available

        # ✅ Debug print: Show received columns
        print(f"🔍 DEBUG: Received columns for {instrument} ({timeframe}): {list(data.columns)}")

    except Exception as e:
        print(f"❌ ERROR: Failed to fetch market data for {instrument} ({timeframe}). Exception: {e}")
        return None

    # ✅ Ensure required columns exist
    required_columns = ["Open", "High", "Low", "Close", "Volume"]
    missing_columns = [col for col in required_columns if col not in data.columns]

    if missing_columns:
        print(f"❌ ERROR: Missing columns {missing_columns} for {instrument} ({timeframe})")
        return None  # Stop if critical data is missing

    # Delete old images before saving a new one
    delete_old_images()

    # Define Support & Resistance Zones
    high_price = data["High"].max()
    low_price = data["Low"].min()
    last_price = data["Close"].iloc[-1]  # Get last closing price

    support_zone = (low_price, low_price * 1.005)  # Support Zone (0.5% buffer)
    resistance_zone = (high_price * 0.995, high_price)  # Resistance Zone (0.5% buffer)

    # Define custom style for the chart
    mc = mpf.make_marketcolors(
        up="green", down="red", edge="green", wick="green", volume="blue"
    )
    s = mpf.make_mpf_style(
        marketcolors=mc, gridcolor="black", gridstyle="--", facecolor="#121212"
    )

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(12, 6), facecolor="#121212")
    ax.set_facecolor("#121212")

    # Add Support & Resistance zones
    ax.axhspan(*support_zone, color="green", alpha=0.3, label="Buy Zone")
    ax.axhspan(*resistance_zone, color="red", alpha=0.3, label="Sell Zone")

    # Plot candlestick chart
    mpf.plot(
        data,
        type="candle",
        style=s,
        ax=ax,
        ylabel="Price (USD)",
    )

    # ✅ Add Current Price Line (Thin Red Line)
    ax.axhline(y=last_price, color="red", linestyle="--", linewidth=1, label=f"Current Price: {last_price:.2f}")

    # ✅ Remove X-Axis (Date at Bottom)
    ax.set_xticklabels([])
    ax.xaxis.set_visible(False)

    # Set title
    plt.title(
        f"{instrument.upper()} ({symbol}) {timeframe} Chart with Support & Resistance",
        fontsize=14, fontweight="bold", color="white"
    )

    # Save the chart
    chart_filename = f"static/{instrument}_{timeframe}.png"
    plt.savefig(chart_filename, facecolor="#121212", bbox_inches="tight", dpi=100)
    plt.close(fig)  # Close plot to free memory

    return chart_filename
