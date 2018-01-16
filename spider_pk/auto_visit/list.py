# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_exempt    #用于处理post请求出现的错误
from django.shortcuts import render
from django.shortcuts import render_to_response
from auto_visit.models import FianceRecord, FianceRecordTotal

from auto_visit.models import ProbUser
# Create your views here.
import time
def auto_list(request):
    # ProbTotals.objects.all().delete()

    current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    obj_pro_fiance = FianceRecord.objects.filter(fiance_record_date=current_date)

    return render_to_response('auto_list.html',{"probs":obj_pro_fiance})

def auto_list_refresh(request):
    # ProbTotals.objects.all().delete()

    rule = request.POST['in_rule']
    in_date= request.POST['in_date']
    print in_date," ",rule

    current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    obj_pro_fiance = FianceRecord.objects.filter(fiance_record_date=in_date, fiance_record_rule_id=rule)
    fiance_record_profit_all = 0
    column_total =  [0]*10
    for fiance in obj_pro_fiance:
        for i in range(10):
            column = i + 1
            if fiance.purchase_record_column == '第' + str(column) + '名':
                column_total[i] = column_total[i] + fiance.fiance_record_profit
                print fiance.purchase_record_column
    FianceRecordTotal.objects.all().delete()
    for i in range(10):
        obj_pros = FianceRecordTotal(fiance_record_id=1,fiance_record_date = in_date, fiance_record_rule_id=rule, fiance_record_value=1,fiance_record_money=1,fiance_record_odds=1,fiance_lose_win=1,
                                                     fiance_record_column='第' + str(i+1) + '名',
                                                     fiance_record_profit_all=column_total[i])
        obj_pros.save()
    print column_total

    obj_pro_fiance_total = FianceRecordTotal.objects.filter(fiance_record_date=in_date, fiance_record_rule_id = rule )
    return render_to_response('auto_list.html',{"probs":obj_pro_fiance, "obj_pro_fiance_total":obj_pro_fiance_total,  "p_date":in_date, "p_rule":rule})

@csrf_exempt
def set_user(request):

    try:
        user_name = request.POST['in_user']
        user_password = request.POST['in_pwd']
        control = request.POST['control']
        user_id = len(ProbUser.objects.all()) + 1
        user_status = False
        if(control == 'add'):
            obj_pro = ProbUser(user_id=user_id, user_name=user_name, user_password=user_password, user_status=user_status)
            obj_pro.save()
        if(control == 'delete'):
            ProbUser.objects.filter(user_name=user_name).delete()
        obj_pro = ProbUser.objects.all()
    except:
        obj_pro = ProbUser.objects.all()
        return render_to_response('set_user.html', {"obj_pro":obj_pro})

    return render_to_response('set_user.html', {"obj_pro":obj_pro})

