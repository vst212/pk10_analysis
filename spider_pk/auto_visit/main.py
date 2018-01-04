# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.shortcuts import render_to_response
from auto_visit.models import ProbUser
from auto_visit.thread import ThreadControl
# Create your views here.

def pk10_view(request):
    thread_status = False
    info_active = True
    th_name = "test"
    thread_list =  ProbUser.objects.get(thread_name=th_name)
    for thread in thread_list:
        c  = ThreadControl()
        try:
            #查看是否处于活跃状态
            status = c.is_alive(thread.thread_name)
            if status:
                #设置状态为1
                thread.thread_status = 1
                thread.save()
            else:
                #设置状态为0
                thread.thread_status = 0
                thread.save()
        except:
            thread.thread_status = 0
            thread.save()
    # return render_to_response('qzone_info.html',{"info_active":info_active , "thread_list":thread_list})


def control_qzone_info_thread(request):
    # th_name = request.POST['id']
    # control = request.POST['control']

    user_name = "test"
    control = "start"
    print "thread_name is ",user_name
    #显示活跃状态
    info_active = True
    thread = ProbUser.objects.get(user_name=user_name)
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
        thread.user_status = 1
        thread.save()
    if control == 'stop':
        # thread1_status = False
        # status = 0
        c  = ThreadControl()
        try:
            c.stop(user_name)
            thread.user_status = 0
            thread.save()
        except:
            print "not thread alive"
    return render_to_response('test.html',{"obj_pro":thread})
    # thread_list = ProbUser.objects.filter(thread_ip=IP)
    # return render_to_response('qzone_info.html',{"thread_name":th_name, "control":control, "thread_list":thread_list,"info_active":info_active})

def auto_admin(request):
    # ProbTotals.objects.all().delete()
    thread_status = False
    info_active = True
    # thread_list =  ProbUser.objects.get(thread_name=th_name)
    thread_list =  ProbUser.objects.all()
    for thread in thread_list:
        c  = ThreadControl()
        try:
            #查看是否处于活跃状态
            status = c.is_alive(thread.thread_name)
            if status:
                #设置状态为1
                thread.user_status = 1
                thread.save()
            else:
                #设置状态为0
                thread.user_status = 0
                thread.save()
        except:
            print thread.user_name, " not start"
            thread.user_status = 0
            thread.save()
    return render_to_response('test.html',{"obj_pro":thread_list})

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
    obj_pro = ProbUser.objects.all()
    print "obj_pro",obj_pro
    for pro in obj_pro:
        print pro.user_name
    return render_to_response('test.html',{"obj_pro":obj_pro})