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
    print(f"🔍 DEBUG: Received columns for {instrument} ({timeframe}): {list(data.columns)}")

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
        return None  # Return None if invalid input

    symbol = symbol_map[instrument.lower()]
    yf_timeframe = valid_timeframes[timeframe]
    period = "7d" if timeframe == "1d" else "5d"

    # Fetch historical data
    try:
        data = yf.download(symbol, period=period, interval=yf_timeframe)
        
        if data.empty:
            print(f"No data available for {instrument} - {timeframe}")
            return None

        # ✅ Flatten multi-index column names if they exist
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = ['_'.join(col).strip() for col in data.columns.values]

        # ✅ Automatically rename any column that has an unexpected ticker suffix
     for col in data.columns:
         for key in ["Open", "High", "Low", "Close", "Volume"]:
             if col.startswith(key) and col != key:
                 data.rename(columns={col: key}, inplace=True)

        # ✅ Ensure numeric data and drop NaN rows
        for column in ["Open", "High", "Low", "Close", "Volume"]:
            if column in data.columns:
                data[column] = pd.to_numeric(data[column], errors="coerce")

        data.dropna(inplace=True)

        if data.empty:
            print(f"After cleaning, no valid data left for {instrument} - {timeframe}")
            return None

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

    # Delete old images before saving a new one
    delete_old_images()

    # ✅ Ensure required columns exist
    required_columns = ["Open", "High", "Low", "Close", "Volume"]
    missing_columns = [col for col in required_columns if col not in data.columns]

    if missing_columns:
    print(f"❌ ERROR: Missing columns {missing_columns} for {instrument} ({timeframe})")
    return None  # Stop if critical data is missing

    # Define Support & Resistance Zones
    high_price = data["High"].max()
    low_price = data["Low"].min()

    last_price = data["Close"].iloc[-1]  # Get last closing price

    support_zone = (low_price, low_price * 1.005)  # Support Zone (5% buffer)
    resistance_zone = (high_price * 0.995, high_price)  # Resistance Zone (5% buffer)

    # Define custom style for the chart
    mc = mpf.make_marketcolors(
        up="green", down="red", edge="green", wick="green", volume="blue"
    )
    s = mpf.make_mpf_style(
        marketcolors=mc, gridcolor="black", gridstyle="--", facecolor="#121212"  # Fully Dark Grey Background
    )

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(12, 6), facecolor="#121212")  # Fully Dark Grey Background
    ax.set_facecolor("#121212")  # Set same background inside the chart

    # Add Support & Resistance zones
    ax.axhspan(*support_zone, color="green", alpha=0.3, label="Buy Zone")  # Transparent Green
    ax.axhspan(*resistance_zone, color="red", alpha=0.3, label="Sell Zone")  # Transparent Red

    # Plot candlestick chart
    mpf.plot(
        data,
        type="candle",
        style=s,
        ax=ax,
        ylabel="Price (USD)",
    )

    # ✅ Fix Sell Candle Colors (Red Body + Red Wick + Red Outline)
    for i in range(len(data)):
        if data["Close"].iloc[i] < data["Open"].iloc[i]:  # Sell candle
            ax.plot([i, i], [data["Low"].iloc[i], data["High"].iloc[i]], color="red", linewidth=0.7)  # Wick
            ax.add_patch(plt.Rectangle((i-0.25, data["Open"].iloc[i]), 0.5, data["Close"].iloc[i] - data["Open"].iloc[i], color="red", ec="red"))

    # ✅ Set Both Left & Right Price Labels
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")

    ax.yaxis.tick_left()
    ax.yaxis.set_label_position("left")

    # ✅ Add More Detailed Price Scale (Every Pip, Readable)
    price_range = np.linspace(low_price, high_price, num=20)  # More price levels
    ax.set_yticks(price_range)  # Set more price levels
    ax.set_yticklabels([f"{price:.2f}" for price in price_range], color="white", fontsize=9)

    # ✅ Add Current Price Line (Thin Red Line)
    ax.axhline(y=last_price, color="red", linestyle="--", linewidth=1, label=f"Current Price: {last_price:.2f}")

    # ✅ Remove X-Axis (Date at Bottom)
    ax.set_xticklabels([])  # Hide X-Axis Dates
    ax.xaxis.set_visible(False)  # Ensure full removal

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
