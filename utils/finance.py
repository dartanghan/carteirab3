"""
Utilitario financeiro
- Pega os dados do YahooFinance
"""
from datetime import datetime
import yfinance as yf
import pandas as pd



def get_current_price(ticker:str) -> float:
    """Retorna o preco atual de um ticker

    Retorna o preco atual de um ticker

    :param ticker:str nome do ticker
    :return float valor atual do ticker
    """
    tk = yf.Ticker(ticker)
    return tk.info['currentPrice'] if 'currentPrice' in tk.info else 0

def get_current_value_from_stocks(walletstocks:list) -> float:
    """Calcula o valor atual da uma lista de stocks desejada

    Calcula o valor atual da uma lista de stocks desejada. Pode ser 
    usada para projeção ou para calcular uma carteira.

    :param walletstocks:list Lista de stocks para calcular
    :return float valor atual
    """
    curr_value=0.0
    for stock in walletstocks:
        curr_value += get_current_price(stock.walletstock_ticker) \
            * stock.walletstock_qtt
    return curr_value

def get_dividends_from_stocks(walletstocks:list) -> float:
    """Calcula o valor de dividendos da uma lista de stocks desejada

    Calcula o valor de dividendos da uma lista de stocks desejada. Pode ser 
    usada para projeção ou para calcular uma carteira.

    :param walletstocks:list Lista de stocks para calcular
    :return float valor atual
    """
    retorno = 0
    for stock in walletstocks:
        try:
            tk = yf.Ticker(stock.walletstock_ticker)
            dividends = pd.DataFrame.from_dict(tk.dividends)
            #dividends.sort_values(by="Date")
            values = dividends[stock.walletstock_buy_date:datetime.now().strftime("%Y-%m-%d")]
            print(values)
            for val in values.loc[:,"Dividends"]: #certo seria pegar a coluna...
                retorno += float(val)
        except Exception as e:
            print(f' [X] Error occuried {e}')
    return retorno