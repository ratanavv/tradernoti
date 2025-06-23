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

    # Filter USDT perpetual futures only
    symbols = []
    for symbol, ticker in tickers.items():
        if symbol not in markets:
            continue
    # Filter for perpetual futures ending in ':USDT' and exclude dated contracts
        if symbol.endswith(':USDT') and '-' not in symbol:
            market = markets[symbol]
        if (market.get('quote') == 'USDT' and market.get('contract') and market.get('future')):
            ticker_volume = ticker.get('quoteVolume', 0)
            if ticker_volume:
                symbols.append((symbol, ticker_volume))

    # Sort by volume descending and select top 5
    top_symbols = [s for s, _ in sorted(symbols, key=lambda x: x[1], reverse=True)[:5]]

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
