from hk_magnet.localtime_api import *
from hk_magnet.quote_api import *
from hk_magnet.trade_api import *
from hk_magnet.ret_sender import *
import time

#### Customers

CODE_HK_BULL     = 'HK.69194'
CODE_HK_BULL_BK1 = 'HK.60139'
CODE_HK_BULL_BK2 = 'HK.69055'

CODE_HK_BEAR     = 'HK.64011'
CODE_HK_BEAR_BK1 = 'HK.63073'
CODE_HK_BEAR_BK2 = 'HK.59022'

TRADE_AMOUNT = 10

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
    TIME_START_WORK    = '15:25:00'
    TIME_CONN_DEADLINE = '15:29:00'
    TIME_PREP_DEADLINE = '15:31:00'
    TIME_MKT_OPEN = '15:30:00'
    TIME_STR_END = '15:45:00'

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
DATA_TYPE_1MIN = "K_1M"
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

FILE_UNLOCK_PASSWD = './unlock.txt'
FILE_BULL_CODES = './bull.txt'
FILE_BEAR_CODES = './bear.txt'

class brocker:
    def __init__(self):
        self.quote = quote_api(HOST, PORT)
        self.trade = trade_api(HOST, PORT, TRADE_TYPE_REAL)
        self.msg = ""
        try:
            file = open(FILE_UNLOCK_PASSWD, 'r')
            all_line_txt = file.readlines()
            self.unlock_passwd = all_line_txt[0].strip('\n')
        except:
            self.unlock_passwd = '123456'

        try:
            file = open(FILE_BULL_CODES, 'r')
            all_line_txt = file.readlines()
            self.bull_codes = [all_line_txt[0].strip('\n'), all_line_txt[1].strip('\n'), all_line_txt[2].strip('\n')]
        except:
            self.bull_codes = [CODE_HK_BULL, CODE_HK_BULL_BK1, CODE_HK_BULL_BK2]

        try:
            file = open(FILE_BEAR_CODES, 'r')
            all_line_txt = file.readlines()
            self.bear_codes = [all_line_txt[0].strip('\n'), all_line_txt[1].strip('\n'), all_line_txt[2].strip('\n')]
        except:
            self.bear_codes = [CODE_HK_BEAR, CODE_HK_BEAR_BK1, CODE_HK_BEAR_BK2]


        self.watch_warrants = []


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

    def store_data(self):
        self.rec_log("Store Data...")
        ret, data_k1min = self.quote.get_day_k(CODE_HK_FUTURE, 31,DATA_TYPE_QUO)
        if ret != RET_OK:
            return RET_ERR
        ## Store into File
        l = localtime_api()
        today_date = l.get_local_date()
        data_k1min.to_csv("C:\\1mk_" + today_date + ".csv", index=False)
        return RET_OK


    def process(self):
        #ret = RET_OK
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

        ret = self.store_data()
        if ret != RET_OK:
            self.rec_log("Store Data ERR")
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

        ret = self.quote.subscribe(CODE_HK_FUTURE, DATA_TYPE_1MIN)
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

    def filter_warrent(self, hsi_animal_list, recycle_min, recycle_max, street_ratio, hsi_open):
        para_code_list = []
        para_code_list_cnt = 0
        para_code_cnt = 0
        hsi_animal_ret = []
        bear_cnt = 0
        bull_cnt = 0
        for code in hsi_animal_list:
            para_code_list.append(code[0])
            para_code_list_cnt += 1
            para_code_cnt += 1

            if para_code_list_cnt >= 199 or para_code_cnt == len(hsi_animal_list):
                ret_code, hsi_animals_shot = self.quote.get_market_snapshot(para_code_list)
                if ret_code != 0:
                    return -1, -1, hsi_animals_shot
                # Filter
                for j in range(0, len(hsi_animals_shot)):
                    warrant_deep = abs(hsi_animals_shot["wrt_recovery_price"][j] - hsi_open)
                    if hsi_animals_shot["suspension"][j] == False and \
                                    hsi_animals_shot["wrt_street_ratio"][j] < street_ratio and \
                                    warrant_deep > recycle_min and \
                                    warrant_deep < recycle_max:
                        if hsi_animals_shot["wrt_type"][j] == "BEAR":
                            bear_cnt += 1
                        if hsi_animals_shot["wrt_type"][j] == "BULL":
                            bull_cnt += 1
                        hsi_animal_ret.append([hsi_animals_shot["code"][j], hsi_animals_shot["wrt_recovery_price"][j],
                                               hsi_animals_shot["wrt_type"][j], warrant_deep])

                time.sleep(6)
                para_code_list = []
                para_code_list_cnt = 0

        return bull_cnt, bear_cnt, hsi_animal_ret

    def find_warrent(self, recycle_min, recycle_max, steet_ratio, hsi_open):
        #ret_code, hsi_shot = self.quote.get_market_snapshot(["HK.800000"])
        #if ret_code != 0:
        #    return -1, hsi_shot
        #hsi_open = hsi_shot["open_price"][0]
        #time.sleep(5)

        warrant_holder_list = ["摩通"]
        hsi_animal_list = []
        ret_code, all_warrant = self.quote.get_stock_basicinfo("HK", stock_type='WARRANT')
        if ret_code != 0:
            return -1, [], []

        hsi_animal_cnt = 0
        for i in range(0, len(all_warrant)):
            if all_warrant["owner_stock_code"][i] == "HK.800000" and all_warrant["lot_size"][i] == 10000 and \
                    (all_warrant["stock_child_type"][i] == "BULL" or all_warrant["stock_child_type"][i] == "BEAR"):
                for holder_num in range(0, len(warrant_holder_list)):
                    if warrant_holder_list[holder_num] in all_warrant["name"][i]:
                        hsi_animal_list.append([all_warrant["code"][i], holder_num, all_warrant["stock_child_type"][i]])
                        hsi_animal_cnt += 1


        bull_cnt, bear_cnt, hsi_animal_ret = self.filter_warrent(hsi_animal_list, recycle_min, recycle_max, steet_ratio,
                                                                 hsi_open)

        if bull_cnt < 2 or bear_cnt < 2:
            bull_cnt, bear_cnt, hsi_animal_ret = self.filter_warrent(hsi_animal_list, recycle_min, recycle_max + 500,
                                                                     steet_ratio, hsi_open)
            if bull_cnt < 0 or bear_cnt < 0:
                return -1, [], []


        hsi_bull_ret = []
        hsi_bear_ret = []
        for i in range(0, len(hsi_animal_ret)):
            if hsi_animal_ret[i][2] == "BULL":
                hsi_bull_ret.append(hsi_animal_ret[i])
            elif hsi_animal_ret[i][2] == "BEAR":
                hsi_bear_ret.append(hsi_animal_ret[i])
            else:
                continue

        ### Sort
        factor_pos = 3
        hsi_bull_ret_order = []
        hsi_bear_ret_order = []
        while len(hsi_bull_ret) > 0:
            min_pos = 0
            for i in range(0, len(hsi_bull_ret)):
                if hsi_bull_ret[i][factor_pos] < hsi_bull_ret[min_pos][factor_pos]:
                    min_pos = i
            hsi_bull_ret_order.append(hsi_bull_ret[min_pos][0])
            # if len(hsi_bull_ret) >= 2:
            # hsi_bull_ret = hsi_bull_ret[:min_pos] + hsi_bull_ret[min_pos + 1:]
            del (hsi_bull_ret[min_pos])

        while len(hsi_bear_ret) > 0:
            min_pos = 0
            for i in range(0, len(hsi_bear_ret)):
                if hsi_bear_ret[i][factor_pos] < hsi_bear_ret[min_pos][factor_pos]:
                    min_pos = i
            hsi_bear_ret_order.append(hsi_bear_ret[min_pos][0])
            # if len(hsi_bear_ret) >= 2:
            # hsi_bear_ret = hsi_bear_ret[:min_pos] + hsi_bear_ret[min_pos + 1:]
            del (hsi_bear_ret[min_pos])

        return 0, hsi_bull_ret_order, hsi_bear_ret_order


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
            #### Search for Warrant Test, Not Enabled
            try:
                ret, hsi_bull_ret_order, hsi_bear_ret_order = self.find_warrent(300, 700, 50, new_open)
            except:
                print("Find Warran Fail")

            if new_open > last_close:
                try:
                    if ret == RET_OK:
                        cnt = 0
                        for i in range(0, len(hsi_bear_ret_order)):
                            self.watch_warrants.append(hsi_bear_ret_order[i])
                            self.rec_log("Finding Warrant Bear " + hsi_bear_ret_order[i])
                            cnt += 1
                            if cnt >= 3:
                                break
                except:
                    print("Find Warrant Fail")
                    for code in self.bear_codes:
                        self.watch_warrants.append(code)


                dir = DIR_BEAR
                #self.warrent = self.bear_codes[0]
                #self.warrent_bk1 = self.bear_codes[1]
                #self.warrent_bk2 = self.bear_codes[2]
            else:
                try:
                    if ret == RET_OK:
                        cnt = 0
                        for i in range(0, len(hsi_bull_ret_order)):
                            self.watch_warrants.append(hsi_bull_ret_order[i])
                            self.rec_log("Finding Warrant Bull" + hsi_bull_ret_order[i])
                            cnt += 1
                            if cnt >= 3:
                                break
                except:
                    print("Find Warran Fail")
                    for code in self.bull_codes:
                        self.watch_warrants.append(code)

                dir = DIR_BULL
                #self.warrent = self.bull_codes[0]
                #self.warrent_bk1 = self.bull_codes[1]
                #self.warrent_bk2 = self.bull_codes[2]

            #self.watch_warrants.append(self.warrent)
            #self.watch_warrants.append(self.warrent_bk1)
            #self.watch_warrants.append(self.warrent_bk2)

            return RET_OK
        else:
            return RET_ERR


    def check_warrent(self):
        self.rec_log("Checking Warrent")
        for warrent in self.watch_warrants:
            ret = self.quote.subscribe(warrent, DATA_TYPE_QUO)
            if ret != RET_OK:
                return RET_ERR
            ret = self.quote.subscribe(warrent, DATA_TYPE_BROKER)
            if ret != RET_OK:
                return RET_ERR
            ret = self.quote.subscribe(warrent, DATA_TYPE_BOOK)
            if ret != RET_OK:
                return RET_ERR


        ## WARRENT CHECK SKIP

        return RET_OK


    def start_trade(self):
        pass


