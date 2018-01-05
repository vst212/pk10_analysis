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
from auto_visit.pretreatment import get_rule, parase_lotterys
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

def get_user_data(request):
    rule = 1
    money = 10
    upper_money = 30
    spider_current_date_data()
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    lotterys = LotteryMonth.objects.filter(lottery_date=current_date)
    if(rule < 5):
        rule_parity_list = get_rule(rule)
        base_lottery_list,parity_lottery_list,larsma_lottery_list = parase_lotterys(lotterys)
        


    obj_pro = ProbUser.objects.all()
    print "obj_pro",obj_pro
    for pro in obj_pro:
        print pro.user_name
    return render_to_response('test.html',{"obj_pro":obj_pro})

def get_prob_data(request):
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))

    prob_data = LotteryMonth.objects.filter(lottery_date=current_date)
    # prob_data = LotteryMonth.objects.all()
    return render_to_response('test.html',{"prob_data":prob_data})