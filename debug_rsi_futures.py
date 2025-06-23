import ccxt
import time
import pandas as pd
from ta.momentum import RSIIndicator

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
    markets = binance.fetch_markets()
    futures = [
        m for m in markets
        if m.get('quote') == 'USDT'
        and m.get('contract', False)
        and m.get('active', False) == False
    ]

    sorted_markets = sorted(futures, key=lambda x: x.get('quoteVolume', 0), reverse=True)
    symbols = [m['symbol'] for m in sorted_markets[:5]]

    print("Top Futures Symbols:", symbols)

    for sym in symbols:
        try:
            df = pd.DataFrame(fetch_ohlcv_safe(sym, '1h'), columns=["ts", "o", "h", "l", "c", "v"])
            if df.empty:
                print(f"[SKIP] No data for {sym}")
                continue
            df["rsi"] = RSIIndicator(df["c"], window=9).rsi()
            print(f"{sym} RSI1H: {df['rsi'].iloc[-1]:.2f}")
        except Exception as e:
            print(f"[FAIL] {sym}: {e}")

if __name__ == "__main__":
    main()