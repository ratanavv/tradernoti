import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from binance.client import Client

# Initialize Binance client
binance_api_key = 'H2zuWdkpm7tyUFnBOZRwj29tFfXrBXXgm7gsu3p4kqFR7EkW38PvODdJt2B1WqVv'
binance_api_secret = 'Rrv5MtPfpxekKDoAVaKqklGipxk2I83Fr6XNJsFHscBqP52MYeLO4FomfbZmVzKl'
client = Client(binance_api_key, binance_api_secret)

# Function to get top 30 futures trading pairs by volume
def get_top_30_pairs():
    tickers = client.futures_ticker()
    sorted_pairs = sorted(tickers, key=lambda x: float(x['quoteVolume']), reverse=True)
    top_30_pairs = [pair['symbol'] for pair in sorted_pairs[:30]]
    return top_30_pairs

# Function to check indicators for each pair
def check_indicators():
    top_30_pairs = get_top_30_pairs()
    alerts = []
    for pair in top_30_pairs:
        klines = client.futures_klines(symbol=pair, interval=Client.KLINE_INTERVAL_1HOUR, limit=14)
        closes = [float(kline[4]) for kline in klines]
        rsi = calculate_rsi(closes, 7)
        stoch_rsi_k, stoch_rsi_d = calculate_stoch_rsi(closes)
        if 40 < rsi < 60 and stoch_rsi_k > stoch_rsi_d:
            alerts.append(pair)
    return alerts

# Function to calculate RSI
def calculate_rsi(closes, period):
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Function to calculate Stochastic RSI
def calculate_stoch_rsi(closes):
    min_close = min(closes)
    max_close = max(closes)
    stoch_rsi_k = 100 * (closes[-1] - min_close) / (max_close - min_close)
    stoch_rsi_d = sum([100 * (closes[i] - min_close) / (max_close - min_close) for i in range(-3, 0)]) / 3
    return stoch_rsi_k, stoch_rsi_d

# Alert function for the bot
def alert(update: Update, context: CallbackContext) -> None:
    alerts = check_indicators()
    if alerts:
        update.message.reply_text(f'Trade indicators met criteria for: {", ".join(alerts)}')
    else:
        update.message.reply_text('No trade indicators met criteria.')

def main():
    # Initialize bot
    updater = Updater("7733779461:AAGQG4bw5u75tjaezh8EkBicS-rHAaoKRXQ")
    dispatcher = updater.dispatcher

    # Add command handler
    dispatcher.add_handler(CommandHandler("alert", alert))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
