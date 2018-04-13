from futuquant import *
import time
class broker:
    def __init__(self, api_svr_ip, api_svr_port):
        self.api_svr_ip = api_svr_ip
        self.api_svr_port = api_svr_port

    def connect_api(self):
        try:
           self.quote_ctx = OpenQuoteContext(host=self.api_svr_ip, port=self.api_svr_port)
        except:
            print("No")
        ret_code, ret_data = self.quote_ctx.get_trading_days('HK', start_date=None, end_date=None)
        print(ret_data)


    def get_cn_list(self):
        cn_list = []
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
        print(ret_data)
        if ret_code != 0:
            return -1, []
        return 0, ret_data


    def sub(self, stock_code, data_type):
        ret_code, ret_data = self.quote_ctx.subscribe(stock_code, data_type, push=False)
        if ret_code != 0:
            return -1, []
        return 0, ret_data

    def get_cur_k(self, code, num, ktype='K_DAY'):
        ret_code, ret_data = self.quote_ctx.get_cur_kline(code, num, ktype, autype='qfq')
        if ret_code != 0:
            return -1, []
        return 0, ret_data




#code             time_key      open     close      high       low
#HK.800000  2018-03-12 12:00:00  31487.62  31469.17  31494.44  31453.04
if __name__ == "__main__":
    API_RM_SVR_IP = '119.29.141.202'
    API_LO_SVR_IP = '127.0.0.1'
    API_SVR_PORT = 11111
    b = broker(API_LO_SVR_IP, API_SVR_PORT)
    b.connect_api()
    print("connected")

    stock_code = 'HK.800000'
    ktype = 'K_15M'
    ret, ret_data = b.sub(stock_code, ktype)
    if ret != -1:
        print(ret_data)
    print("subscribed")

    ret, ret_data = b.get_cur_k(stock_code, 100, ktype)
    if ret != -1:
        print(ret_data)

    stock_code2 = 'HK.00700'
    ret, ret_data = b.sub(stock_code2, ktype)
    if ret != -1:
        print(ret_data)
    print("subscribed")


    ret, ret_data = b.get_cur_k(stock_code2, 100, ktype)
    if ret != -1:
        print(ret_data)
    print("waited for 15mins")
    #ret, ret_data = b.get_history_k(stock_code, '2018-01-01','2018-02-01', ktype)

    print(ret_data)
    time.sleep(60*15)

    exit(0)
    ret = []


    start_day = 3
    time_ = ret_data.iloc[start_day, 1]
    pre_close = ret_data.iloc[start_day, 3]
    pre_ma4 = (ret_data.iloc[start_day - 3, 3] + ret_data.iloc[start_day - 2, 3] + ret_data.iloc[start_day - 1, 3] + ret_data.iloc[start_day, 3]) / 4
    date = time_.split(' ')[0]
    pre_date = date
    day_cnt = 0


    for cnt in range(4, len(ret_data)):
        cur_ma4 = (ret_data.iloc[cnt-3, 3] + ret_data.iloc[cnt-2, 3] + ret_data.iloc[cnt-1, 3] + ret_data.iloc[cnt, 3])/4
        time_ = ret_data.iloc[cnt, 1]
        cur_open = ret_data.iloc[cnt, 2]
        cur_close = ret_data.iloc[cnt, 3]
        date = time_.split(' ')[0]
        cur_date = date
        if cur_date!=pre_date:
            day_cnt +=1
            perct = 0
            if cur_open > pre_close * (1 + perct):

                a =1
                ret.append([cur_date, -1, cur_ma4 - pre_ma4, (cur_close - cur_open) *(-1)])
            elif cur_open < pre_close * (1 - perct):

                a = 1
                ret.append([cur_date,  1, cur_ma4 - pre_ma4, (cur_close - cur_open) * (1)])

        pre_close = cur_close
        pre_date = cur_date
        pre_ma4 = cur_ma4

    sum = 0
    sum_point = 0
    for line in ret:
        print(line)
        point = int(line[3]/10) - 1
        sum += line[3]
        sum_point += point
        #print(point)

    print(sum)
    print(sum_point)
    print(day_cnt)

    for line in ret:
        print(int(line[3]/10) - 1)


