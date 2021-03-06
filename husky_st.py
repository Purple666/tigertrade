from bittrex import Bittrex
bitty = Bittrex("", "")
import time, json, datetime, siberian


def arbitage_loop():
    currencylist = ['LTC', 'DASH', 'XMR', 'DGB', 'BTS', 'XRP', 'XEM', 'XLM', 'FCT', 'DGD', 'WAVES', 'ETC', 'STRAT',
                    'REP', 'NEO', 'ZEC', 'GNT', 'LGD', 'WINGS', 'GNO',
                    'TKN', 'HMQ', 'ANT', 'SC', 'BAT', 'QRL', 'PTOY', 'MYST', 'BNT',
                    'MCO', 'MTL', 'STORJ', 'QTUM', 'BCC']
    #liquidity_asset, liquidity_bal = init_liquidity_asset()
    i=5
    while True:
        for curr in currencylist:
            if i == 5:
                liquidity_asset, liquidity_bal = init_liquidity_asset()
                i=0
            i+=1
            result, depth, rate, rate2 = evaluate_tx(curr,liquidity_asset, liquidity_bal)
            if result > liquidity_bal:
                print("***"+curr + " trade process initiated, submitting order and waiting for it to be filled.***")
                liquidity_asset = put_ask(curr, depth, liquidity_asset, rate, rate2)
                if liquidity_asset == "timeout":
                    print("Timeout, open order has not been filled")
                    break




def switch_asset(asset, bal):
    if asset == "BTC":
        bitty.buy_limit("BTC-ETH", bal, siberian.ask("BTC-ETH")/TOLERANCE())
    if asset == "ETH":
        bitty.sell_limit("BTC-ETH", bal, siberian.ask("BTC-ETH")*TOLERANCE())


def evaluate_tx(curr, liquidity_asset, bal):
    ask_in_eth = siberian.ask("ETH-"+curr)/TOLERANCE()
    bid_in_eth = siberian.bid("ETH-"+curr)*TOLERANCE()
    ask_btc_eth = siberian.ask("BTC-ETH")#/TOLERANCE()
    bid_btc_eth = siberian.bid("BTC-ETH")#*TOLERANCE()
    ask_in_btc = siberian.ask("BTC-"+curr)/TOLERANCE()
    bid_in_btc = siberian.bid("BTC-"+curr)*TOLERANCE()


    if liquidity_asset == "BTC":
        buy_depth_at_price = (bal / ask_in_btc) * BITTREX_FEE()
        sell_result = buy_depth_at_price * bid_in_eth * BITTREX_FEE()
        result_in_terms_of_liquidity_asset = sell_result * ask_btc_eth
        print(curr + ": You end up with this many ETH: " + str(sell_result) + ". Which is equal to this many BTC: " + str(result_in_terms_of_liquidity_asset)+". Starting with "+ str(bal) + " BTC.")
        return (result_in_terms_of_liquidity_asset, buy_depth_at_price, ask_in_btc, bid_in_eth)

    elif liquidity_asset == "ETH":
        buy_depth_at_price = (bal / ask_in_eth) * BITTREX_FEE()
        sell_result = buy_depth_at_price * bid_in_btc * BITTREX_FEE()
        result_in_terms_of_liquidity_asset = sell_result / bid_btc_eth
        print(curr + " You end up with this many BTC: " + str(sell_result) + ". Which is equal to this many ETH: " + str(result_in_terms_of_liquidity_asset)+". Starting with "+ str(bal) + " ETH.")
        return(result_in_terms_of_liquidity_asset, buy_depth_at_price, ask_in_eth, bid_in_btc)

def TOLERANCE():
    #(0,1) the leeway allowed when calculating profitability, the closer to 1 the higher chance of orders not being filled
    return(.9999)

