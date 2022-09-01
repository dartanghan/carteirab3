from fastapi import FastAPI, Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from utils import models, dbutils

dbutils.Base.metadata.create_all(bind=dbutils.engine)
app = FastAPI()

def get_db():
    db = dbutils.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = models.user_list(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}")
def read_users(user_id: int, db: Session = Depends(get_db)):
    users = models.user_get(db, user_id)
    return users

@app.post("/users/")
def create_user(user: dict, db: Session = Depends(get_db)):
    db_user = models.user_get_by_email(db, user["user_email"])
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return models.user_create(db=db, user=user)

@app.delete("/users/")
def delete_user(user: dict, db: Session = Depends(get_db)):
    db_user = models.user_get(db, user["id"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    models.user_delete(db,db_user)
    return models.user_get(db, user["id"])

@app.get("/wallets/")
def read_wallets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = models.wallet_list(db, skip=skip, limit=limit)
    return users

@app.post("/wallets/")
def create_wallet(data: dict, db: Session = Depends(get_db)):
    db_item = models.wallet_get_by_user_and_wallet_name(db, data["wallet_name"], data["user_id"])
    if db_item:
        raise HTTPException(status_code=400, detail="Wallet already registered")
    return models.wallet_create(db,data)

@app.delete("/wallets/")
def delete_wallets(data: dict, db: Session = Depends(get_db)):
    db_item = models.wallet_get(db, data["id"])
    if not db_item:
        raise HTTPException(status_code=404, detail="Wallet not found")
    models.wallet_delete(db,db_item)
    return models.wallet_get(db, data["id"])

@app.get("/wallets/stocks/")
def read_walletstocks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = models.walletstocks_list(db, skip=skip, limit=limit)
    return users

@app.get("/wallets/stocks/{id}")
def read_walletstocks(id: int, db: Session = Depends(get_db)):
    ob = models.walletstocks_get(db, id)
    return ob

@app.post("/wallets/stocks/")
def create_walletstocks(data: dict, db: Session = Depends(get_db)):
    return models.walletstocks_create(db,data)

@app.delete("/wallets/stocks/")
def delete_walletstocks(data: dict, db: Session = Depends(get_db)):
    db_item = models.walletstocks_get(db, data["id"])
    if not db_item:
        raise HTTPException(status_code=404, detail="WalletStock not found")
    models.walletstocks_delete(db,db_item)
    return models.walletstocks_get(db, data["id"])

@app.get("/")
def read_root():
    return {"Hello": "World"}

