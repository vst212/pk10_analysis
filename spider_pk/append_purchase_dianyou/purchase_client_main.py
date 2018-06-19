# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

from django.views.decorators.csrf import csrf_exempt    #用于处理post请求出现的错误
from django.shortcuts import render_to_response

from append_predict.models import ProbUser
from append_purchase_dianyou.client_thread  import ThreadControl
from append_purchase_dianyou.purchase_driver import get_driver


from append_predict.spider_pk10 import get_html_result,load_lottery_predict, get_lottery_id_number
from append_predict.main import get_predict_model_value

from append_predict.models import KillPredict
import datetime

import json
import urllib2

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
    print "password:",password
    control = request.POST['control']

    money = request.POST['auto_in_money']
    rule_id = request.POST['in_rule']

    info_dict = {}
    info_dict["user_name"] = user_name
    info_dict["money"] = int(money)
    info_dict["rule_id"] = int(rule_id)

    info_dict["upper_money"] = int(request.POST['in_upper_monery_1'])
    info_dict["lower_money"] = int(request.POST['in_lower_monery_1'])

    print "info_dict:",info_dict,
    print "money:",info_dict["money"]
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
    return render_to_response('append_purchase_dianyou_main.html',{"prob_user_list":prob_user_list, "p_rule":request.POST['in_rule'], "p_monery":money,
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
            print prob_user.user_name, " not start"
            prob_user.user_status = 0
            prob_user.save()
    return render_to_response('append_purchase_dianyou_main.html',{"prob_user_list":prob_user_list})


#自动购买
def get_predict_kill_and_save(interval):
    #计算统计流程
    # save_gain_flag_confirm = True
    # while(save_gain_flag_confirm):
    #     purchase_flag_minute = int(time.strftime("%M", time.localtime())) % 10
    #     purchase_flag_second = int(time.strftime("%S", time.localtime()))
    #     print "minute:",purchase_flag_minute, "second:",purchase_flag_second
    #     if (purchase_flag_minute == 4) or (purchase_flag_minute == 3 and purchase_flag_second >= 15) or (purchase_flag_minute == 9) or (purchase_flag_minute == 8 and purchase_flag_second >= 15):
    #         print "request server interface!"
    #         result_info = get_server_request_info()
    #         if result_info:
    #             last_id = int(result_info['last_lottery_id'])
    #             predict_id = int(result_info['predict_lottery_id'])
    #             print "calc money is:",interval['money']
    #             money = result_info['xiazhu_money'] * interval['money']
    #             print "calc money is:", money
    #             if last_id == predict_id:
    #                 calculate_percisoin(last_id, result_info['lottery_number'], result_info['predict_number_list'], result_info['predict_number_list_desc'], interval)
    #                 save_gain_flag_confirm = False
    #             else:
    #                 print "wait time until spider pay interface ok"
    #         else:
    #             print "get server interface error for save gain!"
    #         time.sleep(5)
    #     else:
    #         print "save time is no region!"
    #         time.sleep(5)
    #     if (purchase_flag_minute == 4 and purchase_flag_second >= 30) or (purchase_flag_minute == 9 and purchase_flag_second >= 30):
    #         save_gain_flag_confirm = False
    #购买流程
    purchase_flag_confirm = True
    while(purchase_flag_confirm):
        purchase_flag_minute = int(time.strftime("%M", time.localtime())) % 10
        purchase_flag_second = int(time.strftime("%S", time.localtime()))
        print "minute:",purchase_flag_minute, "second:",purchase_flag_second
        if (purchase_flag_minute > 3 and purchase_flag_minute < 5) or (purchase_flag_minute == 5 and purchase_flag_second < 40) or (purchase_flag_minute > 8) or (purchase_flag_minute == 0 and purchase_flag_second < 40):
            print "request server interface!"
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
                            print "unfounded new predict"
                            print "purchase faild!"
                            purchase_flag_confirm = False
                        else:
                            purchase_number_list = result_info['predict_number_list']
                            money = result_info['xiazhu_money'] * interval['money']
                            print "start purchase"
                            print "xiazhu money:",money

                            #获取购买元素列表个数
                            purchase_element_list = get_xiazhu_message_dianyou(purchase_number_list)
                            if len(purchase_element_list) > 0:
                                # 购买
                                purchase_result = start_purchase(purchase_element_list, interval, money)
                                input_money = len(purchase_element_list) * money
                                if purchase_result:
                                    print "purchase sucess!"
                                    print "input_money:",input_money
                                    p = KillPredict.objects.get(lottery_id=predict_id)
                                    p.is_xiazhu = 1
                                    p.input_money = input_money
                                    p.save()
                                    print "save xiazhu sucess!"
                                else:
                                    print "purchase faild!"
                            else:
                                print 'no element in purchase_element_list '
                        purchase_flag_confirm = False
                    else:
                        print "wait time until save ok"
                else:
                    print "get server interface error!"
                time.sleep(5)
        else:
            time.sleep(15)
            print "purchase time is no region!"

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



#购买 电邮
def start_purchase(purchase_element_list, interval, money):
    #计算历史总盈利
    gain_all_money = 0
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    sum_objects_predict = KillPredict.objects.filter(kill_predict_date = current_date)
    for gain in sum_objects_predict:
        if (gain.gain_money):
            gain_all_money = gain_all_money + gain.gain_money
    print "gain_all_money:",gain_all_money

    #开始购买
    try:
        interval['purchase_driver'] = reload_pxiagme1_pk10_driver(interval['purchase_driver'])
        purchase_driver = interval['purchase_driver']

        if 1:
            #切换到子框架
            print "chongzhi!"
            purchase_driver.find_element_by_xpath('//*[@id="memberMainContent"]/div[2]/table/tbody/tr/td[2]/a[2]').click()
            time.sleep(2)

            #遍历填充值
            print "start fill"
            for purchase_element in purchase_element_list:
                print "purchase_element:",purchase_element
                sub_element = purchase_driver.find_element_by_xpath(purchase_element)
                sub_element.send_keys(money)

            print "confirm..."
            confirm = purchase_driver.find_element_by_xpath('//*[@id="memberMainContent"]/div[2]/table/tbody/tr/td[2]/a[1]')
            confirm.click()
            time.sleep(2)
            # 提交按钮
            print "click submit"
            if len(purchase_element_list) > 7:
                submit = purchase_driver.find_element_by_xpath('//*[@id="betSlipDivContent"]/table/tbody/tr[3]/td/a[1]')
            else:
                submit = purchase_driver.find_element_by_xpath('//*[@id="betSlipDivContent"]/table/tbody/tr[2]/td/a[1]')
            #'//*[@id="betSlipDivContent"]/table/tbody/tr[2]/td/a[1]'
            #'//*[@id="betSlipDivContent"]/table/tbody/tr[3]/td/a[1]'
            submit.click()

            return True
    except:
        return False


#根据预测list转换成要购买的元素
def get_xiazhu_message_dianyou(purchase_number_str):
    buy_element_list = []
    # purchase_number_str = '0,9|2|4|7,9|2|10|6,3|4|5|6|7|9,8|1|2|10,1|2|5|7|8|9,1|3|6|8|9|10'
    purchase_number_list = purchase_number_str.split(',')
    for index in range(len(purchase_number_list)):
        if purchase_number_list[index] == '0':
            pass
        else:
            purchase_numbers = purchase_number_list[index].split('|')
            for purchase_number in purchase_numbers:
                #buy_element_list.append('//*[@id="a_B' + str(index+1) + '_' + str(purchase_number) + '"]/input')
                # 构造path
                # 补全2位列,后移2位
                column = str(index+1).zfill(2)
                # 补全2位值
                value = str(purchase_number).zfill(2)
                xpath = '//*[@id="itmStakeInput2' + column + '1' + value + '"]'
                print "xpath:",xpath
                buy_element_list.append(xpath)
    print buy_element_list
    return buy_element_list


def reload_pxiagme1_pk10_driver(driver):
    #重新加载
    print "reload pk10"
    driver.get(driver.current_url)
    driver.switch_to_frame("topFrame")
    print "top frameset1"
    time.sleep(1)

    #pk10
    pk10 = driver.find_element_by_xpath('//*[@id="201"]/a')
    pk10.click()
    time.sleep(1)

    # 1-10
    element_1_10 = driver.find_element_by_xpath('//*[@id="2011to10"]')
    element_1_10.click()
    time.sleep(1)
    #返回原始框架
    driver.switch_to_default_content()
    time.sleep(1)
    #切换到主框架
    driver.switch_to_frame("mainFrame")
    # driver.switch_to.frame()
    print "switch mainFrame"
    time.sleep(1)
    #获取输入框
    #一般
    element_normal = driver.find_element_by_xpath('//*[@id="normalBetSlip"]')
    element_normal.click()
    time.sleep(3)
    print driver.current_url
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
            print "request server faild!"
            time.sleep(3)
            if count > 2:
                request_flag = False
            count = count + 1
    return {}

