class InstrumentStorage:
    def __init__(self):
        self.instruments = []

    def append_instrument(self, instrument):
        self.instruments.append(instrument)
        return self

    def get_stock_by_figi(self, figi):
        return [instrument for instrument in self.instruments if instrument.figi == figi][0]

    def __iter__(self):
        return iter(self.instruments)

    def __getitem__(self, item):
        return self.instruments[item]

    def __len__(self):
        return len(self.instruments)
