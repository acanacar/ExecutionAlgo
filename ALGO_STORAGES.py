import asyncio
import json

import numpy as np
import pandas as pd

from dev.vars.paths import *


class QUEUE_STORAGES:
    fx_plus_messages_queue = asyncio.Queue()
    twap_children_queue = asyncio.Queue()
    detected_parent_orders_queue = asyncio.Queue()
    detected_child_order_queues = {'POV': asyncio.Queue(), 'TWAP': asyncio.Queue(), 'VWAP': asyncio.Queue()}
    child_pov_orders_queue = asyncio.Queue()
    algo_parent_queue = asyncio.Queue()
    algo_parent_pov_queue = asyncio.Queue()


class ORDER_STORAGES:
    algo_parents = {}


class VAR_STORAGES:
    def __init__(self):
        self.field_df = pd.read_pickle(project_path / Path('outputs/fields_lookup.pickle'))
        self.field_df_time = self.field_df.loc[self.field_df.type == 'TIME']

        self.display_shortcode_lookup = self.field_df[['display', 'shortCode']].set_index('display').to_dict()[
            'shortCode']
        self.display_shortcode_lookup.update(
            {'_id': '_id',
             '_i': '_i',
             'E': 'E',
             'err': 'err',
             'code': 'code',
             'mydate': 'mydate',
             'my_time': 'my_time',
             'datetime_pd': 'datetime_pd',
             'vwap': 'wa'
             })

        self.shortcode_display_lookup = {v: k for k, v in self.display_shortcode_lookup.items()}

        self.subscription_fields = {
            'twap': ['DateTime', 'Last']
            , 'pov': ['TotalVolume']  # 'tV'
            , 'last': ['Last']
            , 'unused': [
                'Volume',  # 'v'
                'TradedValue']  # 'TV'
            , 'general': ['DateTime', 'Last',  # 'Bid', 'Ask', 'VWAP',
                          'Volume',  # 'v'
                          'TradedValue',  # 'TV'
                          'TotalVolume'  # 'tV'
                          ]
        }

        self.symbol_securityid_lookup = {
            'HALKB': 'H1552', 'KOZAL': 'H1312', 'TCELL': 'H1392', 'TSKB': 'H1550', 'TTKOM': 'H1332', 'PETKM': 'H1428',
            'SISE': 'H1434', 'DOHOL': 'H1734', 'VAKBN': 'H1728', 'AKBNK': 'H1758', 'GARAN': 'H1846', 'YKBNK': 'H1586',
            'TOASO': 'H2108', 'TKFEN': 'H1962', 'FROTO': 'H2024', 'KOZAA': 'H1922', 'BIMAS': 'H1946', 'TUPRS': 'H2122',
            'KRDMD': 'H2240', 'SODA': 'H2204', 'ARCLK': 'H2680', 'EREGL': 'H2674', 'SAHOL': 'H2746', 'EKGYO': 'H2732',
            'THYAO': 'H2796', 'PGSUS': 'H2554', 'ISCTR': 'H2692', 'KCHOL': 'H2488', 'ASELS': 'H2424', 'TAVHL': 'H2548'}

        self.securityid_legacyCode_lookup_ = {
            'H1552': 'HALKB.E.BIST', 'H1312': 'KOZAL.E.BIST', 'H1392': 'TCELL.E.BIST',
            'H1550': 'TSKB.E.BIST', 'H1332': 'TTKOM.E.BIST', 'H1428': 'PETKM.E.BIST',
            'H1434': 'SISE.E.BIST', 'H1734': 'DOHOL.E.BIST', 'H1728': 'VAKBN.E.BIST',
            'H1758': 'AKBNK.E.BIST', 'H1846': 'GARAN.E.BIST', 'H1586': 'YKBNK.E.BIST',
            'H2108': 'TOASO.E.BIST', 'H1962': 'TKFEN.E.BIST', 'H2024': 'FROTO.E.BIST',
            'H1922': 'KOZAA.E.BIST', 'H1946': 'BIMAS.E.BIST', 'H2122': 'TUPRS.E.BIST',
            'H2240': 'KRDMD.E.BIST', 'H2204': 'SODA.E.BIST', 'H2680': 'ARCLK.E.BIST',
            'H2674': 'EREGL.E.BIST', 'H2746': 'SAHOL.E.BIST', 'H2732': 'EKGYO.E.BIST',
            'H2796': 'THYAO.E.BIST', 'H2554': 'PGSUS.E.BIST', 'H2692': 'ISCTR.E.BIST',
            'H2488': 'KCHOL.E.BIST', 'H2424': 'ASELS.E.BIST', 'H2548': 'TAVHL.E.BIST'}

        self.last_pc_q = ['0']

        self.shortcodes = {
            'general': [self.display_shortcode_lookup[f] for f in self.subscription_fields['general']],
            'last': [self.display_shortcode_lookup[f] for f in self.subscription_fields['last']],
            'pov': [self.display_shortcode_lookup[f] for f in self.subscription_fields['pov']],
            'twap': [self.display_shortcode_lookup[f] for f in self.subscription_fields['twap']],
        }
        # self.symbols_to_subscribe = ['H2240', 'H1846', 'o850', 'o1877', 'o1882', 'o1889']  # KARDMD  and GARAN
        self.symbols_to_subscribe = []
        self.minutes_processed_pool = {symbol: {} for symbol in self.symbols_to_subscribe}
        self.minutes_candlesticks_pool = {symbol: [] for symbol in self.symbols_to_subscribe}
        self.current_tick = {symbol: None for symbol in self.symbols_to_subscribe}
        self.previous_tick = {symbol: None for symbol in self.symbols_to_subscribe}

        self.general_response_template = {shortcode: np.nan for shortcode in self.shortcodes['general']}

        # prices
        self.response_pool = {symbol: {} for symbol in ['H1728']}
        self.last_prices_pool = {symbol: {} for symbol in ['H1728']}
        self.pov_response_pool = {symbol: {} for symbol in self.symbols_to_subscribe}
        self.twap_response_pool = {symbol: {} for symbol in self.symbols_to_subscribe}
        # "s" field ina sahip olmayan her message buraya ekleniyor

        self.MESSAGES = {
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
                "symbols": self.symbols_to_subscribe,
                "fields": self.shortcodes['general']
            })
        }
