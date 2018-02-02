#coding=utf-8
__author__ = 'shifeixiang'

from django.views.decorators.csrf import csrf_exempt    #用于处理post请求出现的错误
from django.shortcuts import render_to_response
import time
from predict.models import KillPredict,KillPredictTotal

def predict_report(request):
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    obj_pro_predict = KillPredict.objects.filter(kill_predict_date=current_date)
    print "obj_pro",obj_pro_predict
    return render_to_response('predict_list.html',{"obj_pro_predict":obj_pro_predict})

def control_predict_report(request):
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