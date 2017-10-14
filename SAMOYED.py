from bittrex import Bittrex
from itertools import cycle
import time

'''
Returns instance bittrex using api key/secret
'''
def get_bittrex_instance():
    return Bittrex('', '')

'''
Chooses either BTC or ETH balance
'''
def initialize():
    bit = get_bittrex_instance()
    asset_curr_list = (bit.get_balance('BTC')['result']['Balance'], 'BTC', bit.get_balance('ETH')['result']['Balance'], 'ETH')
    arbitrage_loop(max(asset_curr_list[0], asset_curr_list[2]), asset_curr_list[asset_curr_list.index(max(asset_curr_list[0], asset_curr_list[2]))+1])

'''
Cycles through list of BTC-X/ETH-X markets, calculates profitability
'''
def arbitrage_loop(balance, asset):
    middle_asset_cycle = cycle(['LTC', 'DASH', 'XMR', 'DGB', 'BTS', 'XRP', 'XEM', 'XLM', 'FCT', 'DGD', 'WAVES', 'ETC', 'STRAT',
         'SNGLS', 'REP', 'NEO', 'ZEC', 'TIME', 'GNT', 'LGD', 'TRST', 'WINGS', 'RLC', 'GNO', 'GUP', 'LUN', 'TKN', 'HMQ', 'ANT',
         'BAT', '1ST', 'QRL', 'CRB', 'PTOY', 'MYST', 'CFI', 'BNT', 'NMR', 'SNT', 'MCO', 'ADT', 'FUN', 'PAY', 'MTL', 'STORJ',
         'ADX', 'OMG', 'CVC', 'QTUM', 'BCC'])
    middle_assets_iterator = iter(middle_asset_cycle)
    bit = get_bittrex_instance()
    while True:
        middle_asset = next(middle_assets_iterator)
        det, first_transaction_rate, second_transaction_rate = calculate(balance, asset, middle_asset)
        if det > 1:
            transactions(asset, first_transaction_rate, middle_asset, second_transaction_rate)
            balance, asset = bit.get_balance(asset_swap(asset))['result']['Balance'], asset_swap(asset)
        if middle_asset == 'BCC':
            det, rate = final_calculate(balance, asset)
            if det > 1:
                final_transaction(balance, asset, rate)
                balance, asset = bit.get_balance(asset_swap(asset))['result']['Balance'], asset_swap(asset)
'''
Calculates resulting balance from transactions
'''
def calculate(balance, asset, middle_asset):
    bit = get_bittrex_instance()
    balance = .9975062344*balance
    first_transaction_rate, second_transaction_rate = bit.get_marketsummary(asset + '-' + middle_asset)['result']['Last'], bit.get_marketsummary(asset_swap(asset) + '-' + middle_asset)['result']['Last']
    middle_asset_balance = balance/first_transaction_rate
    final_asset_balance = .9975*middle_asset_balance*second_transaction_rate
    return profitability(balance, asset, final_asset_balance), first_transaction_rate, second_transaction_rate

'''
Returns opposite asset
'''
def asset_swap(asset):
    if asset == 'BTC':
        return 'ETH'
    return 'BTC'

'''
Calculates final balance:initial balance
'''
def profitability(balance, asset, final_asset_balance):
    bit = get_bittrex_instance()
    return (final_asset_balance*bit.get_marketsummary('USDT-' + asset_swap(asset))['result']['Last'])/(balance*bit.get_marketsummary('USDT-' + asset)['result']['Last'])

'''
Carries out transactions
'''
def transactions(asset, first_transaction_rate, middle_asset, second_transaction_rate):
    bit = get_bittrex_instance()
    if bit.buy_market(asset + '-' + middle_asset, .9975062344*bit.get_balance(asset)['result']['Balance']/first_transaction_rate)['success'] == 1:
        sleeper()
        if bit.sell_market(asset_swap(asset) + '-' + middle_asset, bit.get_balance(middle_asset)['result']['Balance']) == 1:
            sleeper()
        else:
            print("Failed.", bit.sell_market(asset_swap(asset) + '-' + middle_asset, bit.get_balance(middle_asset)['result']['Balance']))
    else:
        print("Failed.", bit.buy_market(asset + '-' + middle_asset, .9975062344*bit.get_balance(asset)['result']['Balance']/first_transaction_rate))
        exit(1)

'''
Waits while orders are open
'''
def sleeper():
    bit = get_bittrex_instance()
    while bit.get_open_orders()['result']:
        time.sleep(1)

'''
Carries out final BTC/ETH transaction
'''
def final_transaction(balance, asset, rate):
    bit = get_bittrex_instance()
    if asset == 'BTC':
        if bit.buy_market(asset + '-' + asset_swap(asset), .9975062344*bit.get_balance(asset)['result']['Balance']/rate)['success'] == 1:
            sleeper()
        else:
            print("Failed.", bit.buy_market(asset + '-' + asset_swap(asset), .9975062344*bit.get_balance(asset)['result']['Balance']/rate))
    else:
        if bit.sell_market(asset_swap(asset) + '-' + asset, bit.get_balance(asset)['result']['Balance'])['success'] == 1:
            sleeper()
        else:
            print(bit.sell_market(asset_swap(asset) + '-' + asset, bit.get_balance(asset)['result']['Balance']))

''''
Calculates resulting balance from transaction between BTC/ETH
'''
def final_calculate(balance, asset):
    bit = get_bittrex_instance()
    if asset_swap(asset) == 'ETH':
        rate = bit.get_marketsummary(asset + '-' + asset_swap(asset))['result']['Last']
        final_asset_balance = (.9975062344*balance)/rate
    else:
        rate = bit.get_marketsummary(asset_swap(asset) + '-' + asset)['result']['Last']
        final_asset_balance = .9975*balance*rate
    return profitability(balance, asset, final_asset_balance), rate
