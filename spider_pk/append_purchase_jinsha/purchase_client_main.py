# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

from django.views.decorators.csrf import csrf_exempt    #用于处理post请求出现的错误
from django.shortcuts import render_to_response

from append_predict.models import ProbUser
from append_purchase_jinsha.client_thread  import ThreadControl
from append_purchase_jinsha.purchase_driver import get_driver

from append_predict.models import KillPredict
import datetime

import json
import urllib2

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pkten_log.pk_log import PkLog
pk_logger = PkLog('append_purchase_jinsha.purchase_client_main').log()

class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

class SingleDriver(Singleton):
    def get_driver(self):
        return self.driver
    def set_driver(self, driver):
        self.driver = driver

class SingleDriverMultiple(Singleton):
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
    info_dict["rule_id"] = int(rule_id)

    info_dict["upper_money"] = int(request.POST['in_upper_monery_1'])
    info_dict["lower_money"] = int(request.POST['in_lower_monery_1'])

    pk_logger.info("money:%s",info_dict["money"])
    #显示活跃状态
    prob_user = ProbUser.objects.get(user_name=user_name)
    if control == 'start':
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
            pk_logger.warn("thread is alive?:%s",status)
            if status:
                pk_logger.warn("thread is alive,caonot start twice!")
            else:
                pk_logger.warn("start ..........thread1")
                c.start(user_name, info_dict)
        except:
            pk_logger.warn("thread is not alive start!!!")
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
            pk_logger.warn("not thread alive")
    prob_user_list =  ProbUser.objects.all()
    return render_to_response('append_purchase_jinsha_main.html',{"prob_user_list":prob_user_list, "p_rule":request.POST['in_rule'], "p_monery":money,
                                                "p_upper_monery_1":request.POST['in_upper_monery_1'], "p_lower_monery_1":request.POST['in_lower_monery_1']})
    # return render_to_response('qzone_info.html',{"thread_name":th_name, "control":control, "thread_list":thread_list,"info_active":info_active})

#主页面
def auto_admin(request):
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
            pk_logger.info("%s not start",prob_user.user_name)
            prob_user.user_status = 0
            prob_user.save()
    return render_to_response('append_purchase_jinsha_main.html',{"prob_user_list":prob_user_list})


#自动购买
def get_predict_kill_and_save(interval):
    #购买流程
    purchase_flag_confirm = True
    while(purchase_flag_confirm):
        purchase_flag_minute = int(time.strftime("%M", time.localtime())) % 10
        purchase_flag_second = int(time.strftime("%S", time.localtime()))
        #pk_logger.info("current time:%s,%s",purchase_flag_minute,purchase_flag_second)
        if (purchase_flag_minute > 3 and purchase_flag_minute < 6) or (purchase_flag_minute == 6 and purchase_flag_second < 30) or (purchase_flag_minute > 8) or (purchase_flag_minute == 0) or (purchase_flag_minute == 1 and purchase_flag_second < 30):
            pk_logger.info("request server interface!")
            result_info = get_server_request_info()
            if 1:
                #判断是否获取接口数据正确
                if result_info:
                    last_id = int(result_info['last_lottery_id'])
                    predict_id = int(result_info['predict_lottery_id'])
                    #判断是否成功拿到predict
                    if predict_id > last_id:
                        #判断是否是最新一期
                        save_predict_time = datetime.datetime.strptime(result_info['save_predict_time'],'%Y-%m-%d %H:%M:%S')
                        current_time = datetime.datetime.now()
                        if (current_time - save_predict_time).seconds > 180:
                            pk_logger.info("unfounded new predict,purchase faild!")
                            purchase_flag_confirm = False
                        else:
                            purchase_number_list = result_info['predict_number_list']
                            money = result_info['xiazhu_money'] * interval['money']
                            pk_logger.info("start purchase, 下注金额:%s",money)

                            #获取购买元素列表个数
                            purchase_element_list = get_xiazhu_message_jinsha(purchase_number_list)
                            if len(purchase_element_list) > 0:
                                # 购买
                                purchase_result = start_purchase(purchase_element_list, interval, money)
                                input_money = len(purchase_element_list) * money
                                if purchase_result:
                                    pk_logger.info("purchase sucess!, input money:%s",input_money)
                                    p = KillPredict.objects.get(lottery_id=predict_id)
                                    p.is_xiazhu = 1
                                    p.input_money = input_money
                                    p.save()
                                    pk_logger.info("save xiazhu args sucess!")
                                else:
                                    pk_logger.info("purchase faild!")
                            else:
                                pk_logger.info("no element in purchase_element_list")
                        purchase_flag_confirm = False
                    else:
                        pk_logger.info("wait time until shahao message save ok")
                else:
                    pk_logger.info("get server interface error!")
                time.sleep(5)
        else:
            time.sleep(20)
            pk_logger.info("purchase time is no region!")

