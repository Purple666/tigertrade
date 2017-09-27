from bittrex import Bittrex
bitty = Bittrex("7f138b67561e4614b5897a93905e1657", "cc430dd6403f4064810d7338ba2c6dc1")
import time, json, datetime, siberian


def arbitage_loop():
    currencylist = ['LTC', 'DASH', 'XMR', 'DGB', 'BTS', 'XRP', 'XEM', 'XLM', 'FCT', 'DGD', 'WAVES', 'ETC', 'STRAT',
                    'SNGLS', 'REP', 'NEO', 'ZEC', 'TIME', 'GNT', 'LGD', 'TRST', 'WINGS', 'RLC', 'GNO', 'GUP', 'LUN',
                    'TKN', 'HMQ', 'ANT', 'SC', 'BAT', '1ST', 'QRL', 'CRB', 'PTOY', 'MYST', 'CFI', 'BNT', 'NMR', 'SNT',
                    'MCO', 'ADT', 'FUN', 'PAY', 'MTL', 'STORJ', 'ADX', 'OMG', 'CVC', 'QTUM', 'BCC']
    liquidity_asset, liquidity_bal = init_liquidity_asset()
    while True:
        for curr in currencylist:
            result, depth, rate, rate2 = evaluate_tx(curr,liquidity_asset, liquidity_bal)
            if result > liquidity_bal:
                print(curr, "after: ", result, "\n", depth, liquidity_asset, rate)
                liquidity_asset = put_ask(curr, depth, liquidity_asset, rate, rate2)
                if liquidity_asset == "timeout":
                    print("timeout, open order has not been filled")
                    break



def evaluate_tx(curr, liquidity_asset, bal):
    ethp_in_eth = siberian.avg_mkt_p("ETH-"+curr, count = 5)
    btc_to_eth = siberian.avg_mkt_p("BTC-ETH", count = 5)
    btcp_in_btc = siberian.avg_mkt_p("BTC-"+curr,count=5)
    if liquidity_asset == "BTC":
        mkt_p = siberian.avg_mkt_p("BTC-"+curr,count=5)
        buy_depth_at_price = (bal / mkt_p) * BITTREX_FEE()
        #print("This many "+ curr +": " + str(buy_depth_at_price))
        sell_result = buy_depth_at_price * ethp_in_eth * BITTREX_FEE()
        result_in_terms_of_liquidity_asset = sell_result*btc_to_eth
        print(curr + ": You end up with this many ETH: " + str(sell_result) + ". Which is equal to this many BTC: " + str(result_in_terms_of_liquidity_asset)+"Starting with "+ str(bal))
        return (result_in_terms_of_liquidity_asset, buy_depth_at_price, mkt_p, ethp_in_eth)
        #
    elif liquidity_asset == "ETH":
        mkt_p = siberian.avg_mkt_p("ETH-"+curr, count = 5)
        buy_depth_at_price = (bal / mkt_p) * BITTREX_FEE()
        #print("This many " + curr + ": " + str(buy_depth_at_price))
        sell_result = buy_depth_at_price * btcp_in_btc * BITTREX_FEE()
        result_in_terms_of_liquidity_asset = sell_result * btc_to_eth
        print("You end up with this many BTC: " + str(sell_result) + ". Which is equal to this many ETH: " + str(result_in_terms_of_liquidity_asset)+"Starting with "+ str(bal))
        return(result_in_terms_of_liquidity_asset, buy_depth_at_price, mkt_p, btcp_in_btc)


def put_ask(curr, depth, asset, price, price2):
    bitty.buy_limit(asset+"-"+curr, depth, price)
    wait = 0
    while wait < 15:
        oList = bitty.get_open_orders(asset + "-" + curr)['result']
        if oList:
            wait += 1
            print("Alt order outstanding")
        else:
            if asset == "BTC":
                asset = "ETH"
            if asset == "ETH":
                asset = "BTC"
            break
        time.sleep(1)
    if wait == 15:
        for o in oList:
            orderId = o['Id']
        bitty.cancel(orderId)
        return(asset)
    else:
        bitty.sell_limit(asset+"-"+curr, depth*BITTREX_FEE(), price2)
        wait = 0
        while wait < 300:
            oList = bitty.get_open_orders(asset + "-" + curr)['result']
            if oList:
                wait += 1
                print(oList+"Main order outstanding")
            else:
               return(asset)
            time.sleep(5)
        if wait == 300:
            return("timeout")


def BITTREX_FEE():
    return(.9975)

def init_liquidity_asset():
    eth_bal = bitty.get_balance("ETH")['result']['Balance']
    btc_bal = bitty.get_balance("BTC")['result']['Balance']
    if eth_bal > btc_bal:
        return("ETH", eth_bal*.1)
    if eth_bal < btc_bal:
        return("BTC", btc_bal*.1)
    else:
        return(None)
def main():
    arbitage_loop()

if __name__ == "__main__":
    main()