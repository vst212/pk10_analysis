#coding=utf-8
__author__ = 'shifeixiang'

from django.views.decorators.csrf import csrf_exempt    #用于处理post请求出现的错误
from django.shortcuts import render_to_response
import time
from predict.models import KillPredictTotal
from predict.models import KillPredict
from predict.models import PredictLottery
import datetime

def predict_report(request):
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    obj_pro_predict = KillPredict.objects.filter(kill_predict_date=current_date)
    print "obj_pro",obj_pro_predict
    return render_to_response('predict_list.html',{"obj_pro_predict":obj_pro_predict})

#旧版
def control_predict_report_old(request):
    in_date= request.POST['in_date']

    KillPredictTotal.objects.all().delete()
    obj_pro_predict = KillPredict.objects.filter(kill_predict_date=in_date)
    target_count = 0
    all_count = 0
    count_count = 0
    for sub_predict in obj_pro_predict:

        predict_num_list_all = sub_predict.kill_predict_number.split(',')
        predict_num_list = []
        for elet in predict_num_list_all:
            tmp_list = elet.split('|')
            predict_num_list.append(tmp_list)

        lottery_num_list = sub_predict.lottery_number.split(',')

        if len(predict_num_list) == len(lottery_num_list):
            for i in range(len(lottery_num_list)):
                if  '0' in predict_num_list[i]:
                    pass
                    # print "predict invalid!"
                else:
                    # print " result_data[i],purchase_number_list[i]:", str(int(lottery_num_list[i])),predict_num_list[i]
                    if str(int(lottery_num_list[i])) in predict_num_list[i]:
                        target_count = target_count +  1
                    all_count = all_count + len(predict_num_list[i])
                    # print "all_count,target_count:", all_count,target_count
        # count_count = count_count + 1
        # if count_count == 2:
        #     break
    if all_count > 0:
        p = KillPredictTotal(kill_predict_date=in_date, predict_total=all_count, target_total=target_count, predict_accuracy=float(float(target_count)/float(all_count)))
        p.save()
    obj_pro_predict_total = KillPredictTotal.objects.all()

    return render_to_response('predict_list.html',{"obj_pro_predict":obj_pro_predict, "obj_pro_predict_total":obj_pro_predict_total,  "p_date":in_date})


from predict.spider_pk10 import get_html_result,get_lottery_id_number,load_lottery_predict
from predict.main import calculate_percisoin

