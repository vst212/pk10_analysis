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
from cross.cross_day import tran_croos_data,get_num_rule,evaluation_num,parase_lotterys,evaluation_column

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
}

def admin_month(request):
    # ProbTotals.objects.all().delete()
    current_month = time.strftime('%Y-%m',time.localtime(time.time()))
    lotterys = LotteryMonth.objects.filter(lottery_month = current_month).order_by('-lottery_id')
    probs = Probs.objects.all()
    prob_totals = ProbTotals.objects.all()
    result_flag = True
    return render_to_response('cross_month_index.html',{'lottery':lotterys,'probs':probs, 'prob_totals':prob_totals, 'result_flag': result_flag})

@csrf_exempt   #处理Post请求出错的情况
def index_month(request):
    p_date = request.POST['in_month_date']
    p_month = p_date[0:7]
    p_day = p_date.split('-')[-1]
    spider_faild_date_list = []

    print 'p_date is ',p_date, ' ',p_month,'  ', p_day
    # in_date = '2017-11-02'
    # in_date = p_date


    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    for day in range(int(p_day)):
        in_date = p_month + '-' + (str(day+1)).zfill(2)
        print in_date
        url = "http://api.api68.com/pks/getPksHistoryList.do?date=" + in_date + "&lotCode=10001"
        print url

        #当天时间
        if (current_date == in_date):
            print 'today ,delete old data'
            LotteryMonth.objects.filter(lottery_date=in_date).delete()
            result_flag = spider_today(url)
            if(result_flag):
                print in_date,' today spider success'
            else:
                print in_date,' today spider faild'
                spider_faild_date_list.append(in_date)
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
                if (len(lotterys) ==179):
                    print in_date,'data right'
                    result_flag = True
                #不等于179删除重新采集
                else:
                    print in_date,'data lost or rongyu!'
                    LotteryMonth.objects.filter(lottery_date=in_date).delete()
                    result_flag = spider_history(url)
                    if (result_flag):
                        print in_date,' history spider success'
                        lotterys = LotteryMonth.objects.filter(lottery_date=in_date)
                    else:
                        print in_date,' history spider faild'
                        spider_faild_date_list.append(in_date)
            #没有任何记录
            else:
                # Lottery.objects.filter(lottery_date=in_date).delete
                print 'not exists'
                #返回True,采集完成，否则采集失败
                result_flag = spider_history(url)
                if (result_flag):
                    print in_date,' history spider success'
                    lotterys = LotteryMonth.objects.filter(lottery_date=in_date)
                else:
                    print in_date, ' history spider faild'
                    spider_faild_date_list.append(in_date)


    ################################################################
    probs = Probs.objects.all()
    prob_totals = ProbTotals.objects.all()
    lotterys = LotteryMonth.objects.filter(lottery_month = p_month).order_by('-lottery_id')
    if(spider_faild_date_list):
        print 'spider faild is ',spider_faild_date_list
        result_flag = False
    else:
        result_flag = True
    return render_to_response('cross_month_index.html',{'lottery': lotterys,'faild_date':spider_faild_date_list,'p_date':p_date, 'result_flag': result_flag} )

#评估
@csrf_exempt   #处理Post请求出错的情况
def index_month_evaluation(request):
    p_date = request.POST['in_date']
    # p_number = request.POST['in_number']
    p_monery = request.POST['in_monery']

    p_rule = request.POST['in_rule']
    p_month = p_date[0:7]
    # print 'p_date is ',p_date,' p_number is ',p_number, ' p_monery is ',p_monery, 'p_month is ',p_month
    print 'p_date is ',p_date, ' p_monery is ',p_monery, 'p_month is ',p_month
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))

    #格式转换，评估
    lotterys = LotteryMonth.objects.filter(lottery_month=p_month).order_by('-lottery_id')
    #将model数据转换成对应的数组
    base_lottery_list,base_lottery_list_left_right_change = parase_lotterys(lotterys)
    p_number = 2
    num = int(p_number)
    monery = int(p_monery)
    p_rule = int(p_rule)
    rule_num_list = get_num_rule(p_number)
    if (p_rule == 1):
        ###################################规则一
        print 'month rule 1'
        #对角线转换，适用于对角线运算
        column_num = 10
        calc_num = 3
        tran_cross_lottery_list = tran_croos_data(base_lottery_list, column_num, calc_num)
        tran_cross_lottery_list_left_right_change = tran_croos_data(base_lottery_list_left_right_change, column_num, calc_num)
        #评估
        evaluation_num(monery,num,tran_cross_lottery_list,rule_num_list, tran_cross_lottery_list_left_right_change)
    if (p_rule == 2):
        ###################################规则一
        print 'month rule 2'
        evaluation_column(monery,num,base_lottery_list,rule_num_list)

    probs = Probs.objects.all()
    prob_totals = ProbTotals.objects.all()
    result_flag = True
    return render_to_response('cross_month_index.html',{'lottery':lotterys,'probs':probs,'prob_totals':prob_totals,
                                            'p_date':p_date, 'p_number':p_number, 'p_monery':p_monery,
                                                  'p_rule':p_rule, 'result_flag':result_flag})

def get_html(url):
    try:
        req = urllib2.Request(url = url, headers = headers)
        page = urllib2.urlopen(req,timeout = 10)
        html = page.read()
    except:
        html = None
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
        if(html):
            html_json = simplejson.loads(html)
            # print html_json
            for i in range(len(html_json['result']['data'])):
                lottery_month = html_json['result']['data'][i]['preDrawTime'][0:7]
                lottery_date = html_json['result']['data'][i]['preDrawTime'][0:10]
                lottery_time = html_json['result']['data'][i]['preDrawTime']
                lottery_id = html_json['result']['data'][i]['preDrawIssue']
                lottery_number = html_json['result']['data'][i]['preDrawCode']

                p = LotteryMonth(lottery_month = lottery_month, lottery_date = lottery_date, lottery_time = lottery_time,
                            lottery_id = lottery_id, lottery_number = lottery_number)
                p.save()
        else:
            return False

    except:
        print "network is error"
        return False
    return True

#历史采集
def spider_history(url):
    try:
        html = get_html(url)
        if(html):
            html_json = simplejson.loads(html)
            for i in range(len(html_json['result']['data'])):
                lottery_month = html_json['result']['data'][i]['preDrawTime'][0:7]
                lottery_date = html_json['result']['data'][i]['preDrawTime'][0:10]
                lottery_time = html_json['result']['data'][i]['preDrawTime']
                lottery_id = html_json['result']['data'][i]['preDrawIssue']
                lottery_number = html_json['result']['data'][i]['preDrawCode']

                p = LotteryMonth(lottery_month = lottery_month, lottery_date =lottery_date, lottery_time = lottery_time,
                                 lottery_id = lottery_id, lottery_number = lottery_number)
                p.save()
        else:
            return False
    except:
        print "network is error"
        return False
    return True
