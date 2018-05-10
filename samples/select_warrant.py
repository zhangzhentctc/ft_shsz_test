from futuquant import *
import time
class broker:
    def __init__(self, api_svr_ip, api_svr_port):
        self.api_svr_ip = api_svr_ip
        self.api_svr_port = api_svr_port

    def connect_api(self):
        self.quote_ctx = OpenQuoteContext(host=self.api_svr_ip, port=self.api_svr_port)


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
        warrant_holder_list = ["摩通"]
        code_list = []
        ret_code, ret_data = self.quote_ctx.get_stock_basicinfo("HK", stock_type='WARRANT')
        if ret_code != 0:
            return -1, ret_data
        print("Get WARRENT Done.")
        cnt = 0
        for i in range(0, len(ret_data)):
            if ret_data["owner_stock_code"][i] == "HK.80000" and ret_data["lot_size"][i] == 10000 and \
                    (ret_data["stock_child_type"][i] == "BULL" or ret_data["stock_child_type"][i] == "BEAR"):
                for holder in warrant_holder_list:
                    if holder in ret_data["name"][i]:
                        code_list.append([ret_data["code"][i],ret_data["name"][i],ret_data["stock_child_type"][i]])
                        cnt += 1

        para_code_list = []
        para_code_list_cnt = 0
        hsi_open = 23809
        para_code_cnt = 0
        for code in code_list:
            para_code_list.append(code[0])
            para_code_list_cnt += 1
            para_code_cnt += 1

            if para_code_list_cnt >= 199 or para_code_cnt == len(code_list):
                ret_code, ret_data_ = self.quote_ctx.get_market_snapshot(para_code_list)
                if ret_code != 0:
                    return -1, ret_data_


                for j in range(0, len(ret_data_)):
                    if ret_data_["suspension"][j] == False and \
                            ret_data_["wrt_street_ratio"][i] < 50 and \
                            abs(ret_data_["wrt_recovery_price"][i] - hsi_open) > 500 and \
                            abs(ret_data_["wrt_recovery_price"][i] - hsi_open) < 1000:
                        print(str(ret_data_["code"][i]) + " " + str(ret_data_["prev_close_price"][i]))

                time.sleep(6)
                para_code_list = []
                para_code_list_cnt = 0









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
    b = broker(API_RM_SVR_IP, API_SVR_PORT)
    b.connect_api()
    ret, cn_list = b.find_warrent()
    if ret != -1:
        print(cn_list)
    exit(0)


