import service.main_page as service
from sqlalchemy.orm import Session
from fastapi import Depends
from model.stock import StockBase

def get_all_info(session: Session):
    return session.query(StockBase).all()

