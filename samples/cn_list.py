from futuquant import *
import time
import math
import random
import matplotlib.pyplot as plt


class broker:
    def __init__(self, api_svr_ip, api_svr_port):
        self.api_svr_ip = api_svr_ip
        self.api_svr_port = api_svr_port

    def connect_api(self):
        self.quote_ctx = OpenQuoteContext(host=self.api_svr_ip, port=self.api_svr_port)
        self.tradehk_ctx = OpenHKTradeContext(self.api_svr_ip, self.api_svr_port)
        ret_code, ret_data = self.tradehk_ctx.unlock_trade("584679")

    def get_day_k(self ):
        code = 'HK.800000'
        num = 999
        ktype = "K_15M"
        sum = 0
        ret, ret_date = self.quote_ctx.subscribe(code, ktype)
        if ret != 0:
            print("subscribe fail")
            print(ret_date)
            return -1, 0
        #code time_key open close high low  volume      turnover  pe_ratio  turnover_rate
        ret_code, ret_data = self.quote_ctx.get_cur_kline(code, num, ktype, autype='qfq')
        if ret_code != 0:
            print(ret_data)
            return -1, ret_data

        ret_data["MA4"] = 0.0
        ret_data["MA4_I"] = 0.0
        ret_data["MA4_R_T3"] = 0.0
        for i in range(3, num):
            ret_data.iloc[i, 10] = ( ret_data.iloc[i, 3] + ret_data.iloc[i - 1, 3] + ret_data.iloc[i - 2, 3] + ret_data.iloc[i - 3, 3])/4
            ret_data.iloc[i, 11] = ( ret_data.iloc[i, 2] + ret_data.iloc[i - 1, 3] + ret_data.iloc[i - 2, 3] + ret_data.iloc[i - 3, 3])/4

        for i in range(6, num):
            ret_data.iloc[i, 12] = ( ret_data.iloc[i, 11] - ret_data.iloc[i - 3, 11] )/3


        for i in range(4, num):
            date_time_p = ret_data.iloc[i - 1, 1]
            date_p = date_time_p.split(" ")[0]
            date_time_c = ret_data.iloc[i, 1]
            date_c = date_time_c.split(" ")[0]
            if date_c == date_p:
                pass
            else:
                close_p = ret_data.iloc[i - 1, 3]
                open_c  = ret_data.iloc[i, 2]
                gap = open_c - close_p
                ma4_r = ret_data.iloc[i, 12]
                rst = ret_data.iloc[i, 3] - ret_data.iloc[i, 2]
                if gap < 0:
                    if ma4_r > 0:
                        trade_ret = rst
                    else:
                        trade_ret = 0
                else:
                    if ma4_r > 0:
                        trade_ret = 0
                    else:
                        trade_ret = rst * (-1)



                print("**** " + date_c)
                print("     " + "Gap: " + str(gap))
                print("     " + "Rat: " + str(ma4_r))
                print("     " + "Ret: " + str(rst))
                print("     " + "Trade Result " + str(trade_ret))
                sum += trade_ret
        print("Total: " + str(sum))
        return 0, ret_data

    def test_random_5M_history(self, start, end):
        code = 'HK.800000'
        # #66 5mK per day
        ktype = "K_5M"

        ## BEAR
        type = -1

        sum = 0
        #  code time_key  open  close  high   low  pe_ratio  turnover_rate volume   turnover  change_rate MA4  MA4_I  MA4_R_T3  trade_result
        pos_open = 2
        pos_close = 3
        pos_high = 4
        pos_low = 5
        pos_ma4 = 11
        pos_ma4_i = 12
        pos_ma4_r = 13
        pos_test_result = 14
        ret, ret_data = self.get_history_k(code, start, end, ktype)
        if ret != 0:
            print("get history fail")
            print(ret_data)
            return -1, 0
        num = len(ret_data)
        ret_data["MA4"] = 0.0
        ret_data["MA4_I"] = 0.0
        ret_data["MA4_R_T3"] = 0.0
        ret_data["trade_result"] = 0.0
        for i in range(3, num):
            ret_data.iloc[i, pos_ma4] = ( ret_data.iloc[i, 3] + ret_data.iloc[i - 1, 3] + ret_data.iloc[i - 2, 3] + ret_data.iloc[i - 3, 3])/4
            ret_data.iloc[i, pos_ma4_i] = ( ret_data.iloc[i, 2] + ret_data.iloc[i - 1, 3] + ret_data.iloc[i - 2, 3] + ret_data.iloc[i - 3, 3])/4

        for i in range(6, num):
            ret_data.iloc[i, pos_ma4_r] = ( ret_data.iloc[i, pos_ma4_i] - ret_data.iloc[i - 3, pos_ma4_i] )/3

        sum_up = 0
        sum_down = 0
        for i in range(4, num):
            date_time_p = ret_data.iloc[i - 1, 1]
            date_p = date_time_p.split(" ")[0]
            date_time_c = ret_data.iloc[i, 1]
            date_c = date_time_c.split(" ")[0]


            if date_c == date_p:
                pass
            else:
                cnt = random.randint(2,65)
                buy_bar_num = i + cnt - 1
                buy_price = ret_data.iloc[i, pos_open]
                min = ret_data.iloc[i, pos_low]
                max = ret_data.iloc[i, pos_high]
                for j in range(buy_bar_num + cnt - 1, buy_bar_num + 65):
                    low = ret_data.iloc[j, pos_low]
                    high = ret_data.iloc[j, pos_high]
                    if low < min:
                        min = low
                    if high >  max:
                        max = high
                    print(ret_data.iloc[buy_bar_num, 1])

                float_up = max - buy_price
                float_down = min - buy_price
                sum_up += float_up
                sum_down += float_down
                date = ret_data.iloc[buy_bar_num, 1]
                print("**** " + date_c + " " + str(date))
                print("     " + "UP  : " + str(float_up))
                print("     " + "DOWN: " + str(float_down))




        return 0, ret_data

    def test_magment_15M_history(self, start, end):
        code = 'HK.800000'

        ktype = "K_15M"
        sum = 0
        #    code             time_key       open      close       high   low  pe_ratio  turnover_rate volume      turnover  change_rate MA4      MA4_I  MA4_R_T3  trade_result
        pos_open = 2
        pos_close = 3
        pos_ma4 = 11
        pos_ma4_i = 12
        pos_ma4_r = 13
        pos_test_result = 14
        ret, ret_data = self.get_history_k(code, start, end, ktype)
        if ret != 0:
            print("get history fail")
            print(ret_data)
            return -1, 0
        num = len(ret_data)
        ret_data["MA4"] = 0.0
        ret_data["MA4_I"] = 0.0
        ret_data["MA4_R_T3"] = 0.0
        ret_data["trade_result"] = 0.0
        for i in range(3, num):
            ret_data.iloc[i, pos_ma4] = ( ret_data.iloc[i, 3] + ret_data.iloc[i - 1, 3] + ret_data.iloc[i - 2, 3] + ret_data.iloc[i - 3, 3])/4
            ret_data.iloc[i, pos_ma4_i] = ( ret_data.iloc[i, 2] + ret_data.iloc[i - 1, 3] + ret_data.iloc[i - 2, 3] + ret_data.iloc[i - 3, 3])/4

        for i in range(6, num):
            ret_data.iloc[i, pos_ma4_r] = ( ret_data.iloc[i, pos_ma4_i] - ret_data.iloc[i - 3, pos_ma4_i] )/3


        for i in range(4, num):
            date_time_p = ret_data.iloc[i - 1, 1]
            date_p = date_time_p.split(" ")[0]
            date_time_c = ret_data.iloc[i, 1]
            date_c = date_time_c.split(" ")[0]
            if date_c == date_p:
                pass
            else:
                close_p = ret_data.iloc[i - 1, 3]
                open_c  = ret_data.iloc[i, 2]
                gap = open_c - close_p
                ma4_r = ret_data.iloc[i, pos_ma4_r]
                rst = ret_data.iloc[i, 3] - ret_data.iloc[i, 2]
                ## Gao Kai
                if gap > 0:
                    trade_ret = rst * (-1)
                    pass
                ## Di Kai
                else:
                    trade_ret = rst
                ret_data.iloc[i, pos_test_result] = trade_ret
                print("**** " + date_c)
                print("     " + "Gap: " + str(gap))
                print("     " + "Rat: " + str(ma4_r))
                print("     " + "Ret: " + str(rst))
                print("     " + "Trade Result " + str(trade_ret))
                sum += trade_ret
        print("Total: " + str(sum))

       # for i in range(4, num):
        #    if  ret_data.iloc[i, pos_test_result]!=0:
       #         print( ret_data.iloc[i, pos_test_result])



        return 0, ret_data

    def test_boll(self, start, end):
        #code time_key open close high low  pe_ratio turnover_rate volume  turnover change_rate
        # 0   1        2    3     4    5    6        7             8       9        10

        code = 'HK.800000'
        ktype = "K_15M"

        ret, ret_data = self.get_history_k(code, start, end, ktype)
        if ret != 0:
            print("get history fail")
            print(ret_data)
            return -1, 0
        num = len(ret_data)



        # BOLL Paras
        boll_n = 20
        boll_k = 2


        pos_k_open = 2
        pos_k_close = 3
        pos_k_high = 4
        pos_k_low = 5

        pos_boll_mid = 11
        pos_boll_upper = 12
        pos_boll_lower = 13
        pos_boll_mid_i = 14
        pos_boll_upper_i = 15
        pos_boll_lower_i = 16
        ret_data["BOLL_MID"] = 0.0
        ret_data["BOLL_UPPER"] = 0.0
        ret_data["BOLL_LOWER"] = 0.0
        ret_data["BOLL_MID_I"] = 0.0
        ret_data["BOLL_UPPER_I"] = 0.0
        ret_data["BOLL_LOWER_I"] = 0.0
        for i in range(boll_n - 1, num):
            # 1. MA
            ma = 0
            for j in range(i - boll_n + 1, i):
                ma += ret_data.iloc[j, pos_k_close] / boll_n

            ma_i = ma + ret_data.iloc[i, pos_k_open] / boll_n
            ma   = ma + ret_data.iloc[i, pos_k_close] / boll_n


            # 2. Sigma
            val = 0
            for j in range(i - boll_n + 1, i + 1):
                val += ((ret_data.iloc[j, pos_k_close] - ma)**2)/boll_n
            sigma = math.sqrt(val)

            val = 0
            for j in range(i - boll_n + 1, i):
                val += ((ret_data.iloc[j, pos_k_close] - ma_i)**2)/boll_n
            val += ((ret_data.iloc[i, pos_k_open] - ma_i) ** 2) / boll_n
            sigma_i = math.sqrt(val)

            # 3. Upper & Lower
            upper = ma + boll_k * sigma
            lower = ma - boll_k * sigma

            upper_i = ma_i + boll_k * sigma_i
            lower_i = ma_i - boll_k * sigma_i

            ret_data.iloc[i, pos_boll_mid] = ma
            ret_data.iloc[i, pos_boll_upper] = upper
            ret_data.iloc[i, pos_boll_lower] = lower

            ret_data.iloc[i, pos_boll_mid_i] = ma_i
            ret_data.iloc[i, pos_boll_upper_i] = upper_i
            ret_data.iloc[i, pos_boll_lower_i] = lower_i


        ## Strategy and Test
        ## Let's see a new day opens on which part
        date = []
        boll_upper = []
        boll_lower = []
        high = []
        low = []
        start = []
        end = []
        for i in range(boll_n - 1, num):
            date_time_p = ret_data.iloc[i - 1, 1]
            date_p = date_time_p.split(" ")[0]
            date_time_c = ret_data.iloc[i, 1]
            date_c = date_time_c.split(" ")[0]
            if date_c == date_p:
                pass
            else:
                if ret_data.iloc[i, pos_k_open] > ret_data.iloc[i - 1, pos_k_close] and \
                        ret_data.iloc[i, pos_k_low] <= (ret_data.iloc[i, pos_boll_lower_i] - 10 ) and \
                        ret_data.iloc[i, pos_k_open] > ret_data.iloc[i, pos_boll_lower_i]:

                    date.append(date_c)
                    boll_upper.append(ret_data.iloc[i, pos_boll_upper_i])
                    boll_lower.append(ret_data.iloc[i, pos_boll_lower_i])
                    high.append(ret_data.iloc[i, pos_k_high])
                    low.append(ret_data.iloc[i, pos_k_low])
                    start.append(ret_data.iloc[i, pos_k_open])
                    end.append(ret_data.iloc[i, pos_k_close])
                    print(date_c + " :" + str(ret_data.iloc[i, pos_k_close] - ret_data.iloc[i, pos_boll_lower_i]))

        plt.plot(boll_upper, 'r--')
        plt.plot(boll_lower, 'r--')
        #plt.plot(high, 'g^')
        plt.plot(low, 'gv')
        #plt.plot(start, '.')
        plt.plot(end, '.')
        plt.show()

        return 0, ret_data


    def get_cn_list(self):
        cn_list = []
        market = "SH"
        market = "HK"
        plate_class = "ALL"

        ret_code, ret_data = self.quote_ctx.get_plate_list( market, plate_class)
        if ret_code != 0:
            return -1, cn_list
        print("Get Plate Done.")
        print(ret_data)

        plate_list = ret_data['code']
        for plate_code in plate_list:
            ret_code, ret_data = self.quote_ctx.get_plate_stock(plate_code)
            if ret_code != 0:
                print("ERR " + str(plate_code))
            for code in ret_data["code"]:
                cn_list.append(code)
            print(str(plate_code) + " Done.")
            time.sleep(1)

        return 0, cn_list

    def get_history_k(self, code, start, end, ktype='K_DAY'):
        ret_code, ret_data = self.quote_ctx.get_history_kline(code, start, end, ktype, autype='qfq'
                                                     )
        if ret_code != 0:
            return -1, []
        return 0, ret_data

    def find_warrent(self):
        ret_code, ret_data = self.quote_ctx.get_stock_basicinfo("HK", stock_type='WARRANT')
        if ret_code != 0:
            return -1, cn_list
        print("Get WARRENT Done.")
        print(ret_data)

    def get_acc_info(self):
        ret_code, ret_data = self.tradehk_ctx.accinfo_query(0)
        if ret_code != 0:
            print("Fail")
        print(ret_data)
        try:
            print(ret_data["ZQSZ"][0])
            print(ret_data["KQXJ"][0])
            print(ret_data["ZSJE"][0])
            print(ret_data["YYJDE"][0])
            print(ret_data["Power"][0])
        except:
            print("???")
        if ret_data["ZCJZ"][0] > 10000:
            print("OK")



        ret_code, ret_data = self.tradehk_ctx.position_list_query(strcode='', stocktype='', pl_ratio_min='', pl_ratio_max='',
                                                             envtype=0)
        if ret_code != 0:
            print("Fail")
        print(ret_data)




