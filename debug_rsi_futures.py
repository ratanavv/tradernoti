import ccxt
import time
import pandas as pd
from ta.momentum import RSIIndicator

# Initialize Binance futures via CCXT
binance = ccxt.binance({
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

def fetch_ohlcv_safe(symbol, timeframe='1h', limit=100):
    try:
        time.sleep(1.0)
        return binance.fetch_ohlcv(symbol, timeframe, limit=limit)
    except Exception as e:
        print(f"[ERROR] {symbol}: {e}")
        return []

def main():
    markets = binance.load_markets()
    tickers = binance.fetch_tickers()

    # Filter true USDT futures markets via CCXT properties
    futures_markets = [
        m for m in markets.values()
        if m.get('future') is True
        and m.get('spot') is False
        and m.get('quote') == 'USDT'
    ]

    # Build list of (symbol, quoteVolume) pairs
    vol_list = []
    for m in futures_markets:
        symbol = m['symbol']
        ticker = tickers.get(symbol, {})
        vol = ticker.get('quoteVolume')
        if vol:
            vol_list.append((symbol, vol))

    # Sort by descending volume, take top 5
    top_symbols = [s for s, _ in sorted(vol_list, key=lambda x: x[1], reverse=True)[:5]]
    print("Top Futures Symbols by 24h Volume:", top_symbols)

    for sym in top_symbols:
        df = pd.DataFrame(fetch_ohlcv_safe(sym, '1h'), columns=["ts", "o", "h", "l", "c", "v"])
        if df.empty:
            print(f"[SKIP] No data for {sym}")
            continue
        df["rsi"] = RSIIndicator(df["c"], window=9).rsi()
        print(f"{sym} RSI1H: {df['rsi'].iloc[-1]:.2f}")

if __name__ == "__main__":
    main()