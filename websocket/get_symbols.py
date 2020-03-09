import requests
import pandas as pd

url = 'http://feed-definition.foreks.com/symbol/search'
res = requests.get(url)

res = res.json()
df = pd.DataFrame(res)

mask_bist = df['exchange'] == 'BIST'
mask_equity = df['marketSector'] == 'Equity'
mask_market = df['market'] == 'MSPOT'
mask_sub_market = df['subMarket'] == 'Z'
df_ = df.loc[mask_bist & mask_equity & mask_market & mask_sub_market]
df_.dropna(axis=1,inplace=True)