#更新，处理lottery_number为空的情况
def control_predict_report(request):
    try:
        in_date= request.POST['in_date']
    except:
        in_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))

    KillPredictTotal.objects.all().delete()
    obj_pro_predict = KillPredict.objects.filter(kill_predict_date=in_date)
    target_count = 0
    all_count = 0
    #检查是否有lottery_num为空的情况
    all_record_count = len(obj_pro_predict)
    record_index = 0
    for sub_predict in obj_pro_predict:
        lottery_id = sub_predict.lottery_id
        lottery_number = sub_predict.lottery_number
        kill_predict_number = sub_predict.kill_predict_number
        # print "lottery_number:",type(sub_predict.lottery_number)
        if lottery_number == '' and record_index < (all_record_count-1):
            print "no lottery_num"
            html_json = get_html_result()
            if html_json == '':
                pass
            else:
                load_lottery_predict(html_json)
                print "lottery_id",lottery_id
                if lottery_id == 0:
                    print "no predict record in history"
                else:
                    #获取该期的开奖号码
                    lottery_num, lottery_time = get_lottery_id_number(lottery_id)
                    print "lottery_num:",lottery_num
                    if (lottery_num):
                        #计算命中率并更新models
                        calculate_percisoin(lottery_id, lottery_num, kill_predict_number, lottery_time)
                    else:
                        print "pay interface lottery id request faild"

        record_index = record_index + 1

    #遍历所有当天对象
    obj_pro_predict = KillPredict.objects.filter(kill_predict_date=in_date)
    base_hour = 8
    every_hour_all_total = 0
    every_hour_target_total = 0
    for sub_predict in obj_pro_predict:


        predict_num_list_all = sub_predict.kill_predict_number.split(',')
        predict_num_list = []
        for elet in predict_num_list_all:
            tmp_list = elet.split('|')
            predict_num_list.append(tmp_list)

        lottery_num_list = sub_predict.lottery_number.split(',')
        print "lottery_num_list:",lottery_num_list

        #最后一行不做统计
        if len(predict_num_list) == len(lottery_num_list):

            current_kill_predict_time = sub_predict.kill_predict_time
            # print "current_kill_predict_time:", current_kill_predict_time
            try:
                date_time = datetime.datetime.strptime(current_kill_predict_time,'%Y-%m-%d %H:%M:%S')
                # print "date_time:", date_time
                current_hour = date_time.hour
                # print "current_hour:", current_hour
            except:
                current_hour = 9
                print "no time"


            for i in range(len(lottery_num_list)):
                if  '0' in predict_num_list[i]:
                    pass
                else:
                    # print " result_data[i],purchase_number_list[i]:", str(int(lottery_num_list[i])),predict_num_list[i]
                    if str(int(lottery_num_list[i])) in predict_num_list[i]:
                        target_count = target_count +  1
                    all_count = all_count + len(predict_num_list[i])

                    if (current_hour-base_hour) > 1:
                        print "current_kill_predict_time:",current_kill_predict_time
                        print "every_hour_all_total:",every_hour_all_total
                        print "every_hour_target_total:",every_hour_target_total
                        p = KillPredictTotal(kill_predict_date=in_date, predict_total=every_hour_all_total, target_total=every_hour_target_total,
                                             predict_accuracy=float(float(every_hour_target_total)/float(every_hour_all_total)), predict_column_desc=int(current_hour)-1)
                        p.save()

                        every_hour_all_total = 0
                        every_hour_target_total = 0
                        base_hour = current_hour - 1
                        if str(int(lottery_num_list[i])) in predict_num_list[i]:
                            every_hour_target_total = every_hour_target_total + 1
                        every_hour_all_total = every_hour_all_total + len(predict_num_list[i])
                    else:
                        if str(int(lottery_num_list[i])) in predict_num_list[i]:
                            every_hour_target_total = every_hour_target_total + 1
                        every_hour_all_total = every_hour_all_total + len(predict_num_list[i])

    p = KillPredictTotal(kill_predict_date=in_date, predict_total=every_hour_all_total, target_total=every_hour_target_total,
                                             predict_accuracy=float(float(every_hour_target_total)/float(every_hour_all_total)), predict_column_desc=int(base_hour)+1)
    p.save()
    print "current_kill_predict_time:",current_kill_predict_time
    print "every_hour_all_total:",every_hour_all_total
    print "every_hour_target_total:",every_hour_target_total

                    # print "all_count,target_count:", all_count,target_count
        # count_count = count_count + 1
        # if count_count == 2:
        #     break
    if all_count > 0:
        p = KillPredictTotal(kill_predict_date=in_date, predict_total=all_count, target_total=target_count, predict_accuracy=float(float(target_count)/float(all_count)), predict_column_desc='总数')
        p.save()
    obj_pro_predict_total = KillPredictTotal.objects.all()

    return render_to_response('predict_list.html',{"obj_pro_predict":obj_pro_predict, "obj_pro_predict_total":obj_pro_predict_total,  "p_date":in_date})


def get_lottery_msg(request):
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    obj_pro_predict = PredictLottery.objects.filter(lottery_date=current_date)
    print "obj_pro",obj_pro_predict
    return render_to_response('test.html',{"obj_pro_predict":obj_pro_predict})


def get_kill_predict_msg(request):
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    obj_pro_kill_predict = KillPredict.objects.filter(kill_predict_date=current_date)
    print "obj_pro_kill_predict",obj_pro_kill_predict
    return render_to_response('test.html',{"obj_pro_kill_predict":obj_pro_kill_predict})