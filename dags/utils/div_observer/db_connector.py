import sqlite3

from sqlalchemy.future import select


class DBConnector:
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def insert_dividends_row(self, **params):
        if params:
            cursor = self.conn.cursor()
            insert_query = f"""
            INSERT INTO dividends (figi, stockname, currency, lastbuydate, 
            datadate, closeprice, yieldvalue, dividendnet) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """
            cursor.execute(insert_query, (params['figi'], params['stock_name'], params['currency'],
                params['last_buy_date'], params['data_date'], params['close_price'],
                params['yield_value'], params['dividend_net']))
            self.conn.commit()
        else:
            print('Нет данных')
        return self

    def update_last_buy_date_dividends(self, figi, new_last_buy_date, new_close_price):
        cursor = self.conn.cursor()
        update_query = f"""
        UPDATE dividends SET lastbuydate = '{new_last_buy_date}',
        closeprice = {new_close_price}
        WHERE figi = '{figi}'
        """
        cursor.execute(update_query)
        self.conn.commit()
        return self

    def select_all_figis(self):
        cursor = self.conn.cursor()
        select_query = """
            SELECT figi FROM dividends
        """
        rows = cursor.execute(select_query).fetchall()
        return rows

    def select_dividends_row(self, figi):
        cursor = self.conn.cursor()
        select_query = f"""
        SELECT * FROM dividends
        WHERE figi = '{figi}'
        """
        row = cursor.execute(select_query).fetchone()
        return row

    def select_all(self):
        cursor = self.conn.cursor()
        select_query = f"""
        SELECT * FROM dividends
        ORDER BY lastbuydate
        """
        rows = cursor.execute(select_query).fetchall()
        return rows

    def delete_old_dividends(self, ds):
        cursor = self.conn.cursor()
        delete_query = f"""
            DELETE FROM dividends 
            WHERE lastbuydate < {ds}; 
        """
        cursor.execute(delete_query)
        self.conn.commit()
        return self