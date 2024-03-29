from datetime import date, datetime

from fastapi import FastAPI, Depends, FastAPI, HTTPException, UploadFile
from sqlalchemy.orm import Session
from utils import models, dbutils
from utils.finance import get_current_value_from_stocks, get_dividends_from_stocks
from utils.security import signJWT, decodeJWT

dbutils.Base.metadata.create_all(bind=dbutils.engine)
app = FastAPI()


def get_db():
    db = dbutils.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/login")
def login(user: dict, db: Session = Depends(get_db)):
    user = models.user_login(db, user['user_email'], user['user_password'])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return signJWT(user)

# Users
####################################################################


@app.get("/users/")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = models.user_list(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}")
def read_users(user_id: int, db: Session = Depends(get_db)):
    users = models.user_get(db, user_id)
    return users


@app.delete("/users/")
def delete_user(user: dict, db: Session = Depends(get_db)):
    db_user = models.user_get(db, user["id"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    models.user_delete(db, db_user)
    return models.user_get(db, user["id"])


@app.post("/users/")
def create_user(user: dict, db: Session = Depends(get_db)):
    db_user = models.user_get_by_email(db, user["user_email"])
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return models.user_create(db=db, user=user)

# Wallet
####################################################################


@app.get("/wallets/")
def list_wallets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    ob = models.wallet_list(db, token["user_id"], skip=skip, limit=limit)
    return ob


@app.get("/wallets/{wallet_id}")
def read_wallets(wallet_id: int, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    ob = models.wallet_get(db, wallet_id, token["user_id"])
    if not ob:
        raise HTTPException(
            status_code=404, detail="WalletStockHistory not found")
    return ob


@app.post("/wallets/")
def create_wallet(data: dict, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    print(token)
    data["user_id"] = token["user_id"]
    db_item = models.wallet_get_by_user_and_wallet_name(
        db, data["wallet_name"], token["user_id"])
    if db_item:
        raise HTTPException(
            status_code=400, detail="Wallet already registered")
    return models.wallet_create(db, data)


@app.delete("/wallets/")
def delete_wallets(data: dict, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    print(token)
    db_item = models.wallet_get(db, data["id"], token["user_id"])
    if not db_item:
        raise HTTPException(status_code=404, detail="Wallet not found")
    models.wallet_delete(db, db_item)
    return {"detail": "Ok"}

# WalletStocks
####################################################################


@app.put("/wallets/stocks/{walletstock_id}")
def update_wallet(walletstock_id: int, data: dict, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    data["walletstock_buy_date"] = datetime.strptime(
        data["walletstock_buy_date"], "%Y-%m-%d")  # TODO automatizar conversao data
    db_item = models.walletstocks_update(
        db, walletstock_id, data, token["user_id"])
    if not db_item or not db_item.id:
        raise HTTPException(status_code=400, detail="WalletStock not found")
    return db_item


@app.post("/wallets/stocks/sell/{wallet_id}")
def sell_wallet_stock(wallet_id: int, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    print(token)  # TODO permitir vender parcial...
    db_item = models.walletstocks_get(db, wallet_id, token["user_id"])
    if not db_item or not db_item.id:
        raise HTTPException(status_code=400, detail="WalletStock not found")
    return models.walletstocks_sell(db, wallet_id, db_item, token["user_id"])


@app.get("/wallets/stocks/")
def list_walletstocks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    ob = models.walletstocks_list(db, token["user_id"], skip=skip, limit=limit)
    return ob


@app.get("/wallets/stocks/{id}")
def read_walletstocks(id: int, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    ob = models.walletstocks_get(db, id, token["user_id"])
    if not ob:
        raise HTTPException(status_code=404, detail="WalletStock not found")
    return ob

@app.get("/wallets/{id}/consolidado")
def read_wallet_consolidado(id: int, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    retorno:dict = {}
    print(id)
    ob = models.wallet_get(db, id, token["user_id"])
    for stock in ob.stocks:
        print(stock)
        if stock.walletstock_ticker not in retorno:
            retorno[stock.walletstock_ticker] = {
                "walletstock_pm": stock.walletstock_pm,
                "walletstock_qtt": stock.walletstock_qtt,
                "walletstock_ticker": stock.walletstock_ticker,
                "walletstock_buy_date": stock.walletstock_buy_date,
                "wallet_id": stock.wallet_id
            }
        else:
            _s_qtt=stock.walletstock_qtt+retorno[stock.walletstock_ticker]["walletstock_qtt"]
            _s_pm=(retorno[stock.walletstock_ticker]["walletstock_qtt"]*retorno[stock.walletstock_ticker]["walletstock_pm"])
            _s_pm=_s_pm+stock.walletstock_qtt*stock.walletstock_pm
            retorno[stock.walletstock_ticker]["walletstock_qtt"]=_s_qtt
            retorno[stock.walletstock_ticker]["walletstock_pm"]=_s_pm/_s_qtt
    print (retorno)
    if not ob:
        raise HTTPException(status_code=404, detail="WalletStock not found")
    return retorno

@app.post("/wallets/stocks/")
def create_walletstocks(data: dict, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    obj = models.walletstocks_create(db, data, token["user_id"])
    return obj if obj else HTTPException(status_code=500, detail="Creation failed")


@app.delete("/wallets/stocks/")
def delete_walletstocks(data: dict, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    db_item = models.walletstocks_get(db, data["id"], token["user_id"])
    if not db_item:
        raise HTTPException(status_code=404, detail="WalletStock not found")
    models.walletstocks_delete(db, db_item)
    return {"detail": "Ok"}

# WalletStocksHistory
####################################################################


@app.get("/wallets/stocks/history/")
def list_walletstockshistory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    ob = models.walletstockshistory_list(
        db, token["user_id"], skip=skip, limit=limit)
    return ob


@app.get("/wallets/stocks/history/{id}")
def read_walletstockshistory(id: int, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    ob = models.walletstockshistory_get(db, id, token["user_id"])
    if not ob:
        raise HTTPException(
            status_code=404, detail="WalletStockHistory not found")
    return ob


@app.delete("/wallets/stocks/history/{id}")
def delete_walletstockshistory(id: int, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    db_item = models.walletstockshistory_get(db, id, token["user_id"])
    if not db_item:
        raise HTTPException(
            status_code=404, detail="WalletStockHistory not found")
    models.walletstockshistory_delete(db, db_item)
    return {"detail": "Ok"}


@app.get("/wallets/performance/{id}")
def get_wallet_performance(id: int, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    """Retorna a performance da carteira questionada

    Retorna a performance da carteira questionada:
    - Valor atual
    - Valor investido
    - % Rentabilidade
    - Dividendos recebidos

    :param id:int id da carteira
    """
    retorno = {
        "curr_value": 0,
        "paid_value": 0,
        "dividends": 0,
    }
    wallet = models.wallet_get(db, id, token["user_id"])
    retorno["curr_value"] = get_current_value_from_stocks(wallet.stocks)
    retorno["paid_value"] = [retorno["paid_value"] +
                             st.walletstock_qtt*st.walletstock_pm for st in wallet.stocks][0]
    retorno["dividends"] = get_dividends_from_stocks(wallet.stocks)
    return retorno


@app.post("/b3loader/{wallet_id}")
def load_b3(file: UploadFile, wallet_id: int, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    """Importa o extrato de negociacao do B3Investidor

    """
    from utils.b3loader import load_data, load_file, perform_operations
    dados = file.file.read()
    dataframe = load_data(dados)
    perform_operations(wallet_id, token["user_id"], dataframe, db)
    return {"detail": "OK"}


@app.get("/b3test")
def b3test(db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    return 'OK'


@app.get("/")
def read_root():
    return {"Hello": "World"}
