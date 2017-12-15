# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_exempt    #用于处理post请求出现的错误

from django.shortcuts import render

from django.shortcuts import render
from django.shortcuts import render_to_response

from prob.models import LotteryMonth
from prob.models import Probs
from prob.models import ProbTotals

import urllib2
import json
import simplejson
import time

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
}

def admin(request):
    # ProbTotals.objects.all().delete()
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    lotterys = LotteryMonth.objects.filter(lottery_date=current_date)
    probs = Probs.objects.all()
    prob_totals = ProbTotals.objects.all()
    result_flag = True
    return render_to_response('cross_day_index.html',{'lottery':lotterys,'probs':probs, 'prob_totals':prob_totals,'result_flag':result_flag})

@csrf_exempt   #处理Post请求出错的情况
def index(request):
    p_date = request.POST['in_date']
    # p_number = request.POST['in_number']
    p_monery = request.POST['in_monery']
    p_rule = request.POST['in_rule']
    # print 'p_date is ',p_date,' p_number is ',p_number, ' p_monery is ',p_monery
    print 'p_date is ',p_date, 'p_monery is ',p_monery
    in_date = p_date
    url = "http://api.api68.com/pks/getPksHistoryList.do?date=" + in_date + "&lotCode=10001"
    print url

    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    history_data = LotteryMonth.objects.all()
    #当天时间
    if (current_date == in_date):
        print 'today ,delete old data'
        LotteryMonth.objects.filter(lottery_date=in_date).delete()
        result_flag = spider_today(url)
        if(result_flag):
            print 'today spider success'
        else:
            print 'today spider faild'
        lotterys = LotteryMonth.objects.filter(lottery_date=in_date)
        print "today count is ",len(lotterys)
    #历史时间
    else:
        print 'history'
        lotterys = LotteryMonth.objects.filter(lottery_date=in_date)
        print len(lotterys)
        #有记录
        if (lotterys):
            print  'exists'
            #等于179不采集
            if (len(lotterys) == 179):
                print 'data right'
                result_flag = True
            #不等于179删除重新采集
            else:
                print 'data lost or rongyu!'
                LotteryMonth.objects.filter(lottery_date=in_date).delete()
                result_flag = spider_history(url)
                if (result_flag):
                    print 'history spider success'
                    lotterys = LotteryMonth.objects.filter(lottery_date=in_date)
                else:
                    print ' history spider faild'
        #没有任何记录
        else:
            # LotteryMonth.objects.filter(lottery_date=in_date).delete
            print 'not exists'
            #返回True,采集完成，否则采集失败
            result_flag = spider_history(url)
            if (result_flag):
                print 'history spider success'
                lotterys = LotteryMonth.objects.filter(lottery_date=in_date)
            else:
                print ' history spider faild'
    #格式转换，评估
    # print "......................"
    # base_lottery_list,base_lottery_list_left_right_change,parity_lottery_list,larsma_lottery_list = parase_lotterys(lotterys)
    p_rule = int(p_rule)
    p_number = 2
    num = int(p_number)
    monery = int(p_monery)
    #获取规则
    rule_num_list = get_num_rule(p_number)
    #将model数据转换成对应的数组
    base_lottery_list,base_lottery_list_left_right_change = parase_lotterys(lotterys)

    if (p_rule == 1):
        ############################################################规则一
        print 'day rule 1'
        column_num = 10
        calc_num = 3
        #对角线转换
        tran_cross_lottery_list = tran_croos_data(base_lottery_list, column_num, calc_num)
        tran_cross_lottery_list_left_right_change = tran_croos_data(base_lottery_list_left_right_change, column_num, calc_num)
        #评估
        evaluation_num(monery,num,tran_cross_lottery_list,rule_num_list, tran_cross_lottery_list_left_right_change)
    if(p_rule == 2):
        ############################################################规则二
        #将model数据转换成对应的数组
        print 'day rule 2'
        evaluation_column(monery,num,base_lottery_list,rule_num_list)

    #获取规则 原始
    # rule_parity_list,rule_larsma_list = get_rule(p_rule)
    # evaluation(monery, num, parity_lottery_list, rule_parity_list, larsma_lottery_list, rule_larsma_list )
    probs = Probs.objects.all()
    prob_totals = ProbTotals.objects.all()
    return render_to_response('cross_day_index.html',{'lottery':lotterys,'probs':probs,'prob_totals':prob_totals,
                                            'p_date':p_date, 'p_number':p_number, 'p_monery':p_monery,'p_rule':p_rule, 'result_flag':result_flag})

