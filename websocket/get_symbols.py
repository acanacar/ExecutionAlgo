import requests
import pandas as pd
import xlsxwriter


def check_cols_areas_to_excel(data):
    '''

    :param data:
    :return:
    '''
    l = {}
    exceptions_cols = ['index', 'indexWeight', 'tag']
    for col in data.columns:
        if col in exceptions_cols:
            continue
        vals = list(data[col].unique())

        l.update({col: vals})

    l2 = {}
    for k, v in l.items():
        l2.update({k: len(v)})

    l2 = sorted(l2.items(), key=lambda x: x[1])

    with xlsxwriter.Workbook('test.xlsx') as wb:
        ws = wb.add_worksheet()
        for row_number, (key, value) in enumerate(l2):
            ws.write(row_number, 0, key)
            ws.write(row_number, 1, value)

    with xlsxwriter.Workbook('test2.xlsx', {'nan_inf_to_errors': True}) as wb:
        ws = wb.add_worksheet()
        for col_number, (key, value) in enumerate(l.items()):
            ws.write(0, col_number, key)
            for row_number, val in enumerate(value, 1):
                if row_number <= 1000:
                    ws.write(row_number, col_number, val)


def get_specific_stock__id(data, ticker):
    return data.loc[data.ticker == ticker].iloc[0]._id


def get_field_shortcodes(field_names):
    url = 'http://feed-definition.foreks.com/field/search'
    res = requests.get(url)

    res = res.json()
    dframe = pd.DataFrame(res)
    short_codes_df = dframe.loc[dframe['name'].isin(field_names), ['display', 'shortCode']] \
        .set_index('display')
    # fields = short_codes_df['shortCode'].values
    d = short_codes_df.to_dict()['shortCode']
    return d


def get_symbol_search_data():
    url = 'http://feed-definition.foreks.com/symbol/search'
    res = requests.get(url)

    res = res.json()
    return pd.DataFrame(res)

#
df = get_symbol_search_data()

#
check_cols_areas_to_excel(data=df)

#
mask_bist = df['exchange'] == 'BIST'
mask_bist_domain = df['domain'] == 'BIST'
mask_equity = df['marketSector'] == 'Equity'
mask_market = df['market'] == 'MSPOT'
mask_sub_market = df['subMarket'] == 'Z'
mask_sub_market_desc = df['subMarketDesc'] == 'PAY-YILDIZ PAZAR'
mask_security_type = df['securityType'] == 'Stock'
mask_currency = df['currency'] == 'TRY'
mask_status = df['status'] == 'ACTIVE'
mask_security = df.security == 'E'
df_ = df.loc[mask_bist &
             mask_equity &
             mask_market &
             mask_sub_market &
             mask_security_type &
             mask_status
             ]
df_.dropna(axis=1, inplace=True)

#
_id = get_specific_stock__id(data=df_, ticker='AKBNK.E')

#
fields_subscribe = \
    [
        "Open", "High", "Low", "Close","Volume",
        "Price",
        "Direction",
        "Last",
        "Spread",
        "Bid", "Ask",
        "BidPrice0", "AskPrice0", "BidAmount0", "AskAmount0",
        "VWAP",
    ]

d = get_field_shortcodes(fields_subscribe)
