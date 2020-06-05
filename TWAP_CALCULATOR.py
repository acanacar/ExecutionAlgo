import logging
from pprint import pprint as pp

import aiohttp
import numpy as np
import pandas as pd


async def fetch(session, url):
    try:
        async with session.get(url) as response:
            return await response.json()
    except Exception as e:
        print(str(e))


class TWAP_CALCULATOR:
    def __init__(self, symbol, var_storages, last_n_minutes, cut_off_time=None):
        self.symbol = symbol
        self.VAR_STORAGES = var_storages
        self.last_n_minutes = last_n_minutes
        self.cut_off_time = cut_off_time
        self.recording_time = None
        self.last_prices = None
        self.twap_dict = None
        self.twap_val = None
        self.get_last_prices()

    @staticmethod
    def console_historical_prices(response):
        for item in response:
            item['d'] = pd.to_datetime(item['d'], unit='ms')
            pp(item)

    def get_last_prices(self):
        current_time = pd.Timestamp.now('Europe/Istanbul')

        if self.cut_off_time is None:
            self.cut_off_time = current_time - pd.DateOffset(minutes=self.last_n_minutes)
        p_ = []
        items = list(self.VAR_STORAGES.twap_response_pool[self.symbol].items())
        n = len(items) - 1
        for i in range(n, 0, -1):
            t, message = items[i]
            if not np.isnan(message['l']):
                p_.append(message['l'])
                if t < self.cut_off_time:
                    break
        p_.reverse()
        self.recording_time = current_time
        self.last_prices = p_

    async def get_historical_price(self):
        headers = {'Authorization': 'Basic Z2VuZWtzMDI6VCUzRTQhZzE='}
        async with aiohttp.ClientSession(headers=headers) as session:
            try:
                at = self.recording_time.strftime('%Y%m%d%H%M%S')
                at_last_service_url = f'http://testcloud.foreks.com/historical-service/intraday/' \
                                      f'code/{self.VAR_STORAGES.securityid_legacyCode_lookup_[self.symbol]}' \
                                      f'/period/{self.last_n_minutes}/at/{at}/last/{1}'
                response = await fetch(session=session, url=at_last_service_url)
                self.console_historical_prices(response)
            except Exception as e:
                print(str(e))
        return response

    def twap_from_last_prices(self):
        last_prices = self.last_prices
        o, h, l, c = last_prices[0], np.max(last_prices), np.min(last_prices), last_prices[-1]

        self.twap_val = (o + h + l + c) / 4
        self.twap_dict = {self.recording_time: {'open': o, 'high': h, 'low': l, 'close': c, 'twap': self.twap_val}}

    async def twap_from_historical_prices(self):
        logging.info(f'Getting historical prices for last {self.last_n_minutes} minutues')

        response = await self.get_historical_price()
        if len(response) > 1:
            logging.warning(f"historical response uzunlugu 1 den fazla")

        open, high, low, close = response[0]['o'], response[0]['h'], response[0]['l'], response[0]['c']
        self.twap_val = sum([open, high, low, close]) / 4
        self.twap_dict = {self.recording_time: {'open': open, 'high': high, 'low': low, 'close': close,
                                                'twap': self.twap_val}}

    async def calculate_twap(self):
        if len(self.last_prices) > 0:
            self.twap_from_last_prices()
        else:
            await self.twap_from_historical_prices()
