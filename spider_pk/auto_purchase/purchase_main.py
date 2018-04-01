# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt    #用于处理post请求出现的错误

from django.shortcuts import render
from django.shortcuts import render_to_response
import time
from predict.models import ProbUser
from auto_purchase.thread  import ThreadControl
from auto_purchase.purchase_driver import get_driver
from predict.predict_driver_extent_purchase_number import spider_predict_selenium

class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

class SingleDriver(Singleton):
    # def __init__(self, driver):
    #   self.driver = driver
    def get_driver(self):
        return self.driver
    def set_driver(self, driver):
        self.driver = driver

class SingleDriverMultiple(Singleton):
    # def __init__(self, driver):
    #   self.driver = driver
    def get_driver(self):
        return self.driver
    def set_driver(self, driver):
        self.driver = driver


@csrf_exempt   #处理Post请求出错的情况
def control_probuser_thread(request):
    user_name = request.POST['user_name']
    password = ProbUser.objects.get(user_name=user_name).user_password;
    control = request.POST['control']

    money = request.POST['auto_in_money']
    in_rule_list = request.POST['in_rule_list'].split(",")
    in_upper_money_list = []
    in_lower_money_list = []
    for in_rule in in_rule_list:
        print "in_rule:",in_rule
        in_upper_money_list.append(request.POST['in_upper_monery_'+str(in_rule)])
        in_lower_money_list.append(request.POST['in_lower_monery_'+str(in_rule)])
    info_dict = {}
    info_dict["user_name"] = user_name
    info_dict["money"] = int(money)
    info_dict["rule_list"] = in_rule_list
    info_dict["upper_money_list"] = in_upper_money_list
    info_dict["lower_money_list"] = in_lower_money_list

    #显示活跃状态
    prob_user = ProbUser.objects.get(user_name=user_name)
    if control == 'start':

        #杀号的driver
        driver = spider_predict_selenium()
        info_dict["driver"] = driver

        #购买driver
        #单例模式
        try:
            web_driver = SingleDriver()
            driver = web_driver.get_driver()
            info_dict["purchase_driver"] = driver
        except:
            web_driver = SingleDriver()
            driver = get_driver(user_name,password)
            web_driver.set_driver(driver)
            info_dict["purchase_driver"] = driver
        #状态信息
        c  = ThreadControl()
        #出现错误，则线程不存在，因此启动线程
        try:
            status = c.is_alive(user_name)
            print "thread is alive? ",status
            if status:
                print "thread is alive,caonot start twice!"
            else:
                print "start ..........thread1"
                c.start(user_name, info_dict)
        except:
            print "thread is not alive start!!!"
            c.start(user_name, info_dict)
        prob_user.user_status = 1
        prob_user.save()
    if control == 'stop':
        c  = ThreadControl()
        try :
            c.stop(user_name)
            prob_user.user_status = 0
            prob_user.save()
        except:
            print "not thread alive"
    prob_user_list =  ProbUser.objects.all()
    return render_to_response('auto_purchase.html',{"prob_user_list":prob_user_list, "p_rule":request.POST['in_rule_list'], "p_monery":money,
                                                "p_upper_monery_1":request.POST['in_upper_monery_1'], "p_lower_monery_1":request.POST['in_lower_monery_1'],
                                                "p_upper_monery_2":request.POST['in_upper_monery_2'], "p_lower_monery_2":request.POST['in_lower_monery_2'],
                                                "p_upper_monery_3":request.POST['in_upper_monery_3'], "p_lower_monery_3":request.POST['in_lower_monery_3'],
                                                "p_upper_monery_4":request.POST['in_upper_monery_4'], "p_lower_monery_4":request.POST['in_lower_monery_4'],
                                                "p_upper_monery_5":request.POST['in_upper_monery_5'], "p_lower_monery_5":request.POST['in_lower_monery_5'],
                                                "p_upper_monery_6":request.POST['in_upper_monery_6'], "p_lower_monery_6":request.POST['in_lower_monery_6'],
                                                "p_upper_monery_7":request.POST['in_upper_monery_7'], "p_lower_monery_7":request.POST['in_lower_monery_7']})
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
    return render_to_response('auto_purchase.html',{"prob_user_list":prob_user_list})



from predict.spider_pk10 import get_html_result,load_lottery_predict, get_lottery_id_number
from predict.main import get_predict_model_value,calculate_percisoin
from predict.predict_driver_extent_purchase_number import get_purchase_list
from predict.models import KillPredict

def spider_save_predict(interval):
    #爬取当天结果,存入objects
    html_json = get_html_result()
    if html_json == '':
        pass
    else:
        load_lottery_predict(html_json)

        #获取models predict最新值
        lottery_id,kill_predict_number = get_predict_model_value()
        print "lottery_id",lottery_id
        if lottery_id == 0:
            print "no predict record in history"
        else:
            #获取该期的开奖号码
            lottery_num = get_lottery_id_number(lottery_id)
            print "lottery_num:",lottery_num
            if (lottery_num):
                #计算命中率并更新models
                #print "save lottery_number"
                calculate_percisoin(lottery_id, lottery_num, kill_predict_number)
            else:
                print "pay interface lottery id request faild"


        #爬取下一期predict
        driver = interval["driver"]
        predict_lottery_id,purchase_number_list,purchase_number_list_desc,predict_number_all_list_str = get_purchase_list(driver)
        if predict_lottery_id != 0:
            #更新models
            print "save:",predict_lottery_id,'  ',purchase_number_list
            current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
            p = KillPredict(kill_predict_date=current_date, lottery_id = int(predict_lottery_id), kill_predict_number = purchase_number_list,
                            kill_predict_number_desc=purchase_number_list_desc, predict_total=0, target_total=0, predict_accuracy=0,
                            predict_number_all=predict_number_all_list_str)
            p.save()