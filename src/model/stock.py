from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Stock(BaseModel):
    figi: str
    stockname: str
    currency: str
    lastbuydate: datetime
    datadate: datetime
    closeprice: float
    yieldvalue: float
    dividendnet: float

class StockBase(Base):
    __tablename__ = "dividends"

    figi = Column(String, primary_key=True, index=True)
    stockname = Column(String, unique=True, index=True)
    currency = Column(String)
    lastbuydate = Column(DateTime)
    datadate = Column(DateTime)
    closeprice = Column(Float)
    yieldvalue = Column(Float)
    dividendnet = Column(Float)
