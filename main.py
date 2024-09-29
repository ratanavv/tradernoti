from binance.client import Client
import os

api_key = os.environ.get('B_API_KEY')
api_secret = os.environ.get('B_SECRET_KEY')

client = Client(api_key, api_secret)

import pandas as pd
import ta

def get_binance_data(symbol, interval='1h', limit=100):
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
                                       'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                       'taker_buy_quote_asset_volume', 'ignore'])
    df['close'] = df['close'].astype(float)
    return df

def calculate_indicators(df):
    # Calculate RSI (length=7)
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=7).rsi()

    # Calculate Stochastic RSI
    stochastic_rsi = ta.momentum.StochRSIIndicator(df['close'])
    df['stoch_k'] = stochastic_rsi.stochrsi_k()
    df['stoch_d'] = stochastic_rsi.stochrsi_d()

    return df

import time

def get_top_30_symbols():
    tickers = client.futures_ticker()
    # Sort tickers by volume and select the top 30
    sorted_tickers = sorted(tickers, key=lambda x: float(x['volume']), reverse=True)
    top_30_symbols = [ticker['symbol'] for ticker in sorted_tickers[:30]]
    return top_30_symbols

def check_conditions(df):
    # Define conditions for RSI and Stochastic RSI
    rsi_cross_up = (df['rsi'].iloc[-2] < 40) and (df['rsi'].iloc[-1] > 40)
    rsi_cross_down = (df['rsi'].iloc[-2] > 60) and (df['rsi'].iloc[-1] < 60)
    stoch_cross = (df['stoch_k'].iloc[-2] < df['stoch_d'].iloc[-2]) and (df['stoch_k'].iloc[-1] > df['stoch_d'].iloc[-1])

    return rsi_cross_up, rsi_cross_down, stoch_cross

def monitor_markets():
    symbols = get_top_30_symbols()
    for symbol in symbols:
        df = get_binance_data(symbol)
        df = calculate_indicators(df)
        rsi_up, rsi_down, stoch_cross = check_conditions(df)

        if rsi_up or rsi_down or stoch_cross:
            send_telegram_alert(symbol, rsi_up, rsi_down, stoch_cross)

        time.sleep(1)  # To avoid hitting rate limits

import requests

telegram_token = os.environ.get('telegram_token')
chat_id = os.environ.get('chat_id')

def send_telegram_alert(symbol, rsi_up, rsi_down, stoch_cross):
    message = f"Alert for {symbol}:\n"
    if rsi_up:
        message += "- RSI crossed up 40.\n"
    if rsi_down:
        message += "- RSI crossed down 60.\n"
    if stoch_cross:
        message += "- Stochastic RSI K and D lines crossover.\n"

    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    requests.post(url, json=payload)

# Run the monitoring function
while True:
    monitor_markets()
    time.sleep(300)  # Wait 5 minutes before running the check again



