from itertools import cycle
import time
from bittrex import Bittrex
mybittrex = Bittrex('2863cfd87a4f4b129a088c8f6d85a9f1', 'aea8b6ed946943f78053e160ba3310e6')

def run():
    try:
        asset_list_loop()
    except KeyboardInterrupt:
        print("\nCancelled.")

'''
Checks account BTC and ETH balances. Whichever is greater is the initial asset.
'''
def get_initial_asset_balance():
    btc_balance, eth_balance = mybittrex.get_balance('BTC')['result']['Balance'], mybittrex.get_balance('ETH')['result']['Balance']
    if btc_balance > eth_balance:
        return btc_balance, 'BTC'
    else:
        return eth_balance, 'ETH'

'''
Creates a cycle iterator for list of ETH-X market s, and checks whether tranasctions are profitable.
'''
def asset_list_loop():
    asset_cycle= cycle(['LTC', 'DASH', 'XMR', 'DGB', 'BTS', 'XRP', 'XEM', 'XLM', 'FCT', 'DGD', 'WAVES', 'ETC', 'STRAT',
                    'SNGLS', 'REP', 'NEO', 'ZEC', 'TIME', 'GNT', 'LGD', 'TRST', 'WINGS', 'RLC', 'GNO', 'GUP', 'LUN',
                    'TKN', 'HMQ', 'ANT', 'BAT', '1ST', 'QRL', 'CRB', 'PTOY', 'MYST', 'CFI', 'BNT', 'NMR', 'SNT', 'MCO',
                    'ADT', 'FUN', 'PAY', 'MTL', 'STORJ', 'ADX', 'OMG', 'CVC', 'QTUM', 'BCC'])
    while True:
        balance, asset = get_initial_asset_balance()
        print(balance, asset, '= ', end="")
        middle_asset = next(asset_cycle)
        check_profitability(asset, balance, middle_asset)
        if middle_asset == 'BCC':
            asset_switch_check(balance, asset)

"""
Determines whether it is profitable to trade between BTC/ETH.
"""
def asset_switch_check(balance, asset):
    print(balance, asset, '= ', end="")
    if asset_swap(asset)=='ETH':
        rate = quantity_buy_check(asset + '-' + asset_swap(asset), .9975*balance)
        final_balance = round((.9975*balance)/rate, 8)
    else:
        rate = quantity_sell_check(asset_swap(asset) + '-' + asset, .9975*balance)
        final_balance = round(.9975*balance*rate, 8)
    print(final_balance, asset_swap(asset) + '. ', end="")
    percent_profit_print(percent_profit(final_balance, balance, asset))
    if percent_profit(final_balance, balance, asset) > 1:
        asset_switch(balance, asset, rate)

'''
Carries out transaction from asset_switch_check if profitable.
'''
def asset_switch(balance, asset, rate):
    if (asset_swap(asset) == 'ETH'):
        if mybittrex.buy_limit(asset + '-' + asset_swap(asset), balance/rate, rate)['success']==1:
            time.sleep(1)
            sleeper()
    else:
        if mybittrex.sell_limit(asset_swap(asset) + '-' + asset, balance, rate):
            time.sleep(1)
            sleeper()
    print("Transaction complete.")

'''
Waits until open orders have been filled.
'''
def sleeper():
    while mybittrex.get_open_orders()['result']:
        time.sleep(1)
'''
Calculates profitability in the following way:
1. Starting balance is 99.75% of acccount balance to take care of fees.
2. Rate for limit buy is determined using quantity_sell_check (see below).
3. Projected balance of middle asset is calculated by dividing initial asset balance by sell rate.  [X/(X/Y) = X*(Y/X) = Y]
4. Rate for limit sell is determined using quantity_buy_check, this time using asset_swap() for target market (again, see below).
5. Projected balance of final asset is calculated by multiplying middle asset balance by buy rate.  [Y*(Y/Z) = Z]
6. Calculates percent of profits using percent_profit function. If this percentage is > 1 (> 100%), the transactions are profitable and should
   be executed at suggested rates. Otherwise, carry on.
'''
def check_profitability(starting_asset, balance, middle_asset):
    starting_balance = round(.9975*balance, 8)
    first_transaction_rate = quantity_sell_check(starting_asset + '-' + middle_asset, starting_balance)
    middle_asset_balance = round(starting_balance/first_transaction_rate, 8)
    print(middle_asset_balance, middle_asset, '= ', end="")
    second_transaction_rate = quantity_buy_check(asset_swap(starting_asset) + '-' + middle_asset, middle_asset_balance)
    final_asset_balance = round(.9975*middle_asset_balance*second_transaction_rate, 8)
    print(final_asset_balance, asset_swap(starting_asset) + '. ', end="")
    percent_profit_print(percent_profit(final_asset_balance, starting_balance, starting_asset))
    if percent_profit(final_asset_balance, starting_balance, starting_asset) > 1:
        transaction(starting_balance, starting_asset, middle_asset, first_transaction_rate, second_transaction_rate)

'''
Takes in the follow arguments in this order:
1. Initial asset balance.
2. Initial asset.
3. Middle asset.
4. Rate of purchase for the first transaction.
5. Rate of purchase for the second transaction.
'''
def transaction(initial_balance, initial_asset, middle_asset, first_rate, second_rate):
    print("First transaction...")
    if mybittrex.buy_limit(initial_asset + '-' + middle_asset, initial_balance/first_rate, first_rate)['success']==1:
        time.sleep(1)
        sleeper()
        print("Transaction complete.")
        time.sleep(10)
        print("Second transaction...")
        if mybittrex.sell_limit(asset_swap(initial_asset) + '-' + middle_asset, mybittrex.get_balance(middle_asset)['result']['Balance'], second_rate)['success']==1:
            time.sleep(1)
            sleeper()
            print("Transactions complete.")
        else:
            print("Second transaction cannot be completed.", mybittrex.sell_limit(asset_swap(initial_asset) + '-' + middle_asset, mybittrex.get_balance(middle_asset)['result']['Balance'], second_rate))
    else:
        print("First transaction cannot be completed.", mybittrex.buy_limit(initial_asset + '-' + middle_asset, initial_balance/first_rate, first_rate))

'''
Prints the percent gain/loss made from transactions and states whether they are profitable.
'''
def percent_profit_print(value):
    if value > 1:
        print(round(100*value, 5), "% of initial balance.")

    else:
        print(round(100*value, 5), "% of initial balance.")

'''
Converts initial and final assets to USDT. These values are divided (final/initial) - this yields the percentage the dollar value
of the final asset is of the initial dollar value.
'''
def percent_profit(final, initial, initial_asset):
    return (final * quantity_buy_check('USDT' + '-' + asset_swap(initial_asset), final)) / (initial * quantity_buy_check('USDT' + '-' + initial_asset, initial))

'''
quantity_X_check functions take a market and balance - if the quantity of an order in the requested orderbook is above the quantity potentially purchased/sold,
then the rate of this order is returned for calculations in hopes that, if calculations show some profit gain, this order will fill immediately.
'''
def quantity_sell_check(market, balance):
    for entry in mybittrex.get_orderbook(market, 'sell')['result']:
        if entry['Quantity']>(balance/entry['Rate']):
            return entry['Rate']

def quantity_buy_check(market, balance):
    for entry in mybittrex.get_orderbook(market, 'buy')['result']:
        if entry['Quantity']>(balance*entry['Rate']):
            return entry['Rate']

'''
Returns asset opposite the one holdings are currently in.
'''
def asset_swap(current_asset):
    if current_asset == 'BTC':
        return 'ETH'
    else:
        return 'BTC'
run()