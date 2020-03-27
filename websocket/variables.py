akbnk_id = 'H1758'
btc_try_id = 'o850'
btc_usd_id = 'o1698'
thyao_id = 'H2796'

fields_ = [['Ask', 'High', 'Close', 'Low', 'Spread', 'VWAP', 'AskAmount0', 'Last', 'BidPrice0', 'Direction', 'Bid',
            'AskPrice0', 'Price', 'BidAmount0', 'Volume', 'Open']]

fields_ = [
    'DateTime',
    # 'Time', 'Date', 'TimeMs', 'BestBidTime', 'BestAskTime',
    # 'TradeNumber',
    'Last',
    # 'Ticker',
    'Bid',
    # 'BidPrice0', 'BidAmount0',
    'Ask',
    # 'AskPrice0', 'AskAmount0'
]
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


aa = {
    'H1758': 'AKBNK',
    'o850': 'BTC_TRY',
    'o1698': 'BTC_USD',
}