def get_html(url):
    req = urllib2.Request(url = url, headers = headers)
    page = urllib2.urlopen(req)
    # page = urllib2.urlopen(url)
    html = page.read()
    return html

#当天采集
def spider_today_old(url):
    try:
        html = get_html(url)
        html_json = simplejson.loads(html)
        for i in range(len(html_json['result']['data'])):
            lottery_date = html_json['result']['data'][i]['preDrawTime'][0:10]
            lottery_time = html_json['result']['data'][i]['preDrawTime']
            lottery_id = html_json['result']['data'][i]['preDrawIssue']
            lottery_number = html_json['result']['data'][i]['preDrawCode']

            flag_id = LotteryMonth.objects.filter(lottery_id=lottery_id)
            if (flag_id):
                print lottery_id, ' id exists'
            else:
                print  lottery_id, ' id not exists'
                p = LotteryMonth(lottery_date =lottery_date, lottery_time = lottery_time, lottery_id = lottery_id, lottery_number = lottery_number)
                p.save()

    except:
        print "network is error"
        return False
    return True


#当天采集更新
def spider_today(url):
    try:
        html = get_html(url)
        html_json = simplejson.loads(html)
        # print html_json
        for i in range(len(html_json['result']['data'])):
            lottery_month = html_json['result']['data'][i]['preDrawTime'][0:7]
            lottery_date = html_json['result']['data'][i]['preDrawTime'][0:10]
            lottery_time = html_json['result']['data'][i]['preDrawTime']
            lottery_id = html_json['result']['data'][i]['preDrawIssue']
            lottery_number = html_json['result']['data'][i]['preDrawCode']

            p = LotteryMonth(lottery_month=lottery_month, lottery_date =lottery_date, lottery_time = lottery_time, lottery_id = lottery_id, lottery_number = lottery_number)
            p.save()

    except:
        print "network is error"
        return False
    return True

#历史采集
def spider_history(url):
    try:
        html = get_html(url)
        html_json = simplejson.loads(html)
        for i in range(len(html_json['result']['data'])):
            lottery_month = html_json['result']['data'][i]['preDrawTime'][0:7]
            lottery_date = html_json['result']['data'][i]['preDrawTime'][0:10]
            lottery_time = html_json['result']['data'][i]['preDrawTime']
            lottery_id = html_json['result']['data'][i]['preDrawIssue']
            lottery_number = html_json['result']['data'][i]['preDrawCode']

            p = LotteryMonth(lottery_month=lottery_month, lottery_date =lottery_date, lottery_time = lottery_time, lottery_id = lottery_id, lottery_number = lottery_number)
            p.save()
    except:
        print "network is error"
        return False
    return True


#格式转换
#首行和末行已转换，已转换成正式查询数组
def parase_lotterys(lottery):

    #定义行列矩阵,179列，10行，基础数组，原始数据，前后互换
    base_lottery_list = [[0 for i in range(10)] for i in range(len(lottery))]

    #定义数据10行，179列，第一列与最后一列互换,左右互换
    base_lottery_list_left_right_change = [[0 for i in range(10)] for i in range(len(lottery))]

    count = 0
    for loty in lottery:
        # print loty.lottery_number
        temp_lotys = loty.lottery_number.split(',')
        #数组宽度
        wid_length = len(temp_lotys)
        for i in range(wid_length):
            sub_num = int(temp_lotys[i])
            #第一行与最后一样转换
            base_lottery_list[len(lottery) - count - 1][i] = sub_num
            base_lottery_list_left_right_change[len(lottery) - count - 1][wid_length - i - 1] = sub_num

        count = count + 1

    #base_lottery_list首行和末行已转换，已转换成正式查询数组;  base_lottery_list_left_right_change  首行和末行转换后再左右转换，便于逆向查询
    return base_lottery_list,base_lottery_list_left_right_change


#交叉规则转换，将原始数据，转换成对角数据
def tran_croos_data(base_data,column_num, calc_num):

    for i in range(int(column_num-calc_num)):
        base_data.append([0]*column_num)
        base_data.insert(0,[0]*column_num)

    #定义最终的数组list
    cross_data_list = [[0 for i in range(column_num)] for i in range(len(base_data) - (column_num-calc_num) - (calc_num - 1))]

    row_num = 0
    max = len(base_data) - (column_num-calc_num) - (calc_num - 1)
    while(row_num<max):
        for cloumn_num in range(len(base_data[row_num])):
            cross_data_list[row_num][cloumn_num] = base_data[row_num+cloumn_num][cloumn_num]
        row_num = row_num + 1
    return cross_data_list

