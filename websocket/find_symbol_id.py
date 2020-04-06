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

btc_row_us = get_btc_id(currency='THYAO.E')._id  # 'o1698'

df = pd.read_pickle('/root/PycharmProjects/ExecutionAlgo/websocket/outputs/symbols_lookup.pickle')

df = df[['ticker', '_id']]

from websocket.variables import all_ids

a = None
for i, r in df.iterrows():
    if r['ticker'].startswith('THYAO.E'):
        print(r)
        a = r

import math

for k, v in a.to_dict().items():
    if type(v) == float:
        if math.isnan(v):
            continue
    print('\n', k, v)


# only bist30

xu30= {}
for i, r in df.iterrows():
    if type(r['index'])==list:
        if 'XU030' in r['index']:
           xu30.update({r['ticker']:r['_id']})


import pickle
from constants import *
with open(websocket_path/Path('outputs/xu030_id.pickle'),'wb') as handle:
    pickle.dump(xu30,handle,protocol=pickle.HIGHEST_PROTOCOL)

