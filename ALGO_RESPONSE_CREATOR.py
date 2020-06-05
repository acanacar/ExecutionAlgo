from dev.export_libraries import *


class RESPONSE_CREATOR:
    def __init__(self, fx_plus_messages_queue, var_storages):
        self.loop = asyncio.get_event_loop()
        self.MSG_COUNT = 0
        self.VAR_STORAGES = var_storages
        self.fx_plus_messages_queue = fx_plus_messages_queue
        self.response_pool_lock = asyncio.Lock()
        self.last_prices_pool_lock = asyncio.Lock()
        self.pov_response_pool_lock = asyncio.Lock()
        self.schedule_tasks()

    def schedule_tasks(self):
        self.loop.create_task(self.handle_message())

    def create_general_response(self, msg):
        try:
            msg_im = self.VAR_STORAGES.general_response_template.copy()
            msg_im.update(msg)
            return msg_im
        except Exception as e:
            logging.exception(e)

    def create_response(self, msg):
        msg = json.loads(msg)
        if '_i' in msg.keys():
            msg['my_time'] = int(round(time.time() * 1000))
            msg['datetime_pd'] = pd.Timestamp.now('Europe/Istanbul')
            msg['time_string'] = msg['datetime_pd'].strftime('%d/%m/%Y %H:%M:%S')
            self.MSG_COUNT += 1
        else:
            print(f'not handled for message : {msg}')
            msg = None
        return msg

    def console_response(self, response):
        '''
        NAME : CONSOLE_RESPONSE
        :param response:
        :return:
        '''
        if self.MSG_COUNT % 100 == 0:
            print(f'{self.MSG_COUNT}. mesaj alindi. :{response}')

    async def update_response_pool(self, input):
        with await self.response_pool_lock:
            self.VAR_STORAGES.response_pool[input['_i']].update(
                {input['datetime_pd']: input})

    async def update_pov_response_pool(self, input):
        with await self.pov_response_pool_lock:
            self.VAR_STORAGES.pov_response_pool[input['_i']].update(
                {input['datetime_pd']: input})

    async def update_last_prices_pool(self, input):
        with await self.last_prices_pool_lock:
            self.VAR_STORAGES.last_prices_pool[input['_i']].update(
                {input['datetime_pd']: input['l']})

    async def update_twap_response_pool(self, input):
        with await self.response_pool_lock:
            self.VAR_STORAGES.twap_response_pool[input['_i']].update(
                {input['datetime_pd']: input})

    def determine_type_response(self, input):
        response_types = []
        if "_s" in input:
            response_types.append('snapshot')
            return response_types
        if not np.isnan(input['l']):
            response_types.append('last')
        if not np.isnan(input['tV']):
            response_types.append('pov')
        if all(not np.isnan(input[k]) for k in self.VAR_STORAGES.shortcodes['twap']):
            response_types.append('twap')
        return response_types

    async def update_storage(self, input, response_types):
        # if 'snapshot' not in response_types:
        if 1 == 1:
            await self.update_response_pool(input=input)

            if 'last' in response_types:
                await self.update_last_prices_pool(input=input)
                # self.make_candlestick(current_tick=input)

            if 'twap' in response_types:
                await self.update_twap_response_pool(input=input)

            if 'pov' in response_types:
                await self.update_pov_response_pool(input=input)

    async def handle_message(self):
        while True:
            message = await self.fx_plus_messages_queue.get()
            if message:
                response = self.create_response(message)
                if response is not None:
                    self.console_response(response)
                    response_general = self.create_general_response(msg=response)

                    response_types = self.determine_type_response(input=response_general)
                    await self.update_storage(input=response_general, response_types=response_types)
                self.fx_plus_messages_queue.task_done()

def make_candlestick(self, current_tick):
        start = time.perf_counter()
        symbol = current_tick['_i']
        previous_tick = self.VAR_STORAGES.previous_tick
        minutes_processed = self.VAR_STORAGES.minutes_processed_pool[symbol]
        minutes_candlesticks = self.VAR_STORAGES.minutes_candlesticks_pool[symbol]

        if previous_tick[symbol] is None:
            previous_tick[symbol] = current_tick['l']

        logging.debug(symbol)
        logging.debug("=== Received Tick ===")
        logging.debug(f"{current_tick['datetime_pd']} @ {current_tick['l']}")
        # print("=== Received Tick ===")
        # print(f"{current_tick['datetime_pd']} @ {current_tick['l']}")

        tick_dt = current_tick['datetime_pd'].floor('1Min')

        if tick_dt not in minutes_processed:
            logging.debug('starting new candlestick')
            minutes_processed[tick_dt] = True

            if len(minutes_candlesticks) > 0:
                minutes_candlesticks[-1]['close'] = previous_tick[symbol]

            minutes_candlesticks.append({
                "minute": tick_dt,
                'open': previous_tick[symbol],
                'high': current_tick['l'],
                'low': current_tick['l']
            })

        if len(minutes_candlesticks) > 0:
            current_candlestick = minutes_candlesticks[-1]
            if current_tick['l'] > current_candlestick['high']:
                current_candlestick['high'] = current_tick['l']
            if current_tick['l'] < current_candlestick['low']:
                current_candlestick['low'] = current_tick['l']

        previous_tick[symbol] = current_tick['l']

        logging.debug("== Candlesticks ==")
        for candlestick in minutes_candlesticks[-3:]:
            logging.debug(candlestick)
        end = time.perf_counter()
        logging.debug(f"on_message is lasted {end - start} seconds")
