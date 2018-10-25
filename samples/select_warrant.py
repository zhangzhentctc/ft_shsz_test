from futuquant import *
import time

DIR_BEAR = -1
DIR_BULL = 1

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

    def filter_warrent(self, hsi_animal_list, recycle_min, recycle_max, steet_ratio, hsi_open):
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
                print("Process group")
                ret_code, hsi_animals_shot = self.quote_ctx.get_market_snapshot(para_code_list)
                if ret_code != 0:
                    return -1, -1, hsi_animals_shot

                # Filter
                for j in range(0, len(hsi_animals_shot)):
                    warrant_deep = abs(hsi_animals_shot["wrt_recovery_price"][j] - hsi_open)
                    if hsi_animals_shot["suspension"][j] == False and \
                                    hsi_animals_shot["wrt_street_ratio"][j] < steet_ratio and \
                                    warrant_deep > recycle_min and \
                                    warrant_deep < recycle_max:
                        if hsi_animals_shot["wrt_type"][j] == "BEAR":
                            bear_cnt += 1
                        if hsi_animals_shot["wrt_type"][j] == "BULL":
                            bull_cnt += 1
                        hsi_animal_ret.append([hsi_animals_shot["code"][j], hsi_animals_shot["wrt_recovery_price"][j],
                                               hsi_animals_shot["wrt_type"][j], abs(warrant_deep - 700)])

                time.sleep(6)
                para_code_list = []
                para_code_list_cnt = 0

        return bull_cnt, bear_cnt, hsi_animal_ret

    def cal_street(self, hsi_animal_list):
        para_code_list = []
        para_code_list_cnt = 0
        para_code_cnt = 0
        hsi_animal_ret = []
        bear_cnt = 0
        bull_cnt = 0
        result = []
        for code in hsi_animal_list:
            para_code_list.append(code[0])
            para_code_list_cnt += 1
            para_code_cnt += 1

            if para_code_list_cnt >= 199 or para_code_cnt == len(hsi_animal_list):
                print("Process group")
                ret_code, hsi_animals_shot = self.quote_ctx.get_market_snapshot(para_code_list)
                if ret_code != 0:
                    return -1, -1, hsi_animals_shot

                # Filter
                for j in range(0, len(hsi_animals_shot)):
                    if hsi_animals_shot["suspension"][j] == False:
                        recov_price = hsi_animals_shot["wrt_recovery_price"][j]
                        street_vol = hsi_animals_shot["wrt_street_vol"][j]
                        found = False
                        for i in range(0, len(result)):
                            if result[i][0] == recov_price:
                                result[i][1] += street_vol
                                found = True
                        if found == False:
                            result.append([recov_price, street_vol, hsi_animals_shot["wrt_type"][j]])

        return bull_cnt, bear_cnt, result

    def test_name(self, name):
        ret = False
        if len(name) != 10:
            ret = False
        else:
            for i in range(0, len(name)):
                # 恒指
                if name[0] == "恒" and name[1] == "指":
                    # 牛/熊
                    if name[6] == "牛" or name[6] == "熊":
                        if name[8] == ".":
                            if name[7].isalpha() and name[9].isalpha():
                                ret = True
        if ret == False:
            print("Bad name: " + name)
        return ret

    def find_warrent(self, recycle_min, recycle_max, steet_ratio, hsi_open = 0):
        ret_code, hsi_shot = self.quote_ctx.get_market_snapshot(["HK.800000"])
        if ret_code != 0:
            return -1, hsi_shot
        hsi_open = hsi_shot["open_price"][0]
        time.sleep(5)

        warrant_holder_list = ["摩通"]
        hsi_animal_list = []
        ret_code, all_warrant = self.quote_ctx.get_stock_basicinfo("HK", stock_type='WARRANT')
        if ret_code != 0:
            return -1, all_warrant, all_warrant

        hsi_animal_cnt = 0
        for i in range(0, len(all_warrant)):
            if all_warrant["owner_stock_code"][i] == "HK.800000" and all_warrant["lot_size"][i] == 10000 and \
                (all_warrant["stock_child_type"][i] == "BULL" or all_warrant["stock_child_type"][i] == "BEAR"):
                if self.test_name(all_warrant["name"][i]) == False:
                    continue
                for holder_num in range(0, len(warrant_holder_list)):
                    if warrant_holder_list[holder_num] in all_warrant["name"][i]:

                        hsi_animal_list.append([all_warrant["code"][i], holder_num, all_warrant["stock_child_type"][i]])
                        hsi_animal_cnt += 1

        bull_cnt, bear_cnt, hsi_animal_ret = self.filter_warrent(hsi_animal_list, recycle_min, recycle_max, steet_ratio, hsi_open)

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

        #for animal in hsi_animal_ret:
        #    print(str(animal[0]) + " " + str(animal[1]) + " " + str(animal[2]) + " " + str(animal[3]))

        print("Sorting...")
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
            #if len(hsi_bull_ret) >= 2:
                #hsi_bull_ret = hsi_bull_ret[:min_pos] + hsi_bull_ret[min_pos + 1:]
            del(hsi_bull_ret[min_pos])

        while len(hsi_bear_ret) > 0:
            min_pos = 0
            for i in range(0, len(hsi_bear_ret)):
                if hsi_bear_ret[i][factor_pos] < hsi_bear_ret[min_pos][factor_pos]:
                    min_pos = i
            hsi_bear_ret_order.append(hsi_bear_ret[min_pos][0])
            #if len(hsi_bear_ret) >= 2:
                #hsi_bear_ret = hsi_bear_ret[:min_pos] + hsi_bear_ret[min_pos + 1:]
            # hsi_bear_ret = hsi_bear_ret[:min_pos] + hsi_bear_ret[min_pos + 1:]
            del (hsi_bear_ret[min_pos])


        for animal in hsi_bull_ret_order:
            print(str(animal))

        print("******************")
        for animal in hsi_bear_ret_order:
            print(str(animal))
            #print(str(animal[0]) + " " + str(animal[1]) + " " + str(animal[2]) + " " + str(animal[3]))
        print("End")
        return 0, hsi_bull_ret_order, hsi_bear_ret_order




    def find_street_stock(self):
        hsi_animal_list = []
        ret_code, all_warrant = self.quote_ctx.get_stock_basicinfo("HK", stock_type='WARRANT')
        if ret_code != 0:
            return -1, all_warrant, all_warrant

        hsi_animal_cnt = 0
        for i in range(0, len(all_warrant)):
            if all_warrant["owner_stock_code"][i] == "HK.800000" and \
                (all_warrant["stock_child_type"][i] == "BULL" or all_warrant["stock_child_type"][i] == "BEAR"):
                if self.test_name(all_warrant["name"][i]) == False:
                    continue

                holder_num = 0
                hsi_animal_list.append([all_warrant["code"][i], holder_num, all_warrant["stock_child_type"][i]])
                hsi_animal_cnt += 1

        print("Got warrant list")

        bull_cnt, bear_cnt, hsi_animal_ret = self.cal_street(hsi_animal_list)

        result = []
        factor_pos = 0
        while len(hsi_animal_ret) > 0:
            min_pos = 0
            for i in range(0, len(hsi_animal_ret)):
                if hsi_animal_ret[i][factor_pos] < hsi_animal_ret[min_pos][factor_pos]:
                    min_pos = i
            result.append(hsi_animal_ret[min_pos][0])

            del (hsi_animal_ret[min_pos])

        for i in range(0, len(result)):
            print(str(result[i][0]) + ": " + str(result[i][1]))

        print("End")
        return 0, hsi_bull_ret_order, hsi_bear_ret_order







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
    ret, hsi_bull_ret_order, hsi_bear_ret_order = b.find_warrent(500, 600, 40, 0)
    if ret == 0:
        cnt = 0
        for i in range(0, len(hsi_bear_ret_order)):
            # self.watch_warrants.append(hsi_bear_ret_order[i])
            print(hsi_bear_ret_order[i])
            cnt += 1
            if cnt >= 3:
                break
        print("-----------------------")
        cnt = 0
        for i in range(0, len(hsi_bull_ret_order)):
            # self.watch_warrants.append(hsi_bull_ret_order[i])
            print(hsi_bull_ret_order[i])
            cnt += 1
            if cnt >= 3:
                break

    exit(0)


