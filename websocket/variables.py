

akbnk_id = 'H1758'


# d_lookup = get_symbols.get_field_shortcodes(get_symbols.fields_subscribe)

d_lookup = {'Ask': 'a',
            'High': 'h',
            'Close': 'cl',
            'Low': 'L',
            'Spread': 'sP',
            'VWAP': 'wa',
            'AskAmount0': 'w0',
            'Last': 'l',
            'BidPrice0': 'b0',
            'Direction': 'd',
            'Bid': 'b', 'AskPrice0': 'a0', 'Price': 'P',
            'BidAmount0': 'v0', 'Volume': 'v', 'Open': 'O'}
d_lookup.update({'_id': '_id', '_i': '_i', 'snapshot': '_s', 'E': 'E'})
inv_d_lookup = {v: k for k, v in d_lookup.items()}

fields = list(d_lookup.values())
