import data.stock as data
from sqlalchemy.orm import Session
from model.stock import Stock

def get_all_info(session: Session) -> list[Stock]:
    return data.get_all_info(session)
