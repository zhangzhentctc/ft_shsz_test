import pandas as pd
import numpy as np
from pandas import DataFrame, Series
import matplotlib.pyplot as plt
import datetime
import calendar
import random

start = '2010-01-04'
end = '2016-10-01'
df = get_price('000157.XSHE', start, end, '1d', ['high'])
highprice0 = df['high']


# 用拉格朗日型二次插值函数拟合，并求出实际值与拟合值之间的差值：
def Lagrange_residual(a, min_point, b, highprice):
    max_residual = 0
    for i in range(a + 1, b):
        L0 = (i - min_point) * (i - b) / ((a - min_point) * (a - b))
        L1 = (i - a) * (i - b) / ((min_point - a) * (min_point - b))
        L2 = (i - min_point) * (i - a) / ((b - min_point) * (b - a))
        interpolation = L0 * highprice[a] + L1 * highprice[min_point] + L2 * highprice[b]
        residual = highprice[i] - interpolation
        if residual > max_residual:
            max_residual = residual

    return max_residual


# 计算周的数量
n = int(len(highprice0) / 5)

# 计算周K线的最高价
highprice = [0] * n

for i in range(n):
    highprice[i] = max(highprice0[i * 5:(i + 1) * 5])

fig_size = plt.rcParams['figure.figsize']
fig_size[0] = 12
fig_size[1] = 8

plt.plot(range(n), highprice, 'k')

random_point_c = random.choice(range(241, 255))
print(random_point_c)
plt.scatter(random_point_c, highprice[random_point_c], color='black')

gama = 1  # gama为B点相对于C点高度的系数
span_request_bc = 0  # B点与C点之间的周数至少为span_request_bc

for i in range(n - random_point_c + span_request_bc + 2, n):
    if highprice[-i] > gama * highprice[random_point_c]:
        if highprice[-i - 1] > highprice[-i]:
            continue
        else:
            b = n - i + 1
            if b > random_point_c:
                break

            # List00 = [highprice[k]>highprice[b] for k in range(int((random_point_c+b)/2),random_point_c)]
            #             if True in List0:
            #                 continue
            else:
                print(b)
                plt.scatter(b, highprice[b], color='blue')
                break

span_bc = random_point_c - b  # span_bc为B点和C点之间间隔的周数
omega = 1  # omega为A点相对于B点高度的系数
span = 10  # span为时间跨度的周数

for i in range(n - b + span + 2, n):
    if highprice[-i] > omega * highprice[b]:
        if highprice[-i - 1] > highprice[-i]:
            continue
        else:
            a = n - i + 1
            if a > b:
                break
            else:
                #                 List0 = [highprice[k]>highprice[b] for k in range(int((a+b)/2),b)]
                #                 if True in List0:
                #                     continue

                #                 one_third = int(a+(b-a)/3)
                #                 two_third = int(a+(b-a)*2/3)

                # 用拉格朗日型二次插值函数拟合：
                # 首先找出a-b间的最低点

                min_point = highprice[a:b].index(min(highprice[a:b])) + a
                #                 print(min_point)

                if min_point == a:
                    continue
                else:
                    residual = Lagrange_residual(a, min_point, b, highprice)
                    if residual > 20:
                        print(residual)
                        continue
                    else:

                        #                     List = [highprice[k]>(highprice[one_third]+highprice[two_third])/2 for k in range(one_third+1,two_third)]
                        #                     if True in List:
                        #                         continue
                        #                     else:
                        print(a)
                        plt.scatter(a, highprice[a], color='red')

                        # 找C点
                        for m in range(random_point_c, n):
                            if highprice[m] > highprice[b]:
                                c = m
                                plt.scatter(c, highprice[c], color='pink')
                                break

                        break