#数字规则
def get_num_rule(p_number):
    #数字规则
    rule_num_list = []
    rule_times = int(p_number) + 1
    for i in range(10):
        num = i + 1
        rule_num_list.append([num]*rule_times)
    return rule_num_list

#交叉计算评估
def evaluation_num(monery,num,tran_cross_lottery_list,rule_num_list, tran_cross_lottery_list_left_right_change):
    print "evaluation..."
    #删除object,再将计算结果写入
    Probs.objects.all().delete()
    ProbTotals.objects.all().delete()

    #正向和反向
    for i in range(2):
        #第几名即 第几列写入prob_range
        if  i == 0:
            prob_range = '正方向'
            cross_lottery_list = tran_cross_lottery_list
        else:
            prob_range = '反方向'
            cross_lottery_list = tran_cross_lottery_list_left_right_change
        # print "1--->  ",prob_range
        for rule_parity in rule_num_list:
            # print 'rule_parity ',rule_parity
            #哪种规则 prob_rule
            prob_rule = ''
            for rule in rule_parity:
                prob_rule = prob_rule + str(rule)
            prob_match = 0
            prob_nomatch = 0
            for cross_lottery in cross_lottery_list:

                #填充规则数据
                rule_num = rule_parity
                target = cross_lottery
                prob_value_tmp = [0] * len(target)
                # print "target  ,rule_num  ",target,rule_num
                prob_value = compute_rule(num, rule_num, target, prob_value_tmp)
                # print "prob_value is ",prob_value
                #开始计算行数据 1的个数，-1的个数
                prob_match = prob_match + prob_value.count(1)
                # print 'prob_match ',prob_match
                prob_nomatch = prob_nomatch + prob_value.count(-1)

            # print 'prob_match ',prob_match
            # print 'prob_nomatch ',prob_nomatch
            prob_bet = prob_match + prob_nomatch

            prob_amount = prob_bet * monery
            # prob_win = prob_match * monery * 0.97 - prob_nomatch * monery
            # prob_lose = prob_nomatch * monery
            # prob_gain = prob_win - prob_lose

            prob_win = prob_match * monery * 9.8
            prob_lose = prob_nomatch * monery
            prob_gain = prob_match * monery * 8.8 - prob_nomatch * monery

            #结果值记录总统计
            # total_prob_value[i].append(prob_value)
            #写入对象
            obj_pro = Probs(prob_range=prob_range, prob_rule=prob_rule, prob_match=prob_match, prob_nomatch=prob_nomatch,
                            prob_bet=prob_bet, prob_amount=prob_amount, prob_win=prob_win, prob_lose=prob_lose, prob_gain=prob_gain )
            #, prob_win=prob_win, prob_lose=prob_lose, prob_gain=prob_gain
            obj_pro.save()

    current_probs = Probs.objects.all()
    # current_probtatol = ProbTotal.objects.all()
    for current_prob in current_probs:
         if(ProbTotals.objects.filter(probtotal_rule=current_prob.prob_rule)):
             tmp_match = ProbTotals.objects.get(
                 probtotal_rule=current_prob.prob_rule).probtotal_match + current_prob.prob_match
             tmp_nomatch = ProbTotals.objects.get(
                 probtotal_rule=current_prob.prob_rule).probtotal_nomatch + current_prob.prob_nomatch
             tmp_bet = ProbTotals.objects.get(
                 probtotal_rule=current_prob.prob_rule).probtotal_bet + current_prob.prob_bet


             tmp_amount = ProbTotals.objects.get(
                 probtotal_rule=current_prob.prob_rule).probtotal_amount + current_prob.prob_amount
             tmp_win = ProbTotals.objects.get(
                 probtotal_rule=current_prob.prob_rule).probtotal_win + current_prob.prob_win
             tmp_lose = ProbTotals.objects.get(
                 probtotal_rule=current_prob.prob_rule).probtotal_lose + current_prob.prob_lose
             tmp_gain = ProbTotals.objects.get(
                 probtotal_rule=current_prob.prob_rule).probtotal_gain + current_prob.prob_gain


             tmp_count_obj = ProbTotals.objects.get(probtotal_rule=current_prob.prob_rule)

             tmp_count_obj.probtotal_match = tmp_match
             tmp_count_obj.probtotal_nomatch = tmp_nomatch
             tmp_count_obj.probtotal_bet = tmp_bet

             tmp_count_obj.probtotal_amount = tmp_amount
             tmp_count_obj.probtotal_win = tmp_win
             tmp_count_obj.probtotal_lose = tmp_lose
             tmp_count_obj.probtotal_gain = tmp_gain
             tmp_count_obj.save()
         else:
             tmp_probtotal = ProbTotals(probtotal_rule=current_prob.prob_rule, probtotal_match=current_prob.prob_match,
                        probtotal_nomatch=current_prob.prob_nomatch,probtotal_bet=current_prob.prob_bet,probtotal_amount=current_prob.prob_amount,
                       probtotal_win=current_prob.prob_win, probtotal_lose=current_prob.prob_lose,probtotal_gain=current_prob.prob_gain)
             tmp_probtotal.save()

    all_total_match = 0
    all_total_nomatch = 0
    all_total_bet = 0
    all_total_amont = 0
    all_total_win = 0
    all_total_lose = 0
    all_total_gain = 0
    for x in ProbTotals.objects.all():
        all_total_match = all_total_match + x.probtotal_match
        all_total_nomatch = all_total_nomatch + x.probtotal_nomatch
        all_total_bet = all_total_bet + x.probtotal_bet

        all_total_amont = all_total_amont + x.probtotal_amount
        all_total_win = all_total_win + x.probtotal_win
        all_total_lose = all_total_lose + x.probtotal_lose
        all_total_gain = all_total_gain + x.probtotal_gain
        # print x.probtotal_rule, '   ', x.probtotal_match,'   ',x.probtotal_nomatch,'   ',x.probtotal_bet,'   ',x.probtotal_amount,'   ', x.probtotal_win,'   ',x.probtotal_lose,'   ',x.probtotal_gain
    tmp_all_total_obj = ProbTotals(probtotal_rule='总记录', probtotal_match=all_total_match, probtotal_nomatch=all_total_nomatch,
                        probtotal_bet=all_total_bet,probtotal_amount=all_total_amont,
                       probtotal_win=all_total_win, probtotal_lose=all_total_lose,probtotal_gain=all_total_gain)
    tmp_all_total_obj.save()

