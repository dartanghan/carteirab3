'''
Arquivo com a lógica para importação do extrato da B3
'''
import pandas as pd
from utils.models import (
    wallet_get,
    walletstocks_create,
    walletstocks_sell,
    WalletStock
)
from sqlalchemy.orm import Session
import datetime


def load_file():
    with open('modelo_importacao.xlsx', 'rb') as file:
        return file.read()


def load_data(data):
    return pd.read_excel(data, engine="openpyxl")


def perform_operations(wallet_id: int, user_id: int, dataframe: any, db: Session):
    _operations = {}  # melhorar
    for i, row in dataframe.iterrows():
        try:
            data_operacao = datetime.datetime.strptime(row.tolist()[0], '%d/%m/%Y')
            if data_operacao not in _operations:
                _operations[data_operacao]:list=[]
            _operations[data_operacao].append(row.tolist())
        except Exception as exce:
            print(exce)
    _operations_keys_ordered = sorted(_operations)
    for _data_oper in _operations_keys_ordered:
        print(f'Processando operacoes de {_data_oper}')
        for _operacao in _operations[_data_oper]:
            try:
                if _operacao[1] == 'Venda':
                    stock = WalletStock(
                        walletstock_pm=_operacao[7],
                        walletstock_qtt=_operacao[6],
                        walletstock_ticker=_operacao[5],
                        walletstock_buy_date=datetime.datetime.strptime(
                            _operacao[0], '%d/%m/%Y'),
                        wallet_id=wallet_id
                    )
                    obj = walletstocks_sell(db, wallet_id, stock, user_id)
                else:
                    stock = {
                        "walletstock_pm": _operacao[7],
                        "walletstock_qtt": _operacao[6],
                        "walletstock_ticker": _operacao[5],
                        "walletstock_buy_date": datetime.datetime.strptime(_operacao[0], '%d/%m/%Y'),
                        "wallet_id": wallet_id
                    }
                    obj = walletstocks_create(db, stock, user_id)
            except Exception as e:
                print(e)


    # rows_to_process = []  # melhorar
    # for i, row in dataframe.iterrows():
    #     try:
    #         data_operacao = datetime.datetime.strptime(row.tolist()[0], '%d/%m/%Y')
    #         rows_to_process.append(row.tolist())
    #     except Exception as e:
    #         print(e)

    
    # print(rows_to_process)
    # rows_to_process = sorted(rows_to_process, key=lambda x:x[0])
    # print(rows_to_process)
    # count = len(rows_to_process)
    # while count > 0:
    #     count -= 1
    #     row = rows_to_process[count]
    #     print(row[1])
    #     if row[1] == 'Venda':
    #         stock = WalletStock(
    #             walletstock_pm=row[7],
    #             walletstock_qtt=row[6],
    #             walletstock_ticker=row[5],
    #             walletstock_buy_date=datetime.datetime.strptime(
    #                 row[0], '%d/%m/%Y'),
    #             wallet_id=wallet_id
    #         )
    #         print(stock.walletstock_buy_date)
    #         try:
    #             obj = walletstocks_sell(db, wallet_id, stock, user_id)
    #         except Exception as e:
    #             print(e)
    #     else:
    #         stock = {
    #             "walletstock_pm": row[7],
    #             "walletstock_qtt": row[6],
    #             "walletstock_ticker": row[5],
    #             "walletstock_buy_date": datetime.datetime.strptime(row[0], '%d/%m/%Y'),
    #             "wallet_id": wallet_id
    #         }
    #         obj = walletstocks_create(db, stock, user_id)
    # return 1
