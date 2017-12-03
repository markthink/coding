# -*- coding=utf-8 -*-
import datetime

# 根据日期获取周信息
def week_get(vdate):
    dayscount = datetime.timedelta(days=vdate.isoweekday())
    dayfrom = vdate - dayscount + datetime.timedelta(days=1)
    dayto = vdate - dayscount + datetime.timedelta(days=7)
    print(' ~~ '.join([str(dayfrom), str(dayto)]))
    week7 = []
    i = 0
    while (i <= 6):
        week7.append('周' + str(i + 1) + ': ' + str(dayfrom + datetime.timedelta(days=i)))
        i += 1
    return week7


if __name__ == '__main__':
    vdate_str = '2017-08-25'
    vdate = datetime.datetime.strptime(vdate_str, '%Y-%m-%d').date()

    for week in week_get(vdate):
        print(week)