def fitting_shape_cup(df_k_line):
    k_line = df_k_line
    cnt = len(k_line)
    #prices_close = k_line['close']
    prices_high = []
    for price in df_k_line["high"]:
        prices_high.append(price)

    random_point_c = cnt - 1  # 随机选取random_point_c代表今天

    # Find B
    para_gama = 1             # gama为B点相对于C点高度的系数
    para_span_request_bc = 3  # B点与C点之间的周数至少为span_request_bc
    ret, point_b = shape_cup_find_b(prices_high, random_point_c, para_gama, para_span_request_bc)
    if ret != -1:
        print("B found")
        # Find A
        omega = 1.05  # omega为A点相对于B点高度的系数
        span = 7  # span为时间跨度的周数
        ret, point_a = shape_cup_find_a(prices_high, point_b, omega, span)
        if ret != -1:
            print("A found")
            print(df_k_line.iloc[point_a,])
            print(df_k_line.iloc[point_b,])
        else:
            print("A not found")
    else:
        print("B not found")

    return

def shape_cup_find_b(prices_high, random_point_c, gama, span_request_bc):
    ret = -1
    val = -1
    cnt = len(prices_high)
    for i in range(cnt - random_point_c + span_request_bc + 1, cnt):
        if prices_high[-i] > gama * prices_high[random_point_c]:
            if prices_high[-i - 1] > prices_high[-i]:
                continue
            else:
                point_b = cnt - i + 1
                if point_b > random_point_c:
                    ret = -1
                    break
                else:
                    print(point_b)
                    val = point_b
                    ret = 0
                    break
    return ret, val

