from bot import start_bot, trade_identifier
from binance.client import Client
from historical import CryptoDataRetrieval
from crossover import Analyze
from knn import KNN
from trade import CryptoTrade
from datetime import datetime
import subprocess
import time

import asyncio
symbol = 'BTCUSDT'
short_period = 7
long_period = 14
#Data Retrieval
def data_retrieval():
    crypto_data = CryptoDataRetrieval(symbol, Client.KLINE_INTERVAL_1HOUR, datetime(2020, 1, 1), datetime(2022, 5, 20))
    crypto_data.data_retrieval()

# KNN Accuracy 
def knn_evaluation():
    data_modifier = Analyze(file="bitcoin_data.csv")
    data_modifier.averages(short_period, long_period)
    data_modifier.volume_calculation()
    data_modifier.ATR_calculation(long_period)
    data_modifier.calculate_rsi(long_period)
    data_modifier.drop_null()
    data_modifier.crossover_detection()
    data_modifier.ATR_trailing_stop_loss()
    data_modifier.save_as_csv("bitcoin_data_V4.csv")
    knn_accuracy = KNN(filename="bitcoin_data_V4.csv")
    preprocess = knn_accuracy.preprocess()
    model = knn_accuracy.model_train(preprocess[0], preprocess[2])
    knn_accuracy.evaluate(model, preprocess[1], preprocess[3])

def indicator():
    #Trade Identifier
    trade = CryptoTrade(symbol, Client.KLINE_INTERVAL_1WEEK, long_period + 1)
    trade.dataframe_creation()
    if trade.bullish_crossover(short_period, long_period) == ("Bullish"): 
        trade_dataframe = trade.get_data_frame()
        dataframe_addition = Analyze(dataframe=trade_dataframe)
        dataframe_addition.averages(short_period, long_period)
        dataframe_addition.calculate_rsi(long_period)
        dataframe_addition.volume_calculation()
        dataframe_addition.ATR_calculation(long_period)
        dataframe_addition.drop_null()
        data = dataframe_addition.get_dataframe()
        # print(data)
        knn_prediction = KNN("bitcoin_data_V4.csv")
        trade_preprocess = knn_prediction.preprocess()
        model = knn_prediction.model_train(trade_preprocess[0], trade_preprocess[2])
        prediction = knn_prediction.predict(data, model)
        return(str(prediction[0]))
    else:
        return("Neither")
    
async def periodic_notification():
    while True:
        current_time = datetime.now()
        if current_time.hour == 0:
            result = indicator()
            await (trade_identifier(result, symbol))
        await asyncio.sleep(1)

async def start():
    bot_start = asyncio.create_task(start_bot())
    await asyncio.sleep(1)
    message = asyncio.create_task(periodic_notification())
    await asyncio.gather(bot_start, message)

def check_internet_connection():
    while True:
        try:
            response = subprocess.run(['ping', '-n', '1', 'google.com'], capture_output=True)
            if response.returncode == 0:
                print("Connected to the internet.")
                return True
            else:
                print("No internet connection. Retrying in 5 seconds...")
                time.sleep(5)
                continue
        except subprocess.CalledProcessError:
            print("No internet connection. Retrying in 5 seconds...")
            time.sleep(5)
            return False


def main():
    if not check_internet_connection():
        print("Cannot establish internet connection. Exiting...")
        return
    asyncio.run(start())

if __name__ == "__main__":
    main()