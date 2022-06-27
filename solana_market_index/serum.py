import argparse
import json
import sys
import typing as t

import pyserum
import pyserum.connection
from pyserum.market import Market

import solana_market_index
from solana_market_index.market_details import MarketDetails

# factor into 2, 5
def try_factor(value: int) -> t.Optional[t.Tuple[int, int]]:
    twos, fives = 0, 0

    while value % 2 == 0:
        value = value // 2
        twos += 1

    while value % 5 == 0:
        value = value // 5
        fives += 1

    if value == 1:
        return (twos, fives)
    
    print(f'Remainder of {value}')
    return None

# The number of decimals needed to represent values of the form (X / precision)
def precision_scale(precision: int) -> t.Optional[int]:
    res = try_factor(precision)
    if res is None:
        return None

    twos, fives = res
    return max(twos, fives)


def generate_serum_market_index(api: str) -> list[MarketDetails]:
    solana_conn = pyserum.connection.conn(api)

    markets = pyserum.connection.get_live_markets()
    all_market_details = []

    for market_info in markets:
        print(f'Processing {market_info.name}')

        base, quote = market_info.name.split('/', 1)

        market = Market.load(solana_conn, market_info.address)
        market_state = market.state
        
        qty_increment = market_state.base_lot_size() / market_state.base_spl_token_multiplier()
        
        # equivalent to quote_lots_per_token / base_lots_per_token
        lot_price_per_token_price = (
            (market_state.quote_spl_token_multiplier() * market_state.base_lot_size()) /
            (market_state.base_spl_token_multiplier() * market_state.quote_lot_size())
        )

        if lot_price_per_token_price < 1:
            scale = 0
        else:
            scale = precision_scale(lot_price_per_token_price)
            assert scale is not None

        price_increment = 10 ** (-1 * scale)

        market_details = MarketDetails(
            market_info.name,
            base,
            quote,
            market_info.address,
            str(market_state.base_mint()),
            str(market_state.quote_mint()),
            qty_increment,
            qty_increment,
            price_increment
        )
        all_market_details.append(market_details.asdict())
    
    return all_market_details


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--api', default='https://api.mainnet-beta.solana.com')
    parser.add_argument('--save', action='store_true')
    args = parser.parse_args(argv)

    index = generate_serum_market_index(args.api)

    if args.save:
        serum_data_file = solana_market_index.get_package_dir().joinpath('data/serum.json')
        with open(serum_data_file, 'w+') as f:
            json.dump(index, f, indent=4)
    else:
        print(json.dumps(index, indent=4))



if __name__ == "__main__":
    main()
