from futuquant import *

RET_OK = 0
RET_ERR = -1
MARKET_HK = 'HK'
CODE_HK_FUTURE = 'HK_FUTURE.999010'
CODE_HK_HSI = 'HK.800000'
CODE_HK_BULL = 'HK.64033'
CODE_HK_BEAR = 'HK.58854'
class quote_api:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connect(self):
        try:
            self.quote_ctx = OpenQuoteContext(host=self.host, port=self.port)
        except:
            print("Connect err")
            return RET_ERR
        return RET_OK

    def disconnect(self):
        try:
            self.quote_ctx.close()
        except:
            print("Disconnect err")
            return RET_ERR
        return RET_OK

#['2018-04-12', '2018-04-11', '2018-04-10', '2018-04-09',
    def get_last_trade_day(self):
        ret_code, ret_data = self.quote_ctx.get_trading_days(MARKET_HK, start_date=None, end_date=None)
        if ret_code != RET_OK:
            print(ret_data)
            return RET_ERR, ''
        return RET_OK, ret_data[0]

    def subscribe(self, stock_code, data_type):
        ret_code, ret_data = self.quote_ctx.subscribe(stock_code, data_type, push=False)
        if ret_code != RET_OK:
            print(ret_data)
            return RET_ERR
        return RET_OK

# code   data_date data_time  last_price  open_price  high_price  \
# 0  HK_FUTURE.999010  2018-04-12  16:05:37     30834.0         0.0         0.0
#   low_price  prev_close_price  volume      turnover  turnover_rate  \
# 0        0.0           30891.0       0  6.443698e+09            0.0
#   amplitude  suspension listing_date  price_spread
# 0        0.0       False   1970-01-01           1.0
    def get_quote(self, code_list):
        ret_code, ret_data = self.quote_ctx.get_stock_quote(code_list)
        if ret_code != RET_OK:
            print(ret_data)
            return RET_ERR, ret_data
        return RET_OK, ret_data

    def get_hkfuture_time(self):
        ret_code, ret_data = self.get_quote([CODE_HK_FUTURE])
        if ret_code != RET_OK:
            print(ret_data)
            return RET_ERR, ''
        try:
            data_time = ret_data["data_time"][0]
        except:
            return RET_ERR, ''
        return RET_OK, data_time

# code             time_key      open     close      high       low  \
# 0  HK.800000  2018-03-27 00:00:00  30985.75  30790.83  30985.75  30738.76
# 1  HK.800000  2018-03-28 00:00:00  30510.38  30022.53  30637.21  30022.53
#  volume      turnover  pe_ratio  turnover_rate
# 0      0  1.352888e+11       0.0            0.0
# 1      0  1.426439e+11       0.0            0.0
    def get_day_k(self, code, num, ktype ='K_DAY'):
        ret_code, ret_data = self.quote_ctx.get_cur_kline(code, num, ktype, autype='qfq')
        if ret_code != RET_OK:
            print(ret_data)
            return RET_ERR, ret_data
        return RET_OK, ret_data


    def get_brokers(self, stock_code):
        ret_code, bid_data, ask_data = self.quote_ctx.get_broker_queue(stock_code)
        if ret_code != RET_OK:
            print(bid_data)
            return RET_ERR, [], []
        return RET_OK, bid_data, ask_data

#{'stock_code': 'HK.65622', 'Ask': [(0.71, 30000000, 1), (0.72, 0, 0), (0.73, 0, 0), (0.74, 12000000, 1), (0.75, 0, 0), (0.76, 0, 0), (0.77, 0, 0), (0.78, 0, 0), (0.79, 0, 0), (0.8, 0, 0)], 'Bid': [(0.67, 30000000, 1), (0.66, 0, 0), (0.65, 0, 0), (0.64, 12000000, 1), (0.63, 0, 0), (0.62, 0, 0), (0.61, 0, 0), (0.6, 0, 0), (0.59, 0, 0), (0.58, 0, 0)]}

    def get_book(self, stock_code):
        ret_code, ret_data = self.quote_ctx.get_order_book(stock_code)
        if ret_code != RET_OK:
            print(ret_data)
            return RET_ERR, -1, -1
        return RET_OK, ret_data["Bid"][0][0], ret_data["Ask"][0][0]

    def get_market_snapshot(self, code_list):
        ret_code, ret_data = self.quote_ctx.get_market_snapshot(["HK.800000"])
        if ret_code != 0:
            return RET_ERR, ret_data
        return RET_OK, ret_data

    def get_stock_basicinfo(self, mkt, stock_type):
        ret_code, ret_data = self.quote_ctx.get_stock_basicinfo(mkt, stock_type=stock_type)
        if ret_code != 0:
            return RET_ERR, ret_data
        return RET_OK, ret_data

