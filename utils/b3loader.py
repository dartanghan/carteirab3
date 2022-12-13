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
    with open('modelo_importacao.xlsx','rb') as file:
        return file.read()

def load_data(data):
    return pd.read_excel(data, engine="openpyxl")

def perform_operations( wallet_id:int, user_id:int, dataframe: any, db: Session):
    rows_to_process = [] # melhorar
    for i,row in dataframe.iterrows():
        rows_to_process.append(row.tolist())
    
    count = len(rows_to_process)
    while count > 0:
        count -= 1
        row = rows_to_process[count]
        print(row[1])
        if row[1] == 'Venda':
            stock = WalletStock(
                walletstock_pm= row[7],
                walletstock_qtt= row[6],
                walletstock_ticker= row[5],
                walletstock_buy_date=datetime.datetime.strptime(row[0], '%d/%m/%Y'),
                wallet_id= wallet_id
            )
            print(stock.walletstock_buy_date)
            try:
                obj = walletstocks_sell(db, wallet_id, stock,user_id)
            except Exception as e:
                print(e)
                raise
        else: 
            stock = {
                "walletstock_pm": row[7],
                "walletstock_qtt": row[6],
                "walletstock_ticker": row[5],
                "walletstock_buy_date": datetime.datetime.strptime(row[0], '%d/%m/%Y'),
                "wallet_id": wallet_id
            }
            obj = walletstocks_create(db,stock,user_id)
    return 1

