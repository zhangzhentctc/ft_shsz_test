import pandas as pd
import numpy as np
from pandas import DataFrame, Series
import matplotlib.pyplot as plt
import datetime
import calendar
import random

start = '2005-01-04'
end = '2016-10-01'
df = get_price('000639.XSHE', start, end, '1d', ['open', 'close', 'high', 'low', 'volume'])
closeprice0 = df['close']
highprice0 = df['high']

# 计算周的数量
# startday = datetime.datetime(2015,1,1,0,0,0)
# weekday_start = startday.weekday()
# if weekday_start != 0:
#     startday +=  datetime.timedelta(days = weekday_start)
# endday = datetime.datetime(2016,10,1,0,0,0)
# lag = (endday-startday).days

week_cnt = int(len(closeprice0) / 5)
print(week_cnt)

# 计算周K线的最高价
closeprice_week = [0] * week_cnt
highprice_week = [0] * week_cnt
for i in range(week_cnt):
    closeprice_week[i] = closeprice0[i * 5:(i + 1) * 5][4]
    highprice_week[i] = max(highprice0[i * 5:(i + 1) * 5])

fig_size = plt.rcParams['figure.figsize']
fig_size[0] = 12
fig_size[1] = 8

plt.plot(range(week_cnt), highprice_week, 'k')

random_point_c = random.choice(range(week_cnt))  # 随机选取random_point_c代表今天
print(random_point_c)
plt.scatter(random_point_c, highprice_week[random_point_c], color='green')

# Set Parameters
para_gama = 1  # gama为B点相对于C点高度的系数
para_span_request_bc = 3  # B点与C点之间的周数至少为span_request_bc

for i in range(week_cnt - random_point_c + para_span_request_bc + 1, week_cnt):
    if highprice_week[-i] > para_gama * highprice_week[random_point_c]:
        if highprice_week[-i - 1] > highprice_week[-i]:
            continue
        else:
            point_b = week_cnt - i + 1
            if point_b > random_point_c:
                break
            else:
                print(point_b)
                plt.scatter(point_b, highprice_week[-i], color='blue')
                break

span_bc = random_point_c - point_b  # span_bc为B点和C点之间间隔的周数
omega = 1.05  # omega为A点相对于B点高度的系数
span = 7  # span为时间跨度的周数
for i in range(week_cnt - point_b + span + 1, week_cnt):
    if highprice_week[-i] > omega * highprice_week[point_b]:
        if highprice_week[-i - 1] > highprice_week[-i]:
            continue
        else:
            point_a = week_cnt - i + 1
            if point_a > point_b:
                break
            else:
                one_third = int(point_a + (point_b - point_a) / 3)
                two_third = int(point_a + (point_b - point_a) * 2 / 3)
                List = [highprice_week[k] > max(highprice_week[one_third], highprice_week[two_third]) for k in
                        range(one_third + 1, two_third)]
                if True in List:
                    continue
                else:
                    print(point_a)
                    plt.scatter(point_a, highprice_week[-i], color='red')

                    # 找C点
                    for m in range(random_point_c, week_cnt):
                        if highprice_week[m] > highprice_week[point_b]:
                            c = m
                            plt.scatter(c, highprice_week[c], color='pink')
                            break

                    break