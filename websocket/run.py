from websocket.export_libraries import *

symbols_lookup = pd.read_pickle('/root/PycharmProjects/ExecutionAlgo/websocket/outputs/symbols_lookup.pickle')


def get_btc_id(symbols_lookup=symbols_lookup, currency=None):
    mask_ticker = symbols_lookup.ticker == 'BTC'
    if currency is None:
        btc_df = symbols_lookup.loc[mask_ticker, :]

    else:
        mask_currency = symbols_lookup.currency == currency
        btc_df = symbols_lookup.loc[mask_ticker & mask_currency, :]

    btc_df = btc_df.dropna(axis=1, how='all').copy()

    return btc_df.iloc[0]


btc_id = get_btc_id()._id  # 'o850'

btc_row_us = get_btc_id(currency='USD')._id  # 'o1698'
