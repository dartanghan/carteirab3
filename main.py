from datetime import date, datetime

from fastapi import FastAPI, Depends, FastAPI, HTTPException,Response
from sqlalchemy.orm import Session
from utils import models, dbutils
from utils.finance import get_current_value_from_stocks,get_dividends_from_stocks
from utils.security import signJWT,decodeJWT

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
    user = models.user_login(db,user['user_email'],user['user_password'])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return signJWT(user)


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
    models.user_delete(db,db_user)
    return models.user_get(db, user["id"])

@app.post("/users/")
def create_user(user: dict, db: Session = Depends(get_db)):
    db_user = models.user_get_by_email(db, user["user_email"])
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return models.user_create(db=db, user=user)

@app.get("/wallets/")
def read_wallets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    users = models.wallet_list(db,token["user_id"],skip=skip, limit=limit)
    return users

@app.get("/wallets/{wallet_id}")
def read_wallets(wallet_id: int, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    item = models.wallet_get(db, wallet_id,token["user_id"])
    return item

@app.post("/wallets/")
def create_wallet(data: dict, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    print(token)
    data["user_id"]=token["user_id"]
    db_item = models.wallet_get_by_user_and_wallet_name(db, data["wallet_name"],token["user_id"])
    if db_item:
        raise HTTPException(status_code=400, detail="Wallet already registered")
    return models.wallet_create(db,data)

@app.delete("/wallets/")
def delete_wallets(data: dict, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    print(token)
    db_item = models.wallet_get(db, data["id"],token["user_id"])
    if not db_item:
        raise HTTPException(status_code=404, detail="Wallet not found")
    models.wallet_delete(db,db_item)
    return {"detail": "Ok"}

@app.put("/wallets/stocks/{walletstock_id}")
def update_wallet(walletstock_id: int, data: dict, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    print(token)
    data["walletstock_buy_date"]= datetime.strptime(data["walletstock_buy_date"],"%Y-%m-%d") #TODO automatizar conversao data
    db_item = models.walletstocks_update(db, walletstock_id, data, token["user_id"])
    if not db_item or not db_item.id:
        raise HTTPException(status_code=400, detail="WalletStock not found")
    return db_item

@app.get("/wallets/stocks/")
def read_walletstocks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    users = models.walletstocks_list(db, token["user_id"], skip=skip, limit=limit)
    return users

@app.get("/wallets/stocks/{id}")
def read_walletstocks(id: int, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    ob = models.walletstocks_get(db, id, token["user_id"])
    return ob

@app.post("/wallets/stocks/")
def create_walletstocks(data: dict, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    obj = models.walletstocks_create(db,data,token["user_id"])
    return obj if obj else HTTPException(status_code=500, detail="Creation failed")

@app.delete("/wallets/stocks/")
def delete_walletstocks(data: dict, db: Session = Depends(get_db), token: str = Depends(decodeJWT)):
    db_item = models.walletstocks_get(db, data["id"],token["user_id"])
    if not db_item:
        raise HTTPException(status_code=404, detail="WalletStock not found")
    models.walletstocks_delete(db,db_item)
    return {"detail": "Ok"}

@app.get("/wallets/performance/{id}")
def get_wallet_performance(id: int, db: Session = Depends(get_db)):
    """Retorna a performance da carteira questionada
    
    Retorna a performance da carteira questionada:
    - Valor atual
    - Valor investido
    - % Rentabilidade
    - Dividendos recebidos

    :param id:int id da carteira
    """
    retorno = {
        "curr_value":0,
        "paid_value":0,
        "dividends":0,
    }
    wallet = models.wallet_get(db, id)
    retorno["curr_value"]=get_current_value_from_stocks(wallet.stocks)
    retorno["paid_value"]=[retorno["paid_value"]+st.walletstock_qtt*st.walletstock_pm for st in wallet.stocks][0]
    retorno["dividends"]=get_dividends_from_stocks(wallet.stocks)
    return retorno



@app.get("/")
def read_root():
    return {"Hello": "World"}

