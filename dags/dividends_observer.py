import airflow
import sqlite3
import os

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.decorators import task

from utils.test_module import test_string
from utils.div_observer.dividend_observer import DividendObserver
from utils.div_observer.instrument_storage import InstrumentStorage
from utils.div_observer.config import DB_PATH
from utils.div_observer.db_connector import DBConnector

DB_PATH = os.path.expanduser(f"~{DB_PATH}")

dag = DAG(
    dag_id="dividends_observer",
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval="@daily",
)

#1 Получение списка текущих figi в бд
def _get_current_dividends(**context):
    with DBConnector(DB_PATH) as conn:
        rows = conn.select_all_figis()
    set_of_figis = {x[0] for x in rows}
    context["task_instance"].xcom_push(key="figis_before_prepare_dividends",
                                       value=set_of_figis)


get_current_dividends = PythonOperator(
    task_id="get_current_dividends",
    python_callable=_get_current_dividends,
    dag=dag,
)

#2 Выгрузка дивидендов в бд
def _prepare_dividend_record():
    storage = InstrumentStorage()
    div_obs = DividendObserver(storage)
    div_obs.work()

prepare_dividend_record = PythonOperator(
    task_id="prepare_dividend_record",
    python_callable=_prepare_dividend_record,
    dag=dag,
)

#3 Очистка просроченных дивидендов
def _clear_old_dividends(**context):
    execution_date = context["ds"]
    with DBConnector(DB_PATH) as conn:
        print('Очистка просроченных дивидендов')
        conn.delete_old_dividends(execution_date)

#3.5 Вставка искусственных данных
clear_old_dividends = PythonOperator(
    task_id="clear_old_dividends",
    python_callable=_clear_old_dividends,
    dag=dag,
)

# def _artificial_insert():
#     params = {
#         'figi': 'test_figi',
#         'stock_name': 'test_name',
#         'currency': 'USD',
#         'last_buy_date': '2025-10-01',
#         'data_date': '2025-10-05',
#         'close_price': 145.05,
#         'yield_value': 0.025,
#         'dividend_net': 0.82
#     }
#     with DBConnector(DB_PATH) as conn:
#         conn.insert_dividends_row(**params)
#
# artificial_insert = PythonOperator(
#     task_id="artificial_insert",
#     python_callable=_artificial_insert,
#     dag=dag,
# )

#4 Сравнение figi до и после выгрузки и очистки
def _compare_figis(**context):
    print("Проверка передачи по xcom")
    old_set_of_figis = context["task_instance"].xcom_pull(task_ids="get_current_dividends",
                                                       key="figis_before_prepare_dividends")
    with DBConnector(DB_PATH) as conn:
        rows = conn.select_all_figis()
    current_set_of_figis = {x[0] for x in rows}

    set_difference = old_set_of_figis.symmetric_difference(current_set_of_figis)
    new_dividend_rows = []
    for figi in set_difference:
        with DBConnector(DB_PATH) as conn:
            row = conn.select_dividends_row(figi)
            new_dividend_rows.append(row)
            print(f'Новая акция: {row[1]}')


compare_files = PythonOperator(
    task_id="compare_files",
    python_callable=_compare_figis,
    dag=dag,
)

get_current_dividends >> prepare_dividend_record >> clear_old_dividends >> compare_files
