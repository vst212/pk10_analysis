# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

from django.views.decorators.csrf import csrf_exempt    #用于处理post请求出现的错误
from django.shortcuts import render_to_response

from predict.models import ProbUser
from auto_purchase.thread import ThreadControl
from auto_purchase.purchase_driver import get_driver
from auto_purchase.purchase_driver_rule import spider_predict_selenium

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
    rule_id = request.POST['in_rule']

    info_dict = {}
    info_dict["user_name"] = user_name
    info_dict["money"] = int(money)
    info_dict["rule_id"] = rule_id

    info_dict["upper_money"] = int(request.POST['in_upper_monery_1'])
    info_dict["lower_money"] = int(request.POST['in_lower_monery_1'])

    print "info_dict:",info_dict
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
    return render_to_response('purchase_main.html',{"prob_user_list":prob_user_list, "p_rule":request.POST['in_rule'], "p_monery":money,
                                                "p_upper_monery_1":request.POST['in_upper_monery_1'], "p_lower_monery_1":request.POST['in_lower_monery_1']})
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
    return render_to_response('purchase_main.html',{"prob_user_list":prob_user_list})



from predict.spider_pk10 import get_html_result,load_lottery_predict, get_lottery_id_number
from predict.main import get_predict_model_value
from auto_purchase.purchase_driver_rule import get_purchase_list
from predict.models import KillPredict


#抓取，保存，自动购买
def spider_save_predict_purchase(interval):
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
                calculate_percisoin(lottery_id, lottery_num, kill_predict_number, interval)
            else:
                print "pay interface lottery id request faild"
    get_predict_kill_and_save(interval)
    return 0

def get_predict_kill_and_save(interval):
    # 爬取下一期predict
    driver = interval["driver"]
    predict_lottery_id, purchase_number_list, purchase_number_list_desc, predict_number_all_list_str = get_purchase_list(interval)

    print "start purchase"
    # 购买
    start_purchase(purchase_number_list, interval)

    # 成功后存入库
    if predict_lottery_id != 0:
        # 更新models
        print "save:", predict_lottery_id, '  ', purchase_number_list
        print "predict_number_all_list_str:", predict_number_all_list_str
        current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        p = KillPredict(kill_predict_date=current_date, lottery_id=int(predict_lottery_id),
                        kill_predict_number=purchase_number_list,
                        kill_predict_number_desc=purchase_number_list_desc, predict_total=0, target_total=0,
                        predict_accuracy=0,
                        predict_number_all=predict_number_all_list_str)
        p.save()

#计算命中率，盈利
def calculate_percisoin(lottery_id, lottery_num, kill_predict_number, interval):
    #lottery_num 转数组，kill_predict_number 转二位数组
    result_data = lottery_num.split(',')

    purchase_number_list = []
    for elet in kill_predict_number.split(','):
        tmp_list = elet.split('|')
        purchase_number_list.append(tmp_list)

    if len(result_data) == len(purchase_number_list):
        all_count = 0
        target_count = 0
        for i in range(len(result_data)):
            if  '0' in purchase_number_list[i]:
                print "predict invalid!"
            else:
                print " result_data[i],purchase_number_list[i]:", str(int(result_data[i])),purchase_number_list[i]
                if str(int(result_data[i])) in purchase_number_list[i]:
                    target_count = target_count +  1
                all_count = all_count + len(purchase_number_list[i])
        print "all_count,target_count:", all_count,target_count
        if all_count == 0:
            predict_accuracy = 0
        else:
            predict_accuracy = float(float(target_count)/float(all_count))
            print float(float(target_count)/float(all_count))
        try:
            p = KillPredict.objects.get(lottery_id=lottery_id)
            p.lottery_number = lottery_num
            p.predict_total = all_count
            p.target_total = target_count
            p.predict_accuracy = predict_accuracy
            p.xiazhu_money = interval['money']
            p.gain_money = target_count * 9.7 - all_count
            p.save()
        except:
            print "the ",lottery_id," is repeat!!!"
    else:
        print 'length error'


