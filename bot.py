import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from taapi import TAAPIClient

# Initialize TAAPI client
taapi = TAAPIClient(api_key='YOUR_TAAPI_API_KEY')

# Function to get top 30 trading pairs by volume
def get_top_30_pairs():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url)
    data = response.json()
    sorted_pairs = sorted(data, key=lambda x: float(x['quoteVolume']), reverse=True)
    top_30_pairs = [pair['symbol'] for pair in sorted_pairs[:30]]
    return top_30_pairs

# Function to check indicators for each pair
def check_indicators():
    top_30_pairs = get_top_30_pairs()
    alerts = []
    for pair in top_30_pairs:
        rsi = taapi.get_indicator('rsi', symbol=pair, interval='1h', optInTimePeriod=7)
        stoch_rsi = taapi.get_indicator('stochrsi', symbol=pair, interval='1h')
        if 40 < rsi['value'] < 60 and stoch_rsi['k'] > stoch_rsi['d']:
            alerts.append(pair)
    return alerts

# Alert function for the bot
def alert(update: Update, context: CallbackContext) -> None:
    alerts = check_indicators()
    if alerts:
        update.message.reply_text(f'Trade indicators met criteria for: {", ".join(alerts)}')
    else:
        update.message.reply_text('No trade indicators met criteria.')

def main():
    # Initialize bot
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")
    dispatcher = updater.dispatcher

    # Add command handler
    dispatcher.add_handler(CommandHandler("alert", alert))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
