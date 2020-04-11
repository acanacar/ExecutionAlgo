from constants import *
from websocket.export_libraries import *

akbnk_id = 'H1758'
btc_try_id = 'o850'
btc_usd_id = 'o1698'
thyao_id = 'H2796'
acsel_id = 'H2898'
tknosa_id = 'H1582'

all_ids = [akbnk_id, btc_try_id, btc_usd_id, thyao_id, acsel_id, tknosa_id]
aa = {
    'H1758': 'AKBNK',
    'o850': 'BTC_TRY',
    'o1698': 'BTC_USD',
    'H2796': 'THYAO',
    'H2898': 'ACSEL',
    'H1582': 'TKNSA'}

# fields_lookup = get_symbols.get_field_shortcodes(get_symbols.fields_subscribe)
field_df = pd.read_pickle(websocket_path / Path('outputs/fields_lookup.pickle'))
field_df_time = field_df.loc[field_df.type == 'TIME']
fields_lookup = field_df[['display', 'shortCode']].set_index('display').to_dict()['shortCode']
fields_lookup.update(
    {'_id': '_id', '_i': '_i', 'snapshot': '_s', 'E': 'E', 'err': 'err', 'code': 'code'
        , 'mydate': 'mydate', 'my_time': 'my_time', 'datetime_pd': 'datetime_pd'
     })

inverse_fields_lookup = {v: k for k, v in fields_lookup.items()}
import pickle

with open(websocket_path / Path('outputs/xu030_id.pickle'), 'rb') as handle:
    xu030 = pickle.load(handle)

symbols_to_subscribe = [
    akbnk_id,
    btc_try_id,
    btc_usd_id,
    thyao_id, acsel_id, tknosa_id

]
xu030_symbols = [xu030['HALKB.E'],
                 xu030['KOZAL.E'],
                 xu030['TCELL.E'],
                 xu030['TSKB.E'],
                 xu030['TTKOM.E'],
                 xu030['PETKM.E'],
                 xu030['SISE.E'],
                 xu030['DOHOL.E'],
                 xu030['VAKBN.E'],
                 xu030['AKBNK.E'],
                 xu030['GARAN.E'],
                 xu030['YKBNK.E'],
                 xu030['TOASO.E'],
                 xu030['TKFEN.E'],
                 xu030['FROTO.E'],
                 xu030['KOZAA.E'],
                 xu030['BIMAS.E'],
                 xu030['TUPRS.E'],
                 xu030['KRDMD.E'],
                 xu030['SODA.E'],
                 xu030['ARCLK.E'],
                 xu030['EREGL.E'],
                 xu030['SAHOL.E'],
                 xu030['EKGYO.E'],
                 xu030['THYAO.E'],
                 xu030['PGSUS.E'],
                 xu030['ISCTR.E'],
                 xu030['KCHOL.E'],
                 xu030['ASELS.E'],
                 xu030['TAVHL.E']]
symbols_to_subscribe = xu030_symbols + [btc_usd_id, btc_try_id]

# fields_ = [['Ask', 'High', 'Close', 'Low', 'Spread', 'VWAP', 'AskAmount0', 'Last', 'BidPrice0', 'Direction', 'Bid',
#             'AskPrice0', 'Price', 'BidAmount0', 'Volume', 'Open']]

# fields_ = [
#     'DateTime',
#     # 'Time', 'Date', 'TimeMs', 'BestBidTime', 'BestAskTime',
#     # 'TradeNumber',
#     'Last',
#     # 'Ticker',
#     'Bid',
#     # 'BidPrice0', 'BidAmount0',
#     'Ask',
#     # 'AskPrice0', 'AskAmount0'
# ]
# fields_ = ['DateTime', 'Ticker', 'Price', 'Last',
#            'Bid', 'BidPrice0', 'BidAmount0',
#            'Ask', 'AskPrice0', 'AskAmount0'
#            ]
# fields_ = ['BidPrice1', 'BidAmount1', 'AskPrice1', 'AskAmount1', 'BidPrice2', 'BidAmount2', 'AskPrice2', 'AskAmount2',
#      'BidPrice3', 'BidAmount3', 'AskPrice3', 'AskAmount3', 'BidPrice4', 'BidAmount4', 'AskPrice4', 'AskAmount4',
#      'BidPrice5', 'BidAmount5', 'AskPrice5', 'AskAmount5', 'BidPrice6', 'BidAmount6', 'AskPrice6', 'AskAmount6',
#      'BidPrice7', 'BidAmount7', 'AskPrice7', 'AskAmount7', 'BidPrice8', 'BidAmount8', 'AskPrice8', 'AskAmount8',
#      'BidPrice9', 'BidAmount9', 'AskPrice9', 'AskAmount9']
# fields_ = fields_ + ['DateTime', 'Time', 'Date']


fields_ = [
    'DateTime',
    'Last',
    'Bid',
    'Ask',
]

fields = [fields_lookup[f] for f in fields_]

MESSAGES = {
    'HEARTBEAT_MESSAGE': json.dumps({"_id": 16}),

    'LOGIN_MSG': json.dumps({
        "_id": 64,
        "user": "IP-AKNKE4623-91746",
        "password": "91746",
        "info": "1.5.22.4",
        "resource": "fxplus"})
    ,
    'SUBSCRIBE_MESSAGE': json.dumps({
        "_id": 1,
        "id": 1,
        "symbols": symbols_to_subscribe,
        "fields": fields
    })}