#购买
def start_purchase(purchase_number_list, interval):
    #计算历史总盈利
    gain_all_money = 0
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    sum_objects_predict = KillPredict.objects.filter(kill_predict_date = current_date)
    for gain in sum_objects_predict:
        if (gain.gain_money):
            gain_all_money = gain_all_money + gain.gain_money
        else:
            print "gain_money  is null"
            pass
    print gain_all_money
    print interval['upper_money'],interval['lower_money']
    #开始购买
    if gain_all_money < interval['upper_money'] and gain_all_money > interval['lower_money']:
        # purchase_driver = interval['purchase_driver']
        # purchase_driver = reload_pk10_driver(interval,purchase_driver)

        interval['purchase_driver'] = reload_pk10_driver(interval['purchase_driver'])

        purchase_driver = interval['purchase_driver']
        #切换到子框架
        print "exchange frame!"
        purchase_driver.switch_to_frame("frame")
        time.sleep(2)

        #遍历填充值
        print "start fill"

        purchase_element_list = get_xiazhu_message(purchase_number_list)
        for purchase_element in purchase_element_list:
            print "purchase_element:",purchase_element
            sub_element = purchase_driver.find_element_by_xpath(purchase_element)
            sub_element.send_keys(interval['money'])
            #time.sleep(1)
        confirm_button = purchase_driver.find_element_by_xpath('//*[@id="header"]/div[2]/div/input[1]')
        confirm_button.click()
        time.sleep(1)

        #返回原始框架
        print "return back"
        purchase_driver.switch_to_default_content()
        time.sleep(1)

        submit_button = purchase_driver.find_element_by_xpath('/html/body/div[6]/div[3]/div/button[1]/span')
        submit_button.click()

    return 0

#根据预测list转换成要购买的元素
def get_xiazhu_message(purchase_number_str):
    buy_element_list = []
    # purchase_number_str = '0,9|2|4|7,9|2|10|6,3|4|5|6|7|9,8|1|2|10,1|2|5|7|8|9,1|3|6|8|9|10'
    purchase_number_list = purchase_number_str.split(',')
    for index in range(len(purchase_number_list)):
        if purchase_number_list[index] == '0':
            pass
        else:
            purchase_numbers = purchase_number_list[index].split('|')
            for purchase_number in purchase_numbers:
                buy_element_list.append('//*[@id="a_B' + str(index+1) + '_' + str(purchase_number) + '"]/input')
    print buy_element_list
    return buy_element_list

#根据预测list转换成要购买的元素的对立元素
def get_xiazhu_message_trans(purchase_number_str):
    buy_element_list = []
    # purchase_number_str = '0,9|2|4|7,9|2|10|6,3|4|5|6|7|9,8|1|2|10,1|2|5|7|8|9,1|3|6|8|9|10'
    base_set = set(['1','2','3','4','5','6','7','8','9','10'])
    # print base_set
    purchase_number_list = purchase_number_str.split(',')
    for index in range(len(purchase_number_list)):
        if purchase_number_list[index] == '0':
            pass
        else:
            purchase_numbers = purchase_number_list[index].split('|')
            purchase_numbers_set = set(purchase_numbers)
            # print "base",base_set
            # print "purchase",purchase_numbers_set
            trans_purchase_numbers =  list(base_set - purchase_numbers_set)
            for purchase_number in trans_purchase_numbers:
                buy_element_list.append('//*[@id="a_B' + str(index+1) + '_' + str(purchase_number) + '"]/input')
    print buy_element_list
    return buy_element_list


def reload_pk10_driver(purchase_driver):
    #purchase_driver = interval['purchase_driver']
    print "purchase_driver.current_url:",purchase_driver.current_url
    purchase_driver.get(purchase_driver.current_url)
    time.sleep(2)
    #点击广告
    purchase_driver.find_element_by_xpath('//*[@id="notice_button1"]/a').click()
    time.sleep(1)

    purchase_driver.find_element_by_xpath('//*[@id="notice_button2"]/a').click()
    time.sleep(1)



    pk10 = purchase_driver.find_element_by_xpath('//*[@id="l_BJPK10"]/span')
    pk10.click()
    time.sleep(1)

    # 1-10
    element_1_10 = purchase_driver.find_element_by_xpath('//*[@id="sub_BJPK10"]/a[2]')
    element_1_10.click()
    time.sleep(1)

    return purchase_driver


def set_user_data(request):
    #写入对象
    ProbUser.objects.all().delete()
    user_id = 1
    user_name = "yup98"
    user_password = "aaa123"
    user_status = False
    obj_pro = ProbUser(user_id=user_id, user_name=user_name, user_password=user_password, user_status=user_status)
    obj_pro.save()
    return render_to_response('test.html')


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