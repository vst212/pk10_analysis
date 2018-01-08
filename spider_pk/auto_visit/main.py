# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.decorators.csrf import csrf_exempt    #用于处理post请求出现的错误

from django.shortcuts import render
from django.shortcuts import render_to_response
from auto_visit.models import ProbUser
from auto_visit.thread import ThreadControl

from auto_visit.spider import spider_current_date_data
from prob.models import LotteryMonth
from auto_visit.models import PurchaseRecord
from auto_visit.pretreatment import get_rule, parase_lotterys,check_double_match,check_single_match

# Create your views here.
import time

def pk10_view(request):
    thread_status = False
    info_active = True
    user_name = "test"
    prob_user_list =  ProbUser.objects.get(user_name=user_name)
    for prob_user in prob_user_list:
        c  = ThreadControl()
        try:
            #查看是否处于活跃状态
            status = c.is_alive(prob_user.user_name)
            if status:
                #设置状态为1
                prob_user.user_status = 1
                prob_user.save()
            else:
                #设置状态为0
                prob_user.user_status = 0
                prob_user.save()
        except:
            prob_user.user_status = 0
            prob_user.save()
    # return render_to_response('qzone_info.html',{"info_active":info_active , "thread_list":thread_list})


@csrf_exempt   #处理Post请求出错的情况
def control_probuser_thread(request):
    user_name = request.POST['user_name']
    control = request.POST['control']
    # user_name = "test"
    # control = "start"
    print "user_name is ",user_name
    #显示活跃状态
    info_active = True
    prob_user = ProbUser.objects.get(user_name=user_name)
    if control == 'start':
        #状态信息
        # thread1_status = True
        c  = ThreadControl()
        # status = 1
        #出现错误，则线程不存在，因此启动线程
        try:
            status = c.is_alive(user_name)
            print "thread is alive? ",status
            if status:
                print "thread is alive,caonot start twice!"
            else:
                print "start ..........thread1"
                c.start(user_name,1)
        except:
            print "thread is not alive start!!!"
            c.start(user_name,1)
        prob_user.user_status = 1
        prob_user.save()
    if control == 'stop':
        c  = ThreadControl()
        try:
            c.stop(user_name)
            prob_user.user_status = 0
            prob_user.save()
        except:
            print "not thread alive"
    prob_user_list =  ProbUser.objects.all()
    return render_to_response('auto_main.html',{"prob_user_list":prob_user_list})
    # return render_to_response('qzone_info.html',{"thread_name":th_name, "control":control, "thread_list":thread_list,"info_active":info_active})

#主页面
def auto_admin(request):
    # ProbTotals.objects.all().delete()
    # thread_list =  ProbUser.objects.get(thread_name=th_name)
    prob_user_list =  ProbUser.objects.all()
    for prob_user in prob_user_list:
        c  = ThreadControl()
        try:
            #查看是否处于活跃状态
            status = c.is_alive(prob_user.user_name)
            if status:
                #设置状态为1
                prob_user.user_status = 1
                prob_user.save()
            else:
                #设置状态为0
                prob_user.user_status = 0
                prob_user.save()
        except:
            print prob_user.user_name, " not start"
            prob_user.user_status = 0
            prob_user.save()
    return render_to_response('auto_main.html',{"prob_user_list":prob_user_list})

def set_user_data(request):
    #写入对象
    user_id = 2
    user_name = "aabb"
    user_password = "123"
    user_status = False
    obj_pro = ProbUser(user_id=user_id, user_name=user_name, user_password=user_password, user_status=user_status)
    obj_pro.save()
    return render_to_response('test.html',{"obj_pro":obj_pro})

# def get_user_data(request):
#
#     rule = 1
#     money = 10
#     upper_money = 30
#     spider_current_date_data()
#     current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
#     lotterys = LotteryMonth.objects.filter(lottery_date=current_date)
#     if(rule < 5):
#         rule_parity_list = get_rule(rule)
#         base_lottery_list,parity_lottery_list,larsma_lottery_list = parase_lotterys(lotterys)
#     obj_pro = ProbUser.objects.all()
#     print "obj_pro",obj_pro
#     for pro in obj_pro:
#         print pro.user_name
#     return render_to_response('test.html',{"obj_pro":obj_pro})

def get_prob_data(request):
    rule = 1
    money = 10
    upper_money = 30
    # spider_current_date_data()
    current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    lotterys = LotteryMonth.objects.filter(lottery_date=current_date)
    rule_parity_list = get_rule(rule)
    #当天的开奖记录数
    current_date_rows = LotteryMonth.objects.filter(lottery_date=current_date).order_by("-lottery_id")
    print"len(current_date_rows)" , len(current_date_rows)

    #需要匹配的数目
    match_rule_num = len(rule_parity_list)-1
    #记录小于规则数
    if(len(current_date_rows) < match_rule_num):
        pass
    else:
        lottery_max_num = current_date_rows[0].lottery_id
        purchase_date_rows = PurchaseRecord.objects.filter(purchase_record_date=current_date).order_by("-purchase_record_id")
        if(len(purchase_date_rows) == 0):
            #直接匹配
            pass
        else:
            purchase_max_num = purchase_date_rows[0].purchase_record_id
            lottery_minus_purchase_len = lottery_max_num - purchase_max_num
            if(lottery_minus_purchase_len >= match_rule_num):
                #单双规则
                if (rule < 5):
                    base_lottery_list, parity_lottery_list, larsma_lottery_list = parase_lotterys(lotterys)
                    column = 1
                    purchase_record_column_list = []
                    purchase_record_value_list = []
                    #从第一名到第十名
                    for parity_lottery in parity_lottery_list:
                        target = parity_lottery[-lottery_minus_purchase_len:]
                        #查看是否匹配
                        result = check_single_match(target,rule_parity_list)
                        if (result == -1):
                            pass
                        else:
                            purchase_record_value = result
                            purchase_record_value_list.append(purchase_record_value)
                            purchase_record_column = column
                            purchase_record_column_list.append(purchase_record_column)
                        column = column + 1
                    for i in range(len(purchase_record_column_list)):
                        #构造path
                        if(purchase_record_value_list[i] == 0):
                            xpath = '//*[@id="itmStakeInput20'+ str(purchase_record_column_list[i]+ 1) + '302"]'
                        else:
                            xpath = '//*[@id="itmStakeInput20' + str(purchase_record_column_list[i] + 1) + '301"]'
                        #输入值
                        input = driver.find_element_by_xpath(xpath)
                        input.send_keys(money)
                    #提交

                    #提交完成后保存至model
            else:
                pass


    prob_data = LotteryMonth.objects.filter(lottery_date=current_date)
    # prob_data = LotteryMonth.objects.all()
    return render_to_response('test.html',{"prob_data":prob_data})