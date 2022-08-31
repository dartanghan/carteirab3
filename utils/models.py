from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship, Session
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

class WalletStock(Base):
    __tablename__ = "walletstock"
    id = Column(Integer, primary_key=True, index=True)
    walletstock_ticker = Column(String)
    walletstock_pm = Column(Float)
    walletstock_qtt = Column(Integer)
    wallet_id = Column(Integer, ForeignKey("wallet.id"))
    wallet = relationship("Wallet", back_populates="stocks")

####
#
# CRUD COMPONENTS ..........................
#
###########

def user_get(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

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

def wallet_get(db: Session, w_id: int):
    return db.query(Wallet).filter(Wallet.id == w_id).first()

def wallet_list(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Wallet).offset(skip).limit(limit).all()

def wallet_create(db: Session, obj):
    db_wallet = Wallet(
        user_id=obj["user_id"],
        wallet_name=obj["wallet_name"])
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet

def get_walletstock(db: Session, ws_id: int):
    return db.query(WalletStock).filter(WalletStock.id == ws_id).first()

def get_walletstocks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(WalletStock).offset(skip).limit(limit).all()

'''
TODO
- wallet_add_stock
- wallet_del_stock
- 
'''