#计算命中率，盈利
def calculate_percisoin(lottery_id, lottery_num, kill_predict_number, purchase_number_list_desc, interval):
    #lottery_num 转数组，kill_predict_number 转二位数组
    result_data = lottery_num.split(',')
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))

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
        if 1:
            lottery_number = lottery_num
            predict_total = all_count
            target_total = target_count
            predict_accuracy = predict_accuracy
            xiazhu_money = interval['money']
            gain_money = (target_count * 9.7 - all_count) * int(xiazhu_money)

            p = KillPredict(kill_predict_date=current_date, lottery_id = lottery_id, lottery_number = lottery_number, kill_predict_number = kill_predict_number,
                            kill_predict_number_desc=purchase_number_list_desc, predict_total=predict_total, target_total=target_total, predict_accuracy=predict_accuracy,
                            xiazhu_money=xiazhu_money, gain_money = gain_money)
            p.save()
        else:
            print "the ",lottery_id," is repeat!!!"
    else:
        print 'length error'


#购买 新金沙
def start_purchase(purchase_element_list, interval, money):
    #计算历史总盈利
    gain_all_money = 0
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    sum_objects_predict = KillPredict.objects.filter(kill_predict_date = current_date)
    for gain in sum_objects_predict:
        if (gain.gain_money):
            gain_all_money = gain_all_money + gain.gain_money
    pk_logger.info("calc gain_all_money:%d", gain_all_money)

    #开始购买
    if 1:
        interval['purchase_driver'] = reload_jinsha_pk10_url(interval['purchase_driver'])
        purchase_driver = interval['purchase_driver']

        if 1:
            #遍历填充值
            for purchase_element in purchase_element_list:
                pk_logger.info("start purchase purchase_element:%s",purchase_element)
                pk_logger.info("current xaizhu money:%d",int(money))
                sub_element = purchase_driver.find_element_by_xpath(purchase_element)
                sub_element.send_keys(money)
                time.sleep(1)

            #'li_chip_btn'
            time.sleep(1)
            js = "var q=document.documentElement.scrollTop=10000"
            purchase_driver.execute_script(js)
            time.sleep(1)
            confirm = purchase_driver.find_element_by_xpath('//*[@id="btn_order_confirm"]')
            confirm.click()
            time.sleep(1)
            # 提交按钮
            pk_logger.info("click submit")
            submit = purchase_driver.find_element_by_xpath('//*[@id="order_ok"]')
            submit.click()

            return True
    else:
        return False


#根据预测list转换成要购买的元素
def get_xiazhu_message_jinsha(purchase_number_str):
    buy_element_list = []
    # purchase_number_str = '0,9|2|4|7,9|2|10|6,3|4|5|6|7|9,8|1|2|10,1|2|5|7|8|9,1|3|6|8|9|10'
    purchase_number_list = purchase_number_str.split(',')
    for index in range(len(purchase_number_list)):
        if purchase_number_list[index] == '0':
            pass
        else:
            purchase_numbers = purchase_number_list[index].split('|')
            for purchase_number in purchase_numbers:
                # 构造path
                column = str((index % 5) + 1)
                # 补全2位值
                value = str(int(purchase_number) + 1)

                xpath = '//*[@id="itmStakeInput2' + column + '1' + value + '"]'
                if index >= 5 :
                    xpath = '//*[@id="odds_body"]/div[2]/div[' + column + ']/ul/li[' + value + ']/div[3]/input'
                else:
                    xpath = '//*[@id="odds_body"]/div[1]/div[' + column + ']/ul/li[' + value + ']/div[3]/input'

                #1-1
                #'//*[@id="odds_body"]/div[1]/div[1]/ul/li[2]/div[3]/input'
                #1-6
                #'//*[@id="odds_body"]/div[1]/div[1]/ul/li[7]/div[3]/input'
                #1-10
                #'//*[@id="odds_body"]/div[1]/div[1]/ul/li[11]/div[3]/input'
                #2-1
                #'//*[@id="odds_body"]/div[1]/div[2]/ul/li[2]/div[3]/input'

                #6-1
                #'//*[@id="odds_body"]/div[2]/div[1]/ul/li[2]/div[3]/input'
                #6-8
                #'//*[@id="odds_body"]/div[2]/div[1]/ul/li[9]/div[3]/input'
                buy_element_list.append(xpath)
    return buy_element_list



def reload_jinsha_pk10_url(driver):
    #重新加载
    pk_logger.info("reload purchase_url:%s",driver.current_url)
    driver.get(driver.current_url)
    try:
        element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID , "odds_body")))
        pk_logger.info("purchase_url reload ok")
    except:
        pk_logger.error("purchase_url reload error timeout")
    time.sleep(5)
    return driver


def get_server_request_info():
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }
    url = 'http://127.0.0.1:8006/get_append_predict_data/'
    request_flag = True
    count = 0
    while(request_flag):
        try:
            req = urllib2.Request(url = url, headers = headers)
            page = urllib2.urlopen(req, timeout=10)
            html = page.read()
            result_info = html
            info_dict = json.loads(result_info)
            request_flag = False
            return info_dict
        except:
            pk_logger.error(" get server request info request server faild!")
            time.sleep(3)
            if count > 2:
                request_flag = False
            count = count + 1
    return {}