def put_ask(curr, depth, asset, price, price2):
    """Constructs a set of orders with the hopes of increasing dollar amount

    This function can be a bit difficult to wade through, but the premise is that we call it once we determine that a
    trade should be profitable(evaluate_tx), it puts in an order with the values given to it. It waits to see if the
    order can be quickly filled, if not it cancels the order. Hopefully it does actually fill, in which case we change
    the asset variable, get the balance of that alt we converted to, and put in an order for either ETH or BTC, the
    opposite of what we had in the beginning. This order has a time limit of ten minutes after which the program times
    out.

    curr: a string such as "VTC" denoting the altcoin involved in this trade
    depth: The amount of altcoin to originally purchase in the first transaction, should be generated by evaluate_tx()
    asset: either BTC or ETH, whichever we are converting FROM, init_liquidity_asset() handles this
    price: the price for transaction1, evaluate_tx() should provide this
    price2: the price of transaction2, evaluate_tx() should provide this
    """
    #Transaction 1
    tmp_list = bitty.buy_limit(asset+"-"+curr, depth, price)
    time.sleep(5) #wait for network latency
    wait = 0
    while wait < 15:
        oList = bitty.get_open_orders(asset + "-" + curr)['result']
        if oList: #if there are orders open, wait until 15
            wait += 1
            print("Alt order outstanding")
        else:#order is filled, switch liquidity assets
            break
        time.sleep(1)
    print(wait)
    if wait == 15: #if it's been 15 seconds and the order is not filled, cancel it

        for o in oList:
            orderId = o['OrderUuid']
        bitty.cancel(orderId)
        time.sleep(5)
        if asset == "BTC":
            asset = "ETH"
        elif asset == "ETH":
            asset = "BTC"
        bal_result = bitty.get_balance(curr)['result']  # gets exact balance of the altcoin, including dust
        depth_to_main = bal_result['Balance']
        print("Order canceled, submitting sell order for any quantity filled.")
        bitty.sell_limit(asset + "-" + curr, depth_to_main, price2)
        return(asset) #back to searching

    if asset == "BTC":
        asset = "ETH"
    elif asset == "ETH":
        asset = "BTC"

    #Transaction 2
    bal_result = bitty.get_balance(curr)['result']  # gets exact balance of the altcoin, including dust
    depth_to_main = bal_result['Balance']
    print(depth_to_main)
    print("Submitting transaction 2, please wait, this may take a while.")
    tmp_list = bitty.sell_limit(asset + "-" + curr, depth_to_main, price2)
    while tmp_list['success'] == False:
        print("Order failed.")
        time.sleep(5)
        tmp_list = bitty.sell_limit(asset + "-" + curr, depth_to_main, price2)

    time.sleep(15)#wait for latency
    wait = 5
    oList= []
    while wait < 86400: #wait ten minutes
        oList = bitty.get_open_orders(asset + "-" + curr)['result']
        if oList:
            wait += 5
            if wait % 60 == 0:
                price2 = recast_lower_sell(oList, asset, curr, price2)
            #elif wait > 675:
            #    price2 = recast_lower_sell(oList, asset, curr, depth_to_main, price2)
            print("Main order outstanding")
        else:
           return(asset)
        time.sleep(5)
    if wait == 86400:
        return("timeout")

def recast_lower_sell(oList, asset, curr, price):

    print("Order not filled, recasting at a lower price (sorry).")
    for o in oList:
        orderId = o['OrderUuid']
    bitty.cancel(orderId)
    time.sleep(10)
    bal_result = bitty.get_balance(curr)['result']  # gets exact balance of the altcoin, including dust
    depth = bal_result['Balance']
    price = price * TOLERANCE()
    bitty.sell_limit(asset + "-" + curr, depth, price)
    time.sleep(5)
    return(price)

def BITTREX_FEE():
    return(.9975)

def init_liquidity_asset():
    eth_bal = bitty.get_balance("ETH")['result']['Balance']
    btc_bal = bitty.get_balance("BTC")['result']['Balance']
    if eth_bal > btc_bal:
        return("ETH", eth_bal)
    if eth_bal < btc_bal:
        return("BTC", btc_bal)
    else:
        return(None)

def main():
    arbitage_loop()

if __name__ == "__main__":
    main()
