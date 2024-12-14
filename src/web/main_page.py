from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from model.stock import Stock
from service import main_page as service
from data.db_connector import SessionLocal

router = APIRouter(prefix="/main")

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@router.get("")
@router.get("/")
def get_all_info(session: Session = Depends(get_session)) -> list[Stock]:
    return service.get_all_info(session)
