
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
    tickers = binance.fetch_tickers()

    # Filter for true USDT perpetual futures
    symbols = []
    for symbol, market in markets.items():
        info = market.get('info', {})
        if (
            market.get('contract') 
            and market.get('future')
            and market.get('quote') == 'USDT' 
            and info.get('contractType') == 'PERPETUAL'
        ):
            ticker = tickers.get(symbol, {})
            vol = ticker.get('quoteVolume', 0)
            if vol:
                symbols.append((symbol, vol))

    # Sort by volume and pick top 5
    symbols = sorted(symbols, key=lambda x: x[1], reverse=True)[:5]
    top_symbols = [s for s, _ in symbols]
    print("Top Perpetual Futures Symbols:", top_symbols)

    # Fetch RSI for each
    for sym in top_symbols:
        df = pd.DataFrame(fetch_ohlcv_safe(sym, '1h'), columns=["ts","o","h","l","c","v"])
        if df.empty:
            print(f"[SKIP] {sym} no data")
            continue
        df["rsi"] = RSIIndicator(df["c"], window=9).rsi()
        print(f"{sym} RSI1H: {df['rsi'].iloc[-1]:.2f}")

if __name__ == "__main__":
    main()