################### Test
if __name__ == "__main__":
    API_RM_SVR_IP = '119.29.141.202'
    API_LO_SVR_IP = '127.0.0.1'
    q = quote_api(API_LO_SVR_IP, 11111)
    ret = q.connect()
    if ret != RET_OK:
        print("Connect ERR")
        exit(0)
    print("Connected")

    ret, last_day = q.get_last_trade_day()
    if ret != RET_OK:
        print("get_last_trade ERR")
        exit(0)
    print("get_last_trade")

    code_future = CODE_HK_FUTURE
    ktype_future = "QUOTE"
    ret = q.subscribe(code_future, ktype_future)
    if ret != RET_OK:
        print("subscribe ERR")
        exit(0)
    print("subscribe " + code_future)

    code_hsi = CODE_HK_HSI
    ktype_hsi = "K_DAY"
    ret = q.subscribe(code_hsi, ktype_hsi)
    if ret != RET_OK:
        print("subscribe ERR")
        exit(0)
    print("subscribe " + code_hsi)

    ret, ret_data = q.get_quote([code_future])
    if ret != RET_OK:
        print("get_quote ERR")
        exit(0)
    print("get_quote " + code_future)

    ret, ret_data = q.get_day_k(code_hsi, 10)
    if ret != RET_OK:
        print("get_day_k ERR")
        exit(0)
    print("get_day_k " + code_hsi)

    code_bear = 'HK.65622'
    ktype_future = "BROKER"
    ret = q.subscribe(code_bear, ktype_future)
    if ret != RET_OK:
        print("subscribe ERR")
        exit(0)
    print("subscribe " + code_future)

    ret, bid_data, ask_data = q.get_brokers(code_bear)
    print(ret)
    if ret != RET_OK:
        print("get_brokers ERR")
        exit(0)
    for i in range(0, len(bid_data.index) - 1):
        bid_broker_pos = bid_data["bid_broker_pos"][i]
        bid_broker_id = bid_data["bid_broker_id"][i]

        if bid_broker_pos == '0' and \
                        bid_broker_id[0] == '9' and bid_broker_id[1] == '7':
            bid_ok = True
            print("BID OK")

    for i in range(0, len(ask_data.index) - 1):
        ask_broker_pos = ask_data["ask_broker_pos"][i]
        ask_broker_id = ask_data["ask_broker_id"][i]

        if ask_broker_pos == '0' and \
                        ask_broker_id[0] == '9' and ask_broker_id[1] == '7':
            ask_ok = True
            print("ASK OK")

    # code bid_broker_id bid_broker_name bid_broker_pos
    # 0  HK.58854          9716          J.P.摩根              0
    # 1  HK.58854          8519              荷银              0
    # 2  HK.58854          9023              瑞银              1
    # 3  HK.58854          9716          J.P.摩根              1
    # 4  HK.58854          8519              荷银              1
    # 5  HK.58854          9023              瑞银              2
    # 6  HK.58854          9716          J.P.摩根              2
    # 7  HK.58854          4637              致富              8
    # 8  HK.58854          9063              瑞银             11
    # code ask_broker_id ask_broker_name ask_broker_pos
    # 0  HK.58854          2249            富途证券              0
    # 1  HK.58854          9716          J.P.摩根              0
    # 2  HK.58854          8519              荷银              0
    # 3  HK.58854          8519              荷银              1
    # 4  HK.58854          9024              瑞银              4
    # 5  HK.58854          9024              瑞银              5

    code_bear = 'HK.58929'
    ktype = "ORDER_BOOK"
    ret = q.subscribe(code_bear, ktype)
    if ret != RET_OK:
        print("subscribe ERR")
        exit(0)
    print("subscribe " + code_bear + " " + ktype)

    ret, bid, ask = q.get_book(code_bear)
    if ret != RET_OK:
        print("get_book ERR")
        exit(0)
    print(bid)
    print(ask)
    print("book ")
    narrow = int(ask * 1000 - bid * 1000)
    if narrow == 1:
        print("OK")