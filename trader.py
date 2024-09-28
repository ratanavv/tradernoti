pip install python-binance pandas numpy ta python-telegram-bot

import pandas as pd
import numpy as np
import talib
from ta.momentum import RSIIndicator, StochRSIIndicator
from binance.client import Client
from binance.enums import *
from telegram import Bot
import time

# Binance and Telegram API credentials
import os
BINANCE_API_KEY = os.environ.get('binance_api')
BINANCE_SECRET_KEY = os.environ.get('binance_secret')
TELEGRAM_TOKEN = os.environ.get('telegram_token')
TELEGRAM_CHAT_ID = os.environ.get('chat_id')

# Initialize Binance and Telegram clients
client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
bot = Bot(token=TELEGRAM_TOKEN)

def get_top_30_pairs():
    # Get futures tickers sorted by volume
    tickers = client.futures_ticker()
    sorted_tickers = sorted(tickers, key=lambda x: float(x['volume']), reverse=True)
    top_30 = [t['symbol'] for t in sorted_tickers[:30]]
    return top_30

def get_ohlcv(symbol, interval='1h', limit=200):
    # Fetch OHLCV data for the given symbol
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
                                       'quote_asset_volume', 'num_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
    df['close'] = df['close'].astype(float)
    return df

def check_rsi_conditions(df):
    # Calculate RSI (length 7)
    rsi = RSIIndicator(df['close'], window=7).rsi()
    current_rsi = rsi.iloc[-1]
    
    if current_rsi > 40 and current_rsi < 60:
        return True, current_rsi
    return False, current_rsi

def check_stochastic_rsi(df):
    # Calculate Stochastic RSI
    stoch_rsi = StochRSIIndicator(df['close'], window=14, smooth1=3, smooth2=3)
    k = stoch_rsi.stochrsi_k().iloc[-2:]
    d = stoch_rsi.stochrsi_d().iloc[-2:]
    
    if k.iloc[-1] > d.iloc[-1] and k.iloc[-2] < d.iloc[-2]:
        return True, k.iloc[-1], d.iloc[-1]
    return False, k.iloc[-1], d.iloc[-1]

def send_notification(message):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def main():
    while True:
        try:
            top_30_pairs = get_top_30_pairs()
            
            for symbol in top_30_pairs:
                df = get_ohlcv(symbol)
                
                # Check RSI conditions
                rsi_condition_met, rsi_value = check_rsi_conditions(df)
                
                # Check Stochastic RSI conditions
                stoch_condition_met, k, d = check_stochastic_rsi(df)
                
                if rsi_condition_met:
                    message = f"{symbol}: RSI (7) is between 40 and 60. Current RSI: {rsi_value:.2f}"
                    send_notification(message)
                
                if stoch_condition_met:
                    message = f"{symbol}: Stochastic RSI %K crossed above %D. %K: {k:.2f}, %D: {d:.2f}"
                    send_notification(message)
            
            # Sleep for 10 minutes before next check
            time.sleep(10 * 60)
        
        except Exception as e:
            # Log any errors and continue
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
