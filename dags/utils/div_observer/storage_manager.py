# import os
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .instrument_storage import InstrumentStorage


class StorageManager:
    def __init__(self, instrument_storage):
        self.storage = instrument_storage

    def append_instrument(self, instrument):
        self.storage.append_instrument(instrument)
        return self

    def get_stock_by_figi(self, figi):
        return self.storage.get_stock_by_figi(figi)

    def iterate_instruments(self):
        return iter(self.storage)