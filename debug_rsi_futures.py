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
    markets = binance.load_markets()
    futures = [
        m for m in markets.values()
        if m.get('quote') == 'USDT'
        and m.get('contract', False)
        and m.get('active', True)
        and 'volume' in m.get('info', {})
    ]

    sorted_futures = sorted(futures, key=lambda x: float(x['info']['volume']), reverse=True)
    symbols = [m['symbol'] for m in sorted_futures[:5]]

    print("Top Futures Symbols by 24h Volume:", symbols)

    for sym in symbols:
        df = pd.DataFrame(fetch_ohlcv_safe(sym, '1h'), columns=["ts", "o", "h", "l", "c", "v"])
        if df.empty:
            print(f"[SKIP] No data for {sym}")
            continue
        df["rsi"] = RSIIndicator(df["c"], window=9).rsi()
        print(f"{sym} RSI1H: {df['rsi'].iloc[-1]:.2f}")

if __name__ == "__main__":
    main()