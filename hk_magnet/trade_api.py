from futuquant import *
import time

RET_OK = 0
RET_ERR = -1

TRADE_TYPE_SIMU = 1
TRADE_TYPE_REAL = 0

TRADE_SIDE_BUY  = 0
TRADE_SIDE_SELL = 1

class trade_api:
    def __init__(self, host, port, envtype):
        self.host = host
        self.port = port
        self.envtype = envtype

    def connect(self):
        try:
            self.tradehk_ctx = OpenHKTradeContext(self.host, self.port)
        except:
            return RET_ERR
        return RET_OK

    def disconnect(self):
        try:
            self.tradehk_ctx.close()
        except:
            return RET_ERR
        return  RET_OK

    def unlock(self, trade_password):
        ret_code, ret_data = self.tradehk_ctx.unlock_trade(trade_password)
        if ret_code != RET_OK:
            return RET_ERR
        return RET_OK

    def place_order(self, price, qty, strcode, orderside):
        ret_code, ret_data = self.tradehk_ctx.place_order(price, qty, strcode, orderside,
                                                          ordertype=0, envtype=self.envtype,
                                                          order_deal_push=False, price_mode=0)
        if ret_code != RET_OK :
            print(ret_data)
            return RET_ERR, ''
        orderid = ret_data["orderid"][0]
        return RET_OK, orderid

    def modify(self, price, qty, orderid):
        ret_code, ret_data = self.tradehk_ctx.change_order(price, qty, orderid, envtype=self.envtype)
        if ret_code != RET_OK:
            print(ret_data)
            return RET_ERR
        return RET_OK

    def query_order(self, orderid):
        status = -100
        ret_code, ret_data = self.tradehk_ctx.order_list_query(orderid=orderid,
                                                          statusfilter="", strcode='', start='', end='',
                                                          envtype=self.envtype)
        if ret_code != RET_OK:
            return RET_ERR, status

        try:
            status = int(ret_data["status"][0])
        except:
            status = -1
        return RET_OK, status

    def query_order_dealt(self, orderid):
        dealt_qty = -100
        ret_code, ret_data = self.tradehk_ctx.order_list_query(orderid=orderid,
                                                          statusfilter="", strcode='', start='', end='',
                                                          envtype=self.envtype)
        if ret_code != RET_OK:
            return RET_ERR, dealt_qty

        try:
            dealt_qty = int(ret_data["dealt_qty"][0])
        except:
            dealt_qty = -1
            return RET_ERR, dealt_qty
        return RET_OK, dealt_qty

######## TEST
if __name__ == "__main__":
    API_RM_SVR_IP = '119.29.141.202'
    API_LO_SVR_IP = '127.0.0.1'
    broker = trade_api(API_RM_SVR_IP, 11111, TRADE_TYPE_SIMU)
    ret = broker.connect()
    if ret != RET_OK:
        print("Connect ERR")
        exit(0)
    print("Connected")

    # ret = broker.unlock('111111')
    if ret != RET_OK:
        print("Unlock ERR")
        exit(0)
    print("Unlocked")

    stock_code = 'HK.00700'
    price = 413
    qty = 100
    ret, orderid = broker.trade(price, qty, stock_code, TRADE_SIDE_BUY)
    if ret != RET_OK:
        print("Buy ERR")
        exit(0)
    print("Bought Placed")

    time.sleep(2)
    ret, status = broker.query_order(orderid)
    if ret != RET_OK:
        print("Query ERR")
        exit(0)
    print("Status: " + str(status))

    time.sleep(1)
    new_price = 420
    ret = broker.modify(new_price, qty, orderid)
    if ret != RET_OK:
        print("Modify ERR")
        exit(0)
    print("Modified")

    time.sleep(2)
    ret, status = broker.query_order(orderid)
    if ret != RET_OK:
        print("Query ERR")
        exit(0)
    print("Status: " + str(status))

    ret, orderid = broker.trade(new_price - 1, qty, stock_code, TRADE_SIDE_SELL)
    if ret != RET_OK:
        print("SELL ERR")
        exit(0)
    print("SELL Placed")

    time.sleep(2)
    ret, status = broker.query_order(orderid)
    if ret != RET_OK:
        print("Query ERR")
        exit(0)
    print("Status: " + str(status))
    if status == '3':
        print("char")
    if status == 3:
        print("int")
    ret = broker.disconnect()