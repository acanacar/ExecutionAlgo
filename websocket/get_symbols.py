import requests
import pandas as pd
import xlsxwriter

url = 'http://feed-definition.foreks.com/symbol/search'
res = requests.get(url)

res = res.json()
df = pd.DataFrame(res)

mask_bist = df['exchange'] == 'BIST'
mask_equity = df['marketSector'] == 'Equity'
mask_market = df['market'] == 'MSPOT'
mask_sub_market = df['subMarket'] == 'Z'
df_ = df.loc[mask_bist & mask_equity & mask_market & mask_sub_market]
df_.dropna(axis=1, inplace=True)

l = {}
exceptions_cols = ['index', 'indexWeight', 'tag']
for col in df.columns:
    if col in exceptions_cols:
        continue
    vals = list(df[col].unique())

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

with xlsxwriter.Workbook('test2.xlsx',{'nan_inf_to_errors':True}) as wb:
    ws = wb.add_worksheet()
    for col_number, (key, value) in enumerate(l.items()):
        ws.write(0, col_number, key)
        for row_number, val in enumerate(value, 1):
            if row_number <= 1000:
                ws.write(row_number, col_number, val)
