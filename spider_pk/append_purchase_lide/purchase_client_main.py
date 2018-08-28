# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
import random

from django.views.decorators.csrf import csrf_exempt    #用于处理post请求出现的错误
from django.shortcuts import render_to_response

from append_predict.models import ProbUser
from append_purchase_lide.client_thread  import ThreadControl
from append_purchase_lide.purchase_driver import get_driver


from append_predict.spider_pk10 import get_html_result,load_lottery_predict, get_lottery_id_number
from append_predict.main import get_predict_model_value

from append_predict.models import KillPredict
import datetime

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pkten_log.pk_log import PkLog
pk_logger = PkLog('append_purchase_lide.purchase_client_main').log()

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
    #print "password:",password
    pk_logger.info("user_name:%s",user_name)
    pk_logger.info("password:%s",password)
    control = request.POST['control']

    money = request.POST['auto_in_money']
    rule_id = request.POST['in_rule']

    info_dict = {}
    info_dict["user_name"] = user_name
    info_dict["password"] = password
    info_dict["money"] = int(money)
    info_dict["rule_id"] = int(rule_id)

    info_dict["upper_money"] = int(request.POST['in_upper_monery_1'])
    info_dict["lower_money"] = int(request.POST['in_lower_monery_1'])

    #print "info_dict:",info_dict,
    #print "money:",info_dict["money"]
    pk_logger.info("init monry:%s",info_dict["money"])
    #显示活跃状态
    prob_user = ProbUser.objects.get(user_name=user_name)
    if control == 'start':

        #杀号的driver
        #driver = spider_predict_selenium()
        #info_dict["driver"] = driver

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
            #print "thread is alive? ",status
            pk_logger.warn("thread is alive?:%s",status)
            if status:
                #print "thread is alive,caonot start twice!"
                pk_logger.warn("thread is alive,caonot start twice!")
            else:
                #print "start ..........thread1"
                pk_logger.warn("start ..........thread1")
                c.start(user_name, info_dict)
        except:
            #print "thread is not alive start!!!"
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
            #print "not thread alive"
            pk_logger.warn("not thread alive")
    prob_user_list =  ProbUser.objects.all()
    return render_to_response('append_purchase_lide_main.html',{"prob_user_list":prob_user_list, "p_rule":request.POST['in_rule'], "p_monery":money,
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
            pk_logger.info("%s not start",prob_user.user_name)
            #print prob_user.user_name, " not start"
            prob_user.user_status = 0
            prob_user.save()
    return render_to_response('append_purchase_lide_main.html',{"prob_user_list":prob_user_list})


def get_predict_kill_and_save(interval):
    #购买流程
    purchase_flag_confirm = True
    while(purchase_flag_confirm):
        purchase_flag_minute = int(time.strftime("%M", time.localtime())) % 10
        purchase_flag_second = int(time.strftime("%S", time.localtime()))
        #print "minute:",purchase_flag_minute, "second:",purchase_flag_second
        #pk_logger.info("current time:%s,%s",purchase_flag_minute,purchase_flag_second)
        if (purchase_flag_minute > 3 and purchase_flag_minute < 5) or (purchase_flag_minute == 5 and purchase_flag_second < 40) or (purchase_flag_minute > 8) or (purchase_flag_minute == 0 and purchase_flag_second < 40):
            #print "request server interface!"
            #pk_logger.info("request server interface!")
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
                            pk_logger.info("start purchase, xiazhu money:%s",money)
                            #获取购买元素列表个数
                            purchase_element_list = get_xiazhu_message_lide(purchase_number_list)
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
                                    #print "purchase faild!"
                                    pk_logger.info("purchase faild!")
                            else:
                                #print 'no element in purchase_element_list '
                                pk_logger.info("no element in purchase_element_list")
                        purchase_flag_confirm = False
                    else:
                        pass
                        #pk_logger.info("wait time until shahao message save ok")
                else:
                    #print "get server interface error!"
                    pk_logger.info("get server interface error!")
                time.sleep(5)
        else:
            time.sleep(15)
            #print "purchase time is no region!"
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


#购买
def start_purchase(purchase_element_list, interval, money):
    #计算历史总盈利
    gain_all_money = 0
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    sum_objects_predict = KillPredict.objects.filter(kill_predict_date = current_date)
    for gain in sum_objects_predict:
        if (gain.gain_money):
            gain_all_money = gain_all_money + gain.gain_money
    #print "gain_all_money:",gain_all_money
    pk_logger.info("calc gain_all_money:%d", gain_all_money)
    #开始购买
    if 1:

        interval['purchase_driver'] = reload_pk10_driver(interval['purchase_driver'], interval)
        purchase_driver = interval['purchase_driver']
        #print "exchange frame!"
        #purchase_driver.switch_to_frame("frame")
        time.sleep(3)
        try:
            gain_all_money = int(purchase_driver.find_element_by_class_name('lottery_info_left').find_element_by_id('bresult').text.replace(',',''))
            pk_logger.info("web get gain_all_money:%s",gain_all_money)
        except:
            #print "get gain_all_money error!"
            pk_logger.error("web get gain_all_money error!")
        #print "gain_all_money:", gain_all_money

        if 1:
            for purchase_element in purchase_element_list:
                #print "purchase_element:",purchase_element
                #print "current xaizhu money",int(money)
                pk_logger.info("start purchase purchase_element:%s",purchase_element)
                pk_logger.info("current xaizhu money:%d",int(money))
                sub_element = purchase_driver.find_element_by_xpath(purchase_element)
                #追加下注
                sub_element.send_keys(str(int(money)))
                #下注一元
                #sub_element.send_keys(str(1))
                time.sleep(random.randint(1,3))
            #提交按钮
            confirm_button = purchase_driver.find_element_by_xpath('//*[@id="gameSubmit"]')
            confirm_button.click()
            time.sleep(2)
            pk_logger.info("commit ok")

            #返回原始框架
            #print "return back"
            #purchase_driver.switch_to_default_content()
            #time.sleep(1)

            #弹窗 确认按钮
            # confirm_elements = purchase_driver.find_elements_by_class_name('myLayerFooter')
            # confirm_count = 0
            # for confirm_element in confirm_elements:
            #     pk_logger.info("confirm_element :%d",confirm_count)
            #     if confirm_count == 1:
            #         confirm_element.find_element_by_link_text(u'提交')
            #     confirm_count = confirm_count + 1

            submit_button =  purchase_driver.find_element_by_class_name('myLayerOk')
            #submit_button = purchase_driver.find_element_by_xpath('//*[@id="myLayer_1"]/tbody/tr/td/div[3]/a[2]')
            submit_button.click()
            time.sleep(2)
            #print "ok"
            pk_logger.info("purchase ok")

            # time.sleep(3)
            # purchase_driver.quit()
            # pk_logger.info("login exit ok")
            #print "current url:",purchase_driver.current_url
            #pk_logger.info("current url:%s",purchase_driver.current_url)
            return True
        else:
            #print "purchase driver error element not found !!!"
            pk_logger.error("purchase driver error element not found !!!")
            return False
    else:
        pk_logger.error("reload pk10 error !!!")
        return False


#根据预测list转换成要购买的元素
def get_xiazhu_message_lide(purchase_number_str):
    buy_element_list = []
    # purchase_number_str = '0,9|2|4|7,9|2|10|6,3|4|5|6|7|9,8|1|2|10,1|2|5|7|8|9,1|3|6|8|9|10'
    purchase_number_list = purchase_number_str.split(',')
    for index in range(len(purchase_number_list)):
        if purchase_number_list[index] == '0':
            pass
        else:
            pk_logger.info("purchase mingci:%d",index+1)
            purchase_numbers = purchase_number_list[index].split('|')
            for purchase_number in purchase_numbers:
                pk_logger.info("purchase number:%s",purchase_number)
                #奇特的编号
                if index >= 5:
                    column = str((index+2) * 3)
                else:
                    column = str(index * 4 + 1)
                # 补全2位值
                if index >= 6:
                    value = str(16 * index  - (index - 5) * 2 + int(purchase_number))
                else:
                    value = str(16 * index + int(purchase_number))
                #xpath = '//*[@id="itmStakeInput2' + column + '1' + value + '"]'
                xpath = '//*[@id="inw_' + str(column) +'_' + str(value) + '"]/input'
                #print "xpath:",xpath
                buy_element_list.append(xpath)
                #buy_element_list.append('//*[@id="a_B' + str(index+1) + '_' + str(purchase_number) + '"]/input')
    return buy_element_list



def restart_pk10_driver(purchase_driver,interval):

    if 1:
        purchase_driver = get_driver(interval['user_name'],interval['password'])
        try:
            element = WebDriverWait(purchase_driver, 15).until(EC.presence_of_element_located((By.ID , "inw_1_1")))
            pk_logger.info("click 1-10 ok")
        except:
            pk_logger.error("click 1-10 error,wait 5s")
            time.sleep(5)
            restart_pk10_driver(purchase_driver, interval)
    else:
        pk_logger.error("reload pk10 error,exit")
        time.sleep(2)
        purchase_driver.quit()
        pk_logger.error("reload pk10 error,restart")
        time.sleep(5)
        #'http://mem4.bbafon311.lbjthg.com/Index.aspx'
        #'http://mem4.bbafon311.lbjthg.com/'
        purchase_driver = get_driver(interval['user_name'],interval['password'])
        reload_pk10_driver(purchase_driver, interval)

    return purchase_driver

def reload_pk10_driver(purchase_driver,interval):

    #10s的超时，超时做异常处理
    # purchase_driver.get(purchase_url)
    # try:
    #     element = WebDriverWait(purchase_driver, 15).until(EC.presence_of_element_located((By.ID , "menuText")))
    #     pk_logger.info("purchase_url reload ok")
    # except:
    #     pk_logger.error("purchase_url reload error timeout")
    # time.sleep(2)


    # purchase_driver.switch_to_default_content()
    # time.sleep(3)
    # pk_logger.info("return  default content!")
    #
    #
    # menu_element = purchase_driver.find_element_by_link_text(u'北京賽車(PK10)')
    # time.sleep(2)
    # pk_logger.info("click menu ok")
    # webdriver.ActionChains(purchase_driver).move_to_element(menu_element).perform()
    # time.sleep(2)
    # purchase_driver.find_element_by_link_text(u'北京賽車(PK10)').click()
    # time.sleep(2)
    # pk_logger.info("click pk10 ok")
    #
    # #切换frame
    # # 'mainIframe'
    try:
        purchase_driver.switch_to_default_content()
        time.sleep(2)
        purchase_driver.switch_to_frame("mainIframe")
        time.sleep(3)
        pk_logger.info("switch mainIFrame ok")
    except:
        pk_logger.info("current mainIFrame ok")
    #1-10
    try:
        #purchase_url = purchase_driver.current_url
        #pk_logger.info("purchase_url:%s",purchase_url)
        try:
            element_1_10 = purchase_driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[1]/div[1]/div/div[1]/ul/li[2]/a')
            element_1_10.click()
        except:
            pk_logger.warn("not found 1-10.")
        try:
            element = WebDriverWait(purchase_driver, 15).until(EC.presence_of_element_located((By.ID , "inw_1_1")))
            pk_logger.info("find inw_1_1 ok")
        except:
            pk_logger.error("find inw_1_1 error,exit")
            time.sleep(2)
            purchase_driver.quit()
            pk_logger.error("find inw_1_1 error,restart")
            time.sleep(2)
            purchase_driver = get_driver(interval['user_name'],interval['password'])
            reload_pk10_driver(purchase_driver, interval)
    except:
        pk_logger.error("reload pk10 error,exit")
        time.sleep(2)
        purchase_driver.quit()
        pk_logger.error("reload pk10 error,restart")
        time.sleep(2)
        #'http://mem4.bbafon311.lbjthg.com/Index.aspx'
        #'http://mem4.bbafon311.lbjthg.com/'
        purchase_driver = get_driver(interval['user_name'],interval['password'])
        reload_pk10_driver(purchase_driver, interval)
        #interval['user_name'],interval['password']


    #pk_logger.info("click 1-10 ok")
    return purchase_driver

import json
from django.http import HttpResponse
import urllib2
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
            #print "request server faild!"
            pk_logger.error(" get server request info request server faild!")
            time.sleep(3)
            if count > 2:
                request_flag = False
            count = count + 1
    return {}


def get_lottery_msg(request):
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    obj_pro_predict = KillPredict.objects.filter(kill_predict_date=current_date)
    #print "obj_pro",obj_pro_predict
    return render_to_response('test.html',{"obj_pro_predict":obj_pro_predict})
