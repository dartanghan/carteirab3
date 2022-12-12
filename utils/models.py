from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.orm import relationship, Session, joinedload
from utils.dbutils import Base

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, unique=True, index=True)
    user_password = Column(String)
    user_is_active = Column(Boolean, default=True)
    wallets = relationship("Wallet", back_populates="user")

class Wallet(Base):
    __tablename__ = "wallet"
    id = Column(Integer, primary_key=True, index=True)
    wallet_name = Column(String)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="wallets")
    stocks = relationship("WalletStock", back_populates="wallet")
    stocks_sold = relationship("WalletStockHistory", back_populates="wallet")

class WalletStock(Base):
    __tablename__ = "walletstock"
    id = Column(Integer, primary_key=True, index=True)
    walletstock_ticker = Column(String)
    walletstock_pm = Column(Float)
    walletstock_buy_date = Column(Date, default=datetime.utcnow)
    walletstock_qtt = Column(Integer)
    wallet_id = Column(Integer, ForeignKey("wallet.id"))
    wallet = relationship("Wallet", back_populates="stocks")
class WalletStockHistory(Base):
    """Historico de negociacoes"""
    __tablename__ = "walletstockhistory"
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallet.id"))
    walletstock_ticker = Column(String)
    walletstock_buy_date = Column(Date, default=datetime.utcnow)
    walletstock_sell_date = Column(Date, default=datetime.utcnow)
    walletstock_qtt = Column(Integer)
    walletstock_pm = Column(Float)
    wallet = relationship("Wallet", back_populates="stocks_sold")

####
#
# CRUD COMPONENTS ..........................
#
###########

def user_get(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def user_login(db: Session, user_email:str, user_password:str):
    return db.query(User).filter(User.user_email == user_email).filter(User.user_password == user_password).first()

def user_get_by_email(db: Session, user_email: str):
    return db.query(User).filter(User.user_email == user_email).first()

def user_list(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def user_create(db: Session, user):
    db_user = User(
        user_password=user["user_password"],
        user_email=user["user_email"])
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def user_delete(db: Session, user: User):
    db.delete(user)
    db.commit()
    return True

# Wallet
####################################################################

def wallet_get(db: Session, w_id: int, user_id:int):
    return db.query(Wallet).options(
    joinedload(Wallet.stocks)).filter(Wallet.id == w_id) \
        .filter(Wallet.user_id==user_id).first()

def wallet_get_by_user_and_wallet_name(db: Session, w_name: str, user_id: int):
    return db.query(Wallet).filter(Wallet.wallet_name == w_name).filter(Wallet.user_id == user_id).first()

def wallet_list(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Wallet).filter(Wallet.user_id==user_id).offset(skip).limit(limit).all()

def wallet_create(db: Session, obj):
    db_wallet = Wallet(
        user_id=obj["user_id"],
        wallet_name=obj["wallet_name"])
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet

def wallet_delete(db: Session, wallet: Wallet):
    db.delete(wallet)
    db.commit()
    return True

# WalletStocks
####################################################################

def walletstocks_get(db: Session, ws_id: int, user_id: int):
    return db.query(WalletStock).join(Wallet).filter(Wallet.user_id==user_id) \
        .filter(WalletStock.id == ws_id).first()

def walletstocks_list(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    wal = wallet_list(db, user_id)
    return db.query(WalletStock).join(Wallet).filter(Wallet.user_id==user_id) \
        .offset(skip).limit(limit).all()

def walletstocks_delete(db: Session, stock: WalletStock):
    db.delete(stock)
    db.commit()
    return True

def walletstocks_update(db: Session, ws_id:int, obj: dict, user_id: int):
    wal = wallet_get(db, obj["wallet_id"], user_id)
    db_item = db.query(WalletStock).filter(WalletStock.id == wal.id).first()
    for k,v in obj.items():
        if k in obj and obj[k]:
            setattr(db_item,k,obj[k])
    db.commit()
    return db_item

def walletstocks_sell(db: Session, ws_id:int, obj: WalletStock):
    ws_hist = WalletStockHistory(
        wallet_id = ws_id,
        walletstock_ticker = obj.walletstock_ticker,
        walletstock_buy_date = obj.walletstock_buy_date,
        walletstock_sell_date = datetime.now(),
        walletstock_qtt = obj.walletstock_qtt,
        walletstock_pm = obj.walletstock_pm,
    )
    db.add(ws_hist)
    db.commit()
    walletstocks_delete(db,obj)
    return ws_hist

def walletstocks_create(db: Session, obj, user_id: int):
    wal = wallet_get(db, obj["wallet_id"], user_id)
    if wal:
        db_item = WalletStock(
            wallet_id=wal.id,
            walletstock_pm=obj["walletstock_pm"],
            walletstock_qtt=obj["walletstock_qtt"],
            walletstock_ticker=obj["walletstock_ticker"])
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    return None

# WalletStocksHistory
####################################################################

def walletstockshistory_get(db: Session, id: int, user_id: int):
    return db.query(WalletStockHistory).join(Wallet).filter(Wallet.user_id==user_id) \
        .filter(WalletStockHistory.id == id).first()

def walletstockshistory_list(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    wal = wallet_list(db, user_id)
    return db.query(WalletStockHistory).join(Wallet).filter(Wallet.user_id==user_id) \
        .offset(skip).limit(limit).all()

def walletstockshistory_delete(db: Session, stock: WalletStockHistory):
    db.delete(stock)
    db.commit()
    return True
