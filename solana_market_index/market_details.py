from dataclasses import dataclass, asdict

@dataclass
class MarketDetails:
    name: str
    base_currency: str
    quote_currency: str
    address: str
    base_mint: str
    quote_mint: str
    min_qty: float
    qty_increment: float
    price_increment: float

    def asdict(self):
        return asdict(self)