#直线统计评估
def evaluation_column(monery, num, parity_lottery_list, rule_parity_list):
    print "evaluation..."
    #删除object,再将计算结果写入
    Probs.objects.all().delete()
    ProbTotals.objects.all().delete()

    # f = open('result.txt','w')
    #行列转置
    tran_parity_lottery_list = map(list, zip(*parity_lottery_list))

    total_prob_value = [[]] * 10
    for i in range(len(tran_parity_lottery_list)):
        #第几名即 第几列写入prob_range
        prob_range = '第' + str(i+1) + '名'
        j = 0
        for rule_parity in rule_parity_list:
            # print 'rule_parity ',rule_parity
            #哪种规则 prob_rule
            prob_rule = ''
            for rule in rule_parity:
                prob_rule = prob_rule + str(rule)

            #填充规则数据
            rule_parity = rule_parity
            target = tran_parity_lottery_list[i]
            prob_value = [0] * len(target)

            prob_value = compute_rule(num, rule_parity, target, prob_value)
            # print 'prob_value  ',prob_value
            # f.write(str(prob_value))
            # f.write('\n')
            #
            # f.close()
            #开始计算行数据 1的个数，-1的个数
            prob_match = prob_value.count(1)
            # print 'prob_match ',prob_match
            prob_nomatch = prob_value.count(-1)
            # print 'prob_nomatch ',prob_nomatch
            prob_bet = prob_match + prob_nomatch

            prob_amount = prob_bet * monery
            # prob_win = prob_match * monery * 0.97 - prob_nomatch * monery
            # prob_lose = prob_nomatch * monery
            # prob_gain = prob_win - prob_lose

            prob_win = prob_match * monery * 9.8
            prob_lose = prob_nomatch * monery
            prob_gain = prob_match * monery * 8.8 - prob_nomatch * monery

            #结果值记录总统计
            total_prob_value[i].append(prob_value)
            if (prob_match == 0 and prob_nomatch == 0):
                pass
            else:
                #写入对象
                obj_pro = Probs(prob_range=prob_range, prob_rule=prob_rule, prob_match=prob_match, prob_nomatch=prob_nomatch,
                                prob_bet=prob_bet, prob_amount=prob_amount, prob_win=prob_win, prob_lose=prob_lose, prob_gain=prob_gain )
                #, prob_win=prob_win, prob_lose=prob_lose, prob_gain=prob_gain
                obj_pro.save()

            j = j + 1

    current_probs = Probs.objects.all()
    # current_probtatol = ProbTotal.objects.all()
    for current_prob in current_probs:
         if(ProbTotals.objects.filter(probtotal_rule=current_prob.prob_rule)):
             tmp_match = ProbTotals.objects.get(
                 probtotal_rule=current_prob.prob_rule).probtotal_match + current_prob.prob_match
             tmp_nomatch = ProbTotals.objects.get(
                 probtotal_rule=current_prob.prob_rule).probtotal_nomatch + current_prob.prob_nomatch
             tmp_bet = ProbTotals.objects.get(
                 probtotal_rule=current_prob.prob_rule).probtotal_bet + current_prob.prob_bet


             tmp_amount = ProbTotals.objects.get(
                 probtotal_rule=current_prob.prob_rule).probtotal_amount + current_prob.prob_amount
             tmp_win = ProbTotals.objects.get(
                 probtotal_rule=current_prob.prob_rule).probtotal_win + current_prob.prob_win
             tmp_lose = ProbTotals.objects.get(
                 probtotal_rule=current_prob.prob_rule).probtotal_lose + current_prob.prob_lose
             tmp_gain = ProbTotals.objects.get(
                 probtotal_rule=current_prob.prob_rule).probtotal_gain + current_prob.prob_gain


             tmp_count_obj = ProbTotals.objects.get(probtotal_rule=current_prob.prob_rule)

             tmp_count_obj.probtotal_match = tmp_match
             tmp_count_obj.probtotal_nomatch = tmp_nomatch
             tmp_count_obj.probtotal_bet = tmp_bet

             tmp_count_obj.probtotal_amount = tmp_amount
             tmp_count_obj.probtotal_win = tmp_win
             tmp_count_obj.probtotal_lose = tmp_lose
             tmp_count_obj.probtotal_gain = tmp_gain
             tmp_count_obj.save()
         else:
             tmp_probtotal = ProbTotals(probtotal_rule=current_prob.prob_rule, probtotal_match=current_prob.prob_match,
                        probtotal_nomatch=current_prob.prob_nomatch,probtotal_bet=current_prob.prob_bet,probtotal_amount=current_prob.prob_amount,
                       probtotal_win=current_prob.prob_win, probtotal_lose=current_prob.prob_lose,probtotal_gain=current_prob.prob_gain)
             tmp_probtotal.save()

    all_total_match = 0
    all_total_nomatch = 0
    all_total_bet = 0
    all_total_amont = 0
    all_total_win = 0
    all_total_lose = 0
    all_total_gain = 0
    for x in ProbTotals.objects.all():
        all_total_match = all_total_match + x.probtotal_match
        all_total_nomatch = all_total_nomatch + x.probtotal_nomatch
        all_total_bet = all_total_bet + x.probtotal_bet

        all_total_amont = all_total_amont + x.probtotal_amount
        all_total_win = all_total_win + x.probtotal_win
        all_total_lose = all_total_lose + x.probtotal_lose
        all_total_gain = all_total_gain + x.probtotal_gain
        # print x.probtotal_rule, '   ', x.probtotal_match,'   ',x.probtotal_nomatch,'   ',x.probtotal_bet,'   ',x.probtotal_amount,'   ', x.probtotal_win,'   ',x.probtotal_lose,'   ',x.probtotal_gain
    tmp_all_total_obj = ProbTotals(probtotal_rule='总记录', probtotal_match=all_total_match, probtotal_nomatch=all_total_nomatch,
                        probtotal_bet=all_total_bet,probtotal_amount=all_total_amont,
                       probtotal_win=all_total_win, probtotal_lose=all_total_lose,probtotal_gain=all_total_gain)
    tmp_all_total_obj.save()


##计算规则，出现相同的时候，判断下一个是否一致，不一致为-1，一致为1，重新开始判断
def compute_rule(num, rule, target, prob_value):
    count = 0
    index = 0
    max = len(target)- num
    while(count < max):
        if(target[count:count+num] == rule[index:index+num]):
            # print target[count:count+num]
            #进一步判断target下一位与rule的下一位是否相等
            count = count + num
            index = index + num

            if(target[count] == rule[index]):
                prob_value[count] = 1
                count = count + 1
                index = 0
                #如果到最后一个，跳出循环
                if (count >= len(target)):
                    break
            else:
                #循环结束即target下一位与rule的下一位不相等，记为-1
                #下一位开始计数
                if (count >= len(target)):
                    break
                else:
                    prob_value[count] = -1
                    count = count + 1
                    index = 0
        else:
            # print "不满足",count
            count = count + 1

    return prob_value

