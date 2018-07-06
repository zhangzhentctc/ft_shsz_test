from futuquant import *
import time
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
    b.get_day_k()
    #start = '2005-01-04'
    #end = '2016-04-29'
    #ret, k = b.get_history_k("HK.800000", start, end)
    #if ret != -1:
    #    print("ok")
    #print(k)
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
    print(k)

    #fitting_shape_cup(k)

