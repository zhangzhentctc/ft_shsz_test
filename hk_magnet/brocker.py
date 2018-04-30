from hk_magnet.localtime_api import *
from hk_magnet.quote_api import *
from hk_magnet.trade_api import *
from hk_magnet.ret_sender import *

#### Customers
UNLOCK_PASSWD = ''
EMAIL_PASSWD = ''
CODE_HK_BULL = 'HK.64033'
CODE_HK_BEAR = 'HK.59628'
TRADE_AMOUNT = 5

#### Systems
TIME_SET_REAL = 1
TIME_SET_TEST = 2
timesets = TIME_SET_REAL
if timesets == TIME_SET_REAL:
    TIME_START_WORK    = '09:25:00'
    TIME_CONN_DEADLINE = '09:29:00'
    TIME_PREP_DEADLINE = '09:31:00'
    TIME_MKT_OPEN = '09:30:00'
    TIME_STR_END = '09:45:00'
else:
    TIME_START_WORK    = '12:55:00'
    TIME_CONN_DEADLINE = '12:59:00'
    TIME_PREP_DEADLINE = '13:01:00'
    TIME_MKT_OPEN = '13:00:00'
    TIME_STR_END = '13:15:00'

HOST = '127.0.0.1'
PORT = 11111
TRADE_TYPE_SIMU = 1
TRADE_TYPE_REAL = 0
CODE_HK_FUTURE = 'HK_FUTURE.999010'
CODE_HK_HSI = 'HK.800000'
MARKET_HK = 'HK'

TIME_CMP_BIGGER = 1
TIME_CMP_EQUAL = 0
TIME_CMP_SMALLER = -1

DATA_TYPE_QUO = "QUOTE"
DATA_TYPE_BROKER = "BROKER"
DATA_TYPE_KDAY = "K_DAY"
DATA_TYPE_BOOK = "ORDER_BOOK"

DIR_BEAR = -1
DIR_BULL = 1

TRADE_SIDE_BUY  = 0
TRADE_SIDE_SELL = 1

ERR_NOT_TRADE_DAY = 10001
ERR_PREP_TIMEOUT = 10002
ERR_NOT_DEALT = 10003

ORDER_PROCESSING = 0
ORDER_SENT = 21

ORDER_INVALID = 4
ORDER_FAILURE = 5
ORDER_WITHDRAWED = 6
ORDER_DELETED = 7
ORDER_WAIT_OPEN = 8

ORDER_SRV_FAIL = 22
ORDER_SRV_TIMEOUT = 23

ORDER_WAIT = 1
ORDER_PARTLY = 2
ORDER_DEALT = 3

UNLOCK_PASSWD_FILE = './unlock.txt'

class brocker:
    def __init__(self):
        self.quote = quote_api(HOST, PORT)
        self.trade = trade_api(HOST, PORT, TRADE_TYPE_REAL)
        self.msg = ""
        try:
            file = open(UNLOCK_PASSWD_FILE, 'r')
            all_line_txt = file.readlines()
            self.unlock_passwd = all_line_txt[0].strip('\n')
        except:
            self.unlock_passwd = '123456'

    def rec_log(self, str):
        l = localtime_api()
        now_time = l.get_local_time()
        msg = "[" + now_time + "] " + str
        print(msg)
        self.msg = self.msg + msg + "\n\r"

    def get_local_time(self):
        l = localtime_api()
        return l.get_local_time()

    def get_local_date(self):
        l = localtime_api()
        return l.get_local_date()

