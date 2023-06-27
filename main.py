from binance.client import Client
from historical import CryptoDataRetrieval
from crossover import Analyze
from knn import KNN
from trade import CryptoTrade
from datetime import datetime

def main():
    #Data Retrieval
    crypto_data = CryptoDataRetrieval('BTCUSDT', Client.KLINE_INTERVAL_1HOUR, datetime(2020, 1, 1), datetime(2022, 5, 20))
    crypto_data.data_retrieval()

    # KNN Accuracy 
    data_modifier = Analyze(file="bitcoin_data.csv")
    data_modifier.averages(7, 14)
    data_modifier.volume_calculation()
    data_modifier.ATR_calculation(14)
    data_modifier.calculate_rsi(14)
    data_modifier.drop_null()
    data_modifier.crossover_detection()
    data_modifier.ATR_trailing_stop_loss()
    data_modifier.save_as_csv("bitcoin_data_V4.csv")
    knn_accuracy = KNN(filename="bitcoin_data_V4.csv")
    preprocess = knn_accuracy.preprocess()
    model = knn_accuracy.model_train(preprocess[0], preprocess[2])
    knn_accuracy.evaluate(model, preprocess[1], preprocess[3])


    #Trade Identifier
    trade = CryptoTrade('BTCUSDT', Client.KLINE_INTERVAL_1WEEK, 15)
    trade.dataframe_creation()
    if trade.bullish_crossover(7, 14) == ("Bullish"): 
        trade_dataframe = trade.get_data_frame()
        dataframe_addition = Analyze(dataframe=trade_dataframe)
        dataframe_addition.averages(7, 14)
        dataframe_addition.calculate_rsi(14)
        dataframe_addition.volume_calculation()
        dataframe_addition.ATR_calculation(14)
        dataframe_addition.drop_null()
        data = dataframe_addition.get_dataframe()
        knn_prediction = KNN("bitcoin_data_V4.csv")
        trade_preprocess = knn_prediction.preprocess()
        model = knn_prediction.model_train(trade_preprocess[0], trade_preprocess[2])
        prediction = knn_prediction.predict(data, model)
        print(prediction)
    else:
        print("Neither")

if __name__ == "__main__":
    main()