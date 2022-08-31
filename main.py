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


@app.get("/")
def read_root():
    return {"Hello": "World"}