## High Level
    def wait_for_start_work(self):
        self.rec_log("Wait for Start Working...")
        while True:
            local_time = self.get_local_time()
            if self.compare_time(local_time, TIME_START_WORK) == TIME_CMP_BIGGER or \
                            self.compare_time(local_time, TIME_START_WORK) == TIME_CMP_EQUAL:
                break
            else:
                time.sleep(60)
        return RET_OK

    def disconnect(self):
        self.rec_log("Done...")
        self.quote.disconnect()
        self.trade.disconnect()

    def connect_quote(self):
        success = False
        while True:
            self.rec_log("Connect Quote...")
            ret = self.quote.connect()
            if ret == RET_OK:
                success = True
                break
            else:
                self.rec_log("----Fail, wait for 10 seconds")
                time.sleep(10)
                local_time = self.get_local_time()
                if self.compare_time(local_time, TIME_CONN_DEADLINE) == TIME_CMP_SMALLER:
                    continue
                else:
                    self.rec_log("Connect Quote Timeout")
                    success = False
                    break
        if success == True:
            return RET_OK
        else:
            return RET_ERR

    def connect_trade(self):
        trial = 3
        success = False
        while trial > 0:
            self.rec_log("Connect Trade...")
            ret = self.trade.connect()
            if ret == RET_OK:
                success = True
                break
            else:
                self.rec_log("----Fail, wait for 3 seconds")
                time.sleep(3)
                trial -= 1
                continue
        if success == True:
            self.rec_log("Unlock...")
            ret = self.trade.unlock(self.unlock_passwd)
            if ret != RET_OK:
                return RET_ERR

            return RET_OK
        else:
            return RET_ERR

    def check_date(self):
        self.rec_log("Check Trade Date...")
        local_date = self.get_local_date()
        ret, last_trade_date = self.quote.get_last_trade_day()
        if ret != RET_OK:
            return RET_ERR
        if local_date.split('-')[2] == last_trade_date.split('-')[2]:
            return RET_OK
        else:
            self.rec_log("----Bad day")
            return ERR_NOT_TRADE_DAY

    def check_prep_time(self):
        self.rec_log("Check Prepare Time...")
        ret = self.quote.subscribe(CODE_HK_FUTURE, DATA_TYPE_QUO)
        if ret != RET_OK:
            return RET_ERR
        ret, data_time = self.quote.get_hkfuture_time()
        if ret != RET_OK:
            return RET_ERR

        if self.compare_time(data_time, TIME_PREP_DEADLINE) == TIME_CMP_SMALLER:
            return RET_OK
        else:
            self.rec_log("----Prepare Timeout")
            return ERR_PREP_TIMEOUT

    def process(self):
        ret = self.wait_for_start_work()
        if ret != RET_OK:
            self.rec_log("Wait for start ERR")
            return ret

        ret = self.connect_quote()
        if ret != RET_OK:
            self.rec_log("Conn Quote ERR")
            return ret

        ret = self.connect_trade()
        if ret != RET_OK:
            self.rec_log("Conn Trade ERR")
            return ret

        ret = self.check_date()
        if ret != RET_OK:
            self.rec_log("Check Date ERR")
            return ret

        #ret = self.check_prep_time()
        if ret != RET_OK:
            self.rec_log("Check Prep Time ERR")
            return ret

        ret = self.wait_for_open_mkt()
        if ret != RET_OK:
            self.rec_log("Wait for open mkt ERR")
            return ret

        ret = self.decide_dir()
        if ret != RET_OK:
            self.rec_log("Decide Direction ERR")
            return ret

        ret = self.check_warrent()
        if ret != RET_OK:
            self.rec_log("Check Warrent ERR")
            return ret

        ret = self.wait_for_open_warrent()
        if ret != RET_OK:
            self.rec_log("Wait for Warrent Open ERR")
            return ret

        ret = self.buy_warrent()
        if ret != RET_OK:
            self.rec_log("Buy Warrent ERR")
            return ret

        ret = self.wait_for_timer()
        if ret != RET_OK:
            self.rec_log("Wait for Timer ERR")
            return ret

        ret = self.sell_warrent()
        if ret != RET_OK:
            self.rec_log("Sell Warent ERR")
            return ret

        ##self.disconnect()

        return RET_OK



## Process Level
    def wait_for_open_mkt(self):
        success = False
        self.rec_log("Waiting for Market Open")
        ret = self.quote.subscribe(CODE_HK_FUTURE, DATA_TYPE_QUO)
        if ret != RET_OK:
            return RET_ERR, 0
        while True:
            ret, data_time = self.quote.get_hkfuture_time()
            if ret != RET_OK:
                success = False
                break

            if self.compare_time(data_time, TIME_MKT_OPEN) == TIME_CMP_BIGGER or \
                self.compare_time(data_time, TIME_MKT_OPEN) == TIME_CMP_EQUAL:
                success = True
                break
            else:
                time.sleep(1)
                continue

        if success == True:
            return RET_OK
        else:
            return RET_ERR


    def decide_dir(self):
        success = False
        self.rec_log("Decide Direction...")
        ret = self.quote.subscribe(CODE_HK_HSI, DATA_TYPE_KDAY)
        if ret != RET_OK:
            return RET_ERR, 0

        k_num = 2
        while True:
            ret, kline = self.quote.get_day_k(CODE_HK_HSI, k_num)
            if ret != RET_OK:
                success = False
                break

            last_close = int(kline["close"][k_num - 2])
            new_open = int(kline["open"][k_num - 1])
            if last_close > 10000 and new_open > 10000:
                success = True
                break
            else:
                time.sleep(1)
                continue

        if success == True:
            if new_open > last_close:
                dir = DIR_BEAR
                self.warrent = CODE_HK_BEAR
            else:
                dir = DIR_BULL
                self.warrent = CODE_HK_BULL
            return RET_OK
        else:
            return RET_ERR


    def check_warrent(self):
        self.rec_log("Checking Warrent")
        ret = self.quote.subscribe(self.warrent, DATA_TYPE_QUO)
        if ret != RET_OK:
            return RET_ERR
        ret = self.quote.subscribe(self.warrent, DATA_TYPE_BROKER)
        if ret != RET_OK:
            return RET_ERR
        ret = self.quote.subscribe(self.warrent, DATA_TYPE_BOOK)
        if ret != RET_OK:
            return RET_ERR
        ## WARRENT CHECK SKIP

        return RET_OK


    def start_trade(self):
        pass