## Trade_Level
    ## Faba 96
    ## Mogen 97
    ## Ruixin 97
    def wait_for_open_warrent(self, warrent_code):
        self.rec_log("----Wait for Warrent Open")
        waited_time = 0
        success = False
        intervel = 0.3
        timeout = 3 * 60
        ticks = int(timeout/intervel)
        while waited_time < ticks:
            s_time = time.time()
            ret, bid_data, ask_data = self.quote.get_brokers(warrent_code)
            if ret != RET_OK:
                print("API ERR")
                success = False
                break
            bid_ok = False
            ask_ok = False
            for i in range (0, len(bid_data.index)):
                bid_broker_pos = bid_data["bid_broker_pos"][i]
                bid_broker_id = bid_data["bid_broker_id"][i]
                if bid_broker_pos != '0':
                    bid_ok = False
                    break

                if bid_broker_pos == '0' and \
                    bid_broker_id[0]== '9' and (bid_broker_id[1] == '7' or bid_broker_id[1] == '6'):
                    bid_ok = True
                    break

            for i in range (0, len(ask_data.index)):
                ask_broker_pos = ask_data["ask_broker_pos"][i]
                ask_broker_id = ask_data["ask_broker_id"][i]
                if ask_broker_pos != '0':
                    ask_ok = False
                    break

                if ask_broker_pos == '0' and \
                    ask_broker_id[0]== '9' and (ask_broker_id[1] == '7' or ask_broker_id[1] == '6'):
                    ask_ok = True
                    break
            e_time = time.time()
            if bid_ok == True and ask_ok == True:
                success = True
                break
            else:
                ### Sometimes, it times out when it is 09:56:00
                time.sleep(intervel)
                tick_cost = int((e_time - s_time)/intervel)
                waited_time = waited_time + tick_cost + 1

                ## DEBUG
                if waited_time >= ticks:
                    self.rec_log("----Wait for Warrent Open Timeout")
                    print(bid_data)
                    print(ask_data)

                continue

        if success == True:
            return RET_OK
        else:
            return RET_ERR

    def wait_for_narrow(self, warrent_code):
        self.rec_log("----Wait for narrow")
        success = False
        while True:
            ret, bid, ask = self.quote.get_book(warrent_code)
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
        if dir == TRADE_SIDE_BUY:
            trail_max = 3
            fail_wait_t = 1
        elif dir == TRADE_SIDE_SELL:
            trail_max = 100
            fail_wait_t = 2
        else:
            return RET_ERR

        trail = 0
        success = False
        flag_modify_fail = False
        dealt = 0
        qty = TRADE_AMOUNT * 10000
        while trail < trail_max:
            self.rec_log("----Make Order")
            ## Place Order
            ret = self.wait_for_open_warrent(warrent_code)
            if ret != RET_OK:
                return RET_ERR

            ret, bid, ask = self.wait_for_narrow(warrent_code)
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
                trail += 1
                time.sleep(fail_wait_t)
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
                        ret = self.wait_for_open_warrent(warrent_code)
                        if ret != RET_OK:
                            return RET_ERR

                        ret, bid, ask = self.wait_for_narrow(warrent_code)
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


    def buy_warrent(self):
        self.rec_log("Buy...")
        success = False
        for warrent in self.watch_warrants:
            self.trade_warrent = warrent
            ret = self.make_order(warrent, TRADE_SIDE_BUY)
            if ret != RET_OK:
                continue
            else:
                success = True
                break
        if success == True:
            return RET_OK
        else:
            return RET_ERR

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
        ret = self.make_order(self.trade_warrent, TRADE_SIDE_SELL)
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
    s = ret_sender(sub, b.msg)
    s.send_email()
