#links to acct with api key
from bittrex import Bittrex
mybittrex = Bittrex(None, None)

initialBalance = 1
ethflag = 0

currencylist = ['LTC', 'DASH', 'XMR', 'DGB', 'BTS', 'XRP', 'XEM', 'XLM', 'FCT', 'DGD', 'WAVES', 'ETC', 'STRAT', 'SNGLS', 'REP', 'NEO', 'ZEC', 'TIME', 'GNT', 'LGD', 'TRST', 'WINGS', 'RLC', 'GNO', 'GUP', 'LUN', 'TKN', 'HMQ', 'ANT', 'SC', 'BAT', '1ST', 'QRL', 'CRB', 'PTOY', 'MYST', 'CFI', 'BNT', 'NMR', 'SNT', 'MCO', 'ADT', 'FUN', 'PAY', 'MTL', 'STORJ', 'ADX', 'OMG', 'CVC', 'QTUM', 'BCC']


def run():
    transaction()

#dynamically retrieve ETH tradable currencies and stores stock symbols......takes forever.
'''
def getList():
    print("Retrieving exchange list", end='')
    currencies = mybittrex.get_currencies()['result']
    for c in currencies:
        if (mybittrex.get_market_history(eth + "-" + c['Currency']))['success']:
            currencylist.append(c['Currency'])
            print(".", end='', sep='', flush=True)
        else:
            pass

    print("\nExchange list retrieved:")
    print(currencylist)
'''

#gather pricing information based on input
def getValue(s, t):
    #construct market string from input
    market = s + "-" + t
    #create a profile for recent transactions
    #print(market)
    priceprofile = mybittrex.get_market_history(market)['result']
    pricelist = []
    #retrieve price information from priceprofile
    for pp in priceprofile:
        pricelist.append(pp['Price'])
    #total the prices from the profile and average them
    total = 0
    for p in pricelist:
        total += p
    #calculate the average of all retrieved prices
    return total/len(pricelist)

#carries out transactions
def transaction():
    global ethflag
    #initially, funds are in BTC
    #iterates through list of coins in while true loop
    currencyIterator = iter(currencylist)
    while 1:
        # move to the next coin in the list
        coin = '' + currencyIterator.__next__()
        det = calculation(coin)

        if det == 1:
            print("DO IT")
            if ethflag == 0:
                ethflag =1
            else:
                ethflag =0
        else:
            print("DONT DO IT")
        print(ethflag)



def calculation(x):
    global initialBalance
    global ethflag

    if ethflag==0:
        c1='BTC'
        c2='ETH'
    else:
        c1='ETH'
        c2='BTC'
    # find c1 balance from account - now hard coded, will be changed to reflect account balances
    print("Initial balance: ", initialBalance, c1)
    # find approx quantity of altcoin that can be purchased with your balance
    quantity = initialBalance/getValue(c1, x)
    print(x, ", ", quantity)

    # buy c2 with this quantity of altcoin based on exchange rate
    c2Balance = quantity * getValue(c2, x)
    print(c2Balance)
    #calculate new balance
    #newBalance = (c2Balance * getValue('BTC', 'ETH')) / initialBalance
    if ethflag == 0:
        c2Value = c2Balance * (getValue('BTC', 'ETH'))
    else:
        c2Value = c2Balance / (getValue('BTC', 'ETH'))
    print("Resulting value:", c2Value, " ", c1, "\n")
    #if the ending balance exceeds the beginning, return 1 to signify that trade is advised.  otherwise, return 0
    if initialBalance < c2Value:
        initialBalance = c2Balance
        return 1
    else:
        return 0

run()