## Trade_Level
    def wait_for_open_warrent(self):
        self.rec_log("----Wait for Warrent Open")
        waited_time = 0
        while waited_time < 360:
            ret, bid_data, ask_data = self.quote.get_brokers(self.warrent)
            if ret != RET_OK:
                success = False
                break
            bid_ok = False
            ask_ok = False
            for i in range (0, len(bid_data.index)):
                bid_broker_pos = bid_data["bid_broker_pos"][i]
                bid_broker_id = bid_data["bid_broker_id"][i]
                if bid_broker_pos == '0' and \
                    bid_broker_id[0]== '9' and bid_broker_id[1] == '7':
                    bid_ok = True

            for i in range (0, len(ask_data.index)):
                ask_broker_pos = ask_data["ask_broker_pos"][i]
                ask_broker_id = ask_data["ask_broker_id"][i]
                if ask_broker_pos == '0' and \
                    ask_broker_id[0]== '9' and ask_broker_id[1] == '7':
                    ask_ok = True
            if bid_ok == True and ask_ok == True:
                success = True
                break
            else:
                time.sleep(1)
                waited_time += 1
                continue

        if success == True:
            return RET_OK
        else:
            return RET_ERR

    def wait_for_narrow(self):
        self.rec_log("----Wait for narrow")
        success = False
        while True:
            ret, bid, ask = self.quote.get_book(self.warrent)
            if ret != RET_OK:
                return RET_ERR, 0, 0
            narrow = ask * 1000 - bid * 1000
            if narrow == 1:
                success = True
                break
            else:
                time.sleep(1)
                continue

        if success == True:
            return RET_OK, bid, ask
        else:
            return RET_ERR, 0, 0

    def make_order(self, warrent_code, dir):
        success = False
        flag_modify_fail = False
        dealt = 0
        qty = TRADE_AMOUNT * 10000
        while True:
            self.rec_log("----Make Order")
            ## Place Order
            ret = self.wait_for_open_warrent()
            if ret != RET_OK:
                return RET_ERR

            ret, bid, ask = self.wait_for_narrow()
            if ret != RET_OK:
                return RET_ERR

            if dir == TRADE_SIDE_BUY:
                price = ask
            elif dir == TRADE_SIDE_SELL:
                price = bid
            else:
                return RET_ERR

            self.rec_log("----Place Order: " + str(dir) + " " + str(warrent_code) + " " + str(price) + " " + str(qty))
            ret, orderid = self.trade.place_order(price, qty, warrent_code, dir)
            if ret != RET_OK:
                return RET_ERR

            while True:
                # Check Status
                ret, status = self.trade.query_order(orderid)
                if ret != RET_OK:
                    self.rec_log("Query Order ERR")
                    return RET_ERR

                if status == ORDER_PROCESSING or status == ORDER_SENT:
                    self.rec_log("----Order Processing: status=" + str(status))
                    time.sleep(1)
                    continue
                else:
                    break

            if status == ORDER_SRV_TIMEOUT or status == ORDER_SRV_FAIL or \
                status == ORDER_DELETED or status == ORDER_FAILURE or \
                status == ORDER_WITHDRAWED or status == ORDER_INVALID:
                self.rec_log("----Order Fail: status=" + str(status) + " Try Again")
                continue

            elif status == ORDER_DEALT:
                self.rec_log("----Order Dealt")
                success = True
                break

            else:
                self.rec_log("----Order Waiting status="  + str(status))
                while True:
                    time.sleep(3)
                    ret, status = self.trade.query_order(orderid)
                    if ret != RET_OK:
                        self.rec_log("Query Order ERR")
                        return RET_ERR

                    if status == ORDER_DEALT:
                        self.rec_log("--------Order Dealt")
                        success = True
                        break
                    elif status == ORDER_WAIT or status == ORDER_PARTLY:
                        self.rec_log("--------Order Not All Dealt")
                        ## Modify Order
                        ret = self.wait_for_open_warrent()
                        if ret != RET_OK:
                            return RET_ERR

                        ret, bid, ask = self.wait_for_narrow()
                        if ret != RET_OK:
                            return RET_ERR

                        if dir == TRADE_SIDE_BUY:
                            price = ask
                        elif dir == TRADE_SIDE_SELL:
                            price = bid
                        self.rec_log("--------Modify Price " + str(dir) + " " + str(warrent_code) + " " + str(price) + " " + str(qty))
                        ret = self.trade.modify(price, qty, orderid)
                        if ret != RET_OK:
                            flag_modify_fail = True
                            ret, dealt = self.trade.query_order_dealt(orderid)
                            if ret != RET_OK:
                                self.rec_log("Query Order ERR")
                                return RET_ERR
                            break
                        ## Modify Success
                        continue

                if flag_modify_fail == True:
                    qty = qty - dealt
                    continue

                if success == True:
                    break

        if success == True:
            return RET_OK
        else:
            return RET_ERR


    def make_order_1st(self, warrent_code, dir):
        self.rec_log("----Make Order")
        ret = self.wait_for_open_warrent()
        if ret != RET_OK:
            return RET_ERR

        ret, bid, ask = self.wait_for_narrow()
        if ret != RET_OK:
            return RET_ERR
        ## Place Order
        if dir == TRADE_SIDE_BUY:
            price = ask
        elif dir == TRADE_SIDE_SELL:
            price = bid
        else:
            return RET_ERR




        qty = TRADE_AMOUNT * 10000
        self.rec_log("----Place Order: " + str(dir) + " " + str(warrent_code) + " " + str(price) + " " + str(qty))

        ret, orderid = self.trade.place_order(price, qty, warrent_code, dir)
        if ret != RET_OK:
            return RET_ERR
        success = False
        ## Check
        ret, status = self.trade.query_order(orderid)
        if ret != RET_OK:
            self.rec_log("Query Order ERR")
            return RET_ERR

        if status != 3:
            self.rec_log("----Not dealt... wait for 3 seconds")
            ## Wait for 3 s
            time.sleep(3)
            ## Check Again
            ret, status = self.trade.query_order(orderid)
            if ret != RET_OK:
                return RET_ERR
            ## Not Dealt
            if status != 3:
                self.rec_log("----Not dealt..." + str(status))

                ## Wait for being dealt or is partly dealt
                if status == 1 or status == 2:
                    ret = self.wait_for_open_warrent()
                    if ret != RET_OK:
                        return RET_ERR

                    ret, bid, ask = self.wait_for_narrow()
                    if ret != RET_OK:
                        return RET_ERR

                    if dir == TRADE_SIDE_BUY:
                        price = ask
                    elif dir == TRADE_SIDE_SELL:
                        price = bid

                    self.rec_log(
                        "----Modify Price " + str(dir) + " " + str(warrent_code) + " " + str(price) + " " + str(qty))
                    ret = self.trade.modify(price, qty, orderid)
                    if ret != RET_OK:
                        return RET_ERR
                    time.sleep(3)
                    ret, status = self.trade.query_order(orderid)
                    if ret != RET_OK:
                        return RET_ERR
                    ## Not Dealt
                    if status != 3:
                        self.rec_log("Not Dealt. Big ERR!!!!")
                        return ERR_NOT_DEALT
                    else:
                        success = True
        ## Dealt
        else:
            success = True

        if success == True:
            return RET_OK
        else:
            return RET_ERR


    def buy_warrent(self):
        self.rec_log("Buy...")
        ret = self.make_order(self.warrent, TRADE_SIDE_BUY)
        if ret != RET_OK:
            return RET_ERR
        return RET_OK

    def wait_for_timer(self):
        self.rec_log("Waiting for Timer")
        success = False
        while True:
            ret, data_time = self.quote.get_hkfuture_time()
            if ret != RET_OK:
                success = False
                break

            if self.compare_time(data_time, TIME_STR_END) == TIME_CMP_BIGGER or \
                self.compare_time(data_time, TIME_STR_END) == TIME_CMP_EQUAL:
                success = True
                break
            else:
                time.sleep(1)
                continue

        if success == True:
            return RET_OK
        else:
            return RET_ERR


    def sell_warrent(self):
        self.rec_log("Sell...")
        ret = self.make_order(self.warrent, TRADE_SIDE_SELL)
        if ret != RET_OK:
            return RET_ERR
        return RET_OK


#----------------------------------------------------
    def compare_time(self, a_time, b_time):
        a_time_list = a_time.split(":")
        a_time_list_second = int(a_time_list[0]) * 3600 + \
                             int(a_time_list[1]) * 60 + \
                             int(a_time_list[2]) * 1
        b_time_list = b_time.split(":")
        b_time_list_second = int(b_time_list[0]) * 3600 + \
                             int(b_time_list[1]) * 60 + \
                             int(b_time_list[2]) * 1

        if a_time_list_second > b_time_list_second:
            return TIME_CMP_BIGGER
        elif a_time_list_second == b_time_list_second:
            return TIME_CMP_EQUAL
        else:
            return TIME_CMP_SMALLER


if __name__ == "__main__":
    b = brocker()
    b.process()
    b.disconnect()

    sub = "[" + b.get_local_date() + "]" + " Magnet Log"
    s = ret_sender(sub, b.msg, EMAIL_PASSWD)
    s.send_email()