def shape_cup_find_a(prices_high, point_b, omega, span):
    ret = -1
    val = -1
    cnt = len(prices_high)
    for i in range(cnt - point_b + span + 1, cnt):
        if prices_high[-i] > omega * prices_high[point_b]:
            if prices_high[-i - 1] > prices_high[-i]:
                continue
            else:
                point_a = cnt - i + 1
                if point_a > point_b:
                    ret = -1
                    break
                else:
                    one_third = int(point_a + (point_b - point_a) / 3)
                    two_third = int(point_a + (point_b - point_a) * 2 / 3)
                    List = [prices_high[k] > max(prices_high[one_third], prices_high[two_third]) for k in
                            range(one_third + 1, two_third)]
                    if True in List:
                        continue
                    else:
                        print(point_a)
                        ret = 0
                        val = point_a
                        break
    return ret, val




if __name__ == "__main__":
    API_RM_SVR_IP = '119.29.141.202'
    API_LO_SVR_IP = '127.0.0.1'
    API_SVR_PORT = 11111
    b = broker(API_LO_SVR_IP, API_SVR_PORT)
    b.connect_api()
    #b.test_boll()
    start = '2017-12-20'
    end = '2018-06-30'
    #ret, k = b.test_boll(start, end)
    ret, k = b.get_history_k("HK.800000", start, end, "K_5M")
    if ret == -1:
        print("fail")
    cycle = 9
    test_day = '2018-07-09'
    test_day2 = '2018-07-20'
    ret, test_set = b.get_history_k("HK.800000", test_day2, test_day2, "K_5M")
    if ret == -1:
        print("fail")
    #print(test_set)
    test_ret = [[],[]]
    cnt = 0
    for i in range(1, len(k)):
        date_time_p = k.iloc[i - 1, 1]
        date_p = date_time_p.split(" ")[0]
        date_time_c = k.iloc[i, 1]
        date_c = date_time_c.split(" ")[0]
        if date_c == date_p:
            pass
        else:
            cnt +=1
            # Get highest and lowest of src
            src_h = k.iloc[i, 3]
            src_l = k.iloc[i, 3]
            for j in range(0, cycle):
                if k.iloc[i + j, 3] > src_h:
                    src_h = k.iloc[i + j, 3]
                if k.iloc[i + j, 3] < src_l:
                    src_l = k.iloc[i + j, 3]

            # Get highest and lowest of test
            tet_h = test_set.iloc[0, 3]
            tet_l = test_set.iloc[0, 3]
            for j in range(0, cycle):
                if k.iloc[ j, 3] > tet_h:
                    tet_h = test_set.iloc[0 + j, 3]
                if k.iloc[ j, 3] < tet_l:
                    tet_l = test_set.iloc[0 + j, 3]

            # Calculate derivative
            delta = (src_h - src_l) - (tet_h - tet_l)
            single_ret_list = []
            for t in range(0, abs(int(delta)) + 1):
                der = 0
                for j in range(0, cycle):
                    if delta > 0:
                        unit1 = (k.iloc[i + j, 2] - src_l) - (test_set.iloc[0 + j, 2] - tet_l + t)
                        unit2 = (k.iloc[i + j, 3] - src_l) - (test_set.iloc[0 + j, 3] - tet_l + t)
                        unit3 = (k.iloc[i + j, 4] - src_l) - (test_set.iloc[0 + j, 4] - tet_l + t)
                        unit4 = (k.iloc[i + j, 5] - src_l) - (test_set.iloc[0 + j, 5] - tet_l + t)
                    else:
                        unit1 = (k.iloc[i + j, 2] - src_l + t) - (test_set.iloc[0 + j, 2] - tet_l)
                        unit2 = (k.iloc[i + j, 3] - src_l + t) - (test_set.iloc[0 + j, 3] - tet_l)
                        unit3 = (k.iloc[i + j, 4] - src_l + t) - (test_set.iloc[0 + j, 4] - tet_l)
                        unit4 = (k.iloc[i + j, 5] - src_l + t) - (test_set.iloc[0 + j, 5] - tet_l)
                    der += (unit1 * unit1 + unit2 * unit2 + unit3 * unit3 + unit4 * unit4)
                single_ret_list.append(der)
            # find smallest der

            min_val = single_ret_list[0]
            for val in single_ret_list:
                if val < min_val:
                    min_val = val

            # Done
            test_ret[0].append(date_c)
            test_ret[1].append(min_val)


    # Print result
    min_day = test_ret[1][0]
    min_pos = 0
    for i in range(0, cnt):
        if test_ret[1][i] < min_day:
            min_day = test_ret[1][i]
            min_pos = i
    print(test_ret[0][min_pos])
    print(test_ret[1][min_pos])
    for i in range(1, len(k)):
        date_time_p = k.iloc[i - 1, 1]
        date_p = date_time_p.split(" ")[0]
        date_time_c = k.iloc[i, 1]
        date_c = date_time_c.split(" ")[0]
        if date_c == date_p:
            pass
        else:
            if date_c == test_ret[0][min_pos]:
                for n in range(0, 5):
                    d1 = k.iloc[i + cycle - 1 + n, 2] - k.iloc[i + cycle - 1 + n, 2]
                    d2 = k.iloc[i + cycle - 1 + n, 3] - k.iloc[i + cycle - 1 + n, 2]
                    d3 = k.iloc[i + cycle - 1 + n, 4] - k.iloc[i + cycle - 1 + n, 2]
                    d4 = k.iloc[i + cycle - 1 + n, 5] - k.iloc[i + cycle - 1 + n, 2]
                    print(str(d1) + " " + str(d2) +" "+ str(d3) + " "+str(d4))
    print("   ")
    print(test_day2)
    for n in range(0, 5):
        d1 = test_set.iloc[cycle - 1 + n, 2] - test_set.iloc[cycle - 1 + n, 2]
        d2 = test_set.iloc[cycle - 1 + n, 3] - test_set.iloc[cycle - 1 + n, 2]
        d3 = test_set.iloc[cycle - 1 + n, 4] - test_set.iloc[cycle - 1 + n, 2]
        d4 = test_set.iloc[cycle - 1 + n, 5] - test_set.iloc[cycle - 1 + n, 2]
        print(str(d1) + " " + str(d2) + " " + str(d3) + " " + str(d4))




    exit(0)
    b.get_acc_info()


    ret, cn_list = b.find_warrent()
    if ret != -1:
        print(cn_list)


    start = '2005-01-04'
    end = '2016-04-29'
    code = 'SZ.000639'
    ret, k = b.get_history_k(code, start, end)
    if ret != -1:
        print("ok")
    k.to_csv("C:\\15M_history.csv", index=False)
    print("Saved")
    #print(k)

    #fitting_shape_cup(k)

