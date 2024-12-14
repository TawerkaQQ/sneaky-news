import os
import sqlite3
import time

from datetime import datetime, timedelta
from locale import currency

from dotenv import load_dotenv
from tinkoff.invest import Client, RequestError, InstrumentStatus
from .storage_manager import StorageManager
from .db_connector import DBConnector
from .config import TOKEN, DB_PATH

load_dotenv()

DB_PATH = os.path.expanduser(f"~{DB_PATH}")

# current_path = os.path.dirname(os.path.abspath(__file__))
# DB_PATH = os.path.join(current_path, '..', 'db', 'tink_lite_db.db')

class DividendObserver:
    def __init__(self, instrument_storage):
        self.token = None

        self.storage_manager = StorageManager(instrument_storage)

        self.set_token()

    def set_token(self):
        token = TOKEN
        if token is None:
            raise ValueError('Token is None')
        self.token = token

    def work(self):
        self.form_instrument_storage()
        self.form_record()

    def form_instrument_storage(self):
        with Client(self.token) as client:
            instruments = client.instruments.shares(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_BASE)
            for instrument in instruments.instruments:
                self.storage_manager.append_instrument(instrument)
        return self

    def get_dividends(self, figi):
        with Client(self.token) as client:
            dividends = client.instruments.get_dividends(
                figi = figi,
                from_=datetime.utcnow(),
                to=datetime.utcnow() + timedelta(days=365),

            )
        return dividends.dividends

    def form_record(self):
        for i, instrument in enumerate(self.storage_manager.iterate_instruments()):
            if instrument.currency != 'rub':
                continue
            print(instrument)
            got_dividends = False
            while got_dividends == False:
                try:
                    dividends = self.get_dividends(instrument.figi)
                    got_dividends = True
                except RequestError as e:
                    print('Ловим таймаут')
                    time_to_wait = e.metadata.ratelimit_reset
                    print(f'Ждем {time_to_wait} секунд ...')
                    time.sleep(time_to_wait)
                    got_dividends = False

            for dividend in dividends:
                current_record = {
                    'figi': instrument.figi,
                    'stock_name': instrument.name,
                    'currency': instrument.currency,
                    #'payment_date': dividend.payment_date,
                    #'declared_date': dividend.declared_date,
                    'last_buy_date': dividend.last_buy_date,
                    'data_date': datetime.now(),
                    'close_price': self.unit_former(dividend.close_price),
                    'yield_value': self.unit_former(dividend.yield_value),
                    'dividend_net': self.unit_former(dividend.dividend_net)
                }
                self.insert_dividends_row(current_record)
        return self

    def insert_dividends_row(self, record):
        with DBConnector(DB_PATH) as conn:
            print(f'Работа с {record["figi"]} - {record["stock_name"]}')
            try:
                conn.insert_dividends_row(**record)
            except sqlite3.Error as e:
                figi = record['figi']
                last_buy_date = str(record['last_buy_date'])
                close_price = float(record['close_price'])
                print(e)
                print(f'{figi} уже существует в таблице')
                print(f'Проверка на дату дивидендов')
                last_buy_date_db = conn.select_dividends_row(record['figi'])[3]
                #close_price_db = conn.select_dividends_row(record['figi'])[5]
                conn.update_last_buy_date_dividends(figi, last_buy_date, close_price)
                print('Изменилась дата дивидендов\n')
        return self

    def unit_former(self, unit_object):
        if str(unit_object.nano).count('0') > 1:
            return f'{unit_object.units}.{str(unit_object.nano).replace("0", "")}'
        else:
            return f'{unit_object.units}.{unit_object.nano}'
