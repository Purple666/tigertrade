#links to acct with api key
from bittrex import Bittrex
mybittrex = Bittrex(None, None)

#used in getting BTC balance from account - initializaed to 1 for testing purposes
initialBalance = 1
#used to distinguish what currency your holdings are currently in; begins as BTC but can be changed
ethflag = 0

currencylist = ['LTC', 'DASH', 'XMR', 'DGB', 'BTS', 'XRP', 'XEM', 'XLM', 'FCT', 'DGD', 'WAVES', 'ETC', 'STRAT', 'SNGLS', 'REP', 'NEO', 'ZEC', 'TIME', 'GNT', 'LGD', 'TRST', 'WINGS', 'RLC', 'GNO', 'GUP', 'LUN', 'TKN', 'HMQ', 'ANT', 'SC', 'BAT', '1ST', 'QRL', 'CRB', 'PTOY', 'MYST', 'CFI', 'BNT', 'NMR', 'SNT', 'MCO', 'ADT', 'FUN', 'PAY', 'MTL', 'STORJ', 'ADX', 'OMG', 'CVC', 'QTUM', 'BCC']

def run():
    #getBalance()
    transaction()

'''
#retrieves balance information from account based on api key/secret
def getBalance():
    global initialBalance
    balance = mybittrex.get_balance('BTC')['result']
    initialBalance = balance['Balance']

#dynamically retrieve ETH tradable currencies and stores stock symbols......takes forever.

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
    priceprofile = mybittrex.get_market_history(market)['result']
    pricelist = []
    #retrieve price information from priceprofile
    for pp in priceprofile:
        pricelist.append(pp['Price'])
    #average the prices from the profile and return
    total = 0
    for p in pricelist:
        total += p
    return total/len(pricelist)

#carries out transactions
def transaction():
    global ethflag
    #iterates through list of coins
    currencyIterator = iter(currencylist)
    coin = '' + currencyIterator.__next__()
    while 1:
        #determine if the transaction is profitable
        det = calculation(coin)
        #if it's profitable, complete the transaction and change the flag to swap BTC/ETH
        if det == 1:
            print("^DO IT^\n")
            ethflag = not ethflag
        #if it's not profitable, do not advise
        else:
            print("^DONT DO IT^\n")
        # attempt to move to the next altcoin in the list
        try:
            coin = ''+currencyIterator.__next__()
        #in the event there is none, check if it is profitable to buy BTC/ETH with current holdings
        except StopIteration:
            finalTrans('BTC', 'ETH')
            #create new iterator and begin again
            currencyIterator = iter(currencylist)
            coin = '' + currencyIterator.__next__()

def finalTrans(c1, c2):
    global ethflag
    global initialBalance
    print("Initial balance: ", initialBalance, c1)
    quantity1 = (initialBalance*getValue('USDT', c1))
    print(quantity1)
    if(ethflag==0):
        quantity2 = (initialBalance/getValue('BTC', 'ETH'))-.0025*(initialBalance/getValue('BTC', 'ETH'))
        compquantity=quantity2*getValue('USDT', c2)
    else:
        quantity2 = initialBalance*getValue('BTC', 'ETH')-.0025*(initialBalance*getValue('BTC', 'ETH'))
        compquantity = quantity2*getValue('USDT', c2)
    print(compquantity)
    diff = (compquantity / initialBalance)
    if diff>quantity1:
        initialBalance = quantity2
        print("^DO IT^\n")
        ethflag=not ethflag
    else:
        print("^DONT DO IT^\n")

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
    #simulate trade with a local balance (so not to actually adjust the balance)
    #account for fee
    altbalance = (initialBalance/getValue(c1, x))-.0025*(initialBalance/getValue(c1, x))
    print(x, ", ", altbalance)
    # buy c2 with this quantity of altcoin based on exchange rate and account for second fee
    c2Balance = (altbalance*getValue(c2, x))-.0025*(altbalance*getValue(c2, x))
    print(c2Balance)
    #calculate new balance by converting and comparing to initial currency balance
    if ethflag == 0:
        c2ValueInc1 = (c2Balance * (getValue(c1, c2)))
    else:
        c2ValueInc1 = (c2Balance / (getValue(c2, c1)))
    #calculate percent difference after trades
    diff = (c2ValueInc1 / initialBalance)
    print("Percent change: ", diff, "%")
    #determine if trade is advisable
    if diff>1:
        initialBalance = c2Balance
        return 1
    else:
        return 0
