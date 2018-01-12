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
from auto_visit.pretreatment import get_rule, parase_lotterys,check_double_match,check_single_match,parase_lotterys_cross, tran_croos_data_auto, change_r_l, check_cross_match
from auto_visit.driver import get_driver

# Create your views here.
import time


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
    password = ProbUser.objects.get(user_name=user_name).user_password;
    control = request.POST['control']

    # for i in range(len(in_rule_list)):
    #     print i,"  ",in_upper_money_list[i]
    #     print i,"  ",in_lower_money_list[i]

    # rule = request.POST['auto_in_rule']
    # upper_money = request.POST['auto_in_upper_money']
    # upper_money = 10

    # print "user_name is ",user_name, " pwd ",password

    # print info_dict["money"],info_dict["rule"],info_dict["upper_money"]
    # prob_user_list = ProbUser.objects.all()
    # return render_to_response('auto_main.html',{"prob_user_list":prob_user_list, "p_rule":rule, "p_monery":money, "p_upper_number":upper_money})
    # return render_to_response('auto_main.html', {"prob_user_list": prob_user_list})
    # return ('auto_main.html')

    #显示活跃状态
    prob_user = ProbUser.objects.get(user_name=user_name)
    if control == 'start':
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

        #单例模式
        # try:
        #     web_driver = SingleDriver()
        #     driver = web_driver.get_driver()
        #     info_dict["driver"] = driver
        # except:
        #     web_driver = SingleDriver()
        #     driver = get_driver(user_name,password)
        #     web_driver.set_driver(driver)
        #     info_dict["driver"] = driver
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
    return render_to_response('auto_main.html',{"prob_user_list":prob_user_list, "p_rule":str(in_rule_list), "p_monery":money})
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
    ProbUser.objects.all().delete()
    user_id = 1
    user_name = "abab2233"
    user_password = "ABCd1234"
    user_status = False
    obj_pro = ProbUser(user_id=user_id, user_name=user_name, user_password=user_password, user_status=user_status)
    obj_pro.save()
    return render_to_response('test.html')

def get_user_data(request):
    #写入对象
    obj_pro = ProbUser.objects.all()
    return render_to_response('test.html',{"obj_pro":obj_pro})

def get_purchase_data(request):
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    lotterys = LotteryMonth.objects.filter(lottery_date=current_date)
    # obj_pro_purchase = PurchaseRecord.objects.all()
    obj_pro_purchase = PurchaseRecord.objects.filter(purchase_record_rule=1 ,purchase_record_date=current_date).order_by("-purchase_record_id")
    print "obj_pro",obj_pro_purchase
    return render_to_response('test.html',{"obj_pro_purchase":obj_pro_purchase})


# 测试
def get_prob_data(request):
    rule = 1
    money = 10
    upper_money = 30
    PurchaseRecord.objects.all().delete()
    spider_current_date_data()
    current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    print current_date
    lotterys = LotteryMonth.objects.filter(lottery_date=current_date)
    rule_parity_list = get_rule(rule)
    #当天的开奖记录数
    current_date_rows = LotteryMonth.objects.filter(lottery_date=current_date).order_by("-lottery_id")
    print"len(current_date_rows)" , len(current_date_rows)

    #需要匹配的数目
    match_rule_num = len(rule_parity_list)-1
    #记录小于规则数
    if(len(current_date_rows) < match_rule_num):
        pass
    else:
        lottery_max_num = current_date_rows[0].lottery_id
        lottery_max_date = current_date_rows[0].lottery_date
        lottery_purchase_id = current_date_rows[0].lottery_id + 1

        purchase_date_rows = PurchaseRecord.objects.filter(purchase_record_date=current_date).order_by("-purchase_record_id")
        #没有购买记录
        if(len(purchase_date_rows) == 0):
            #直接匹配
            print "purchase is 0"
            lottery_minus_purchase_len = len(lotterys)
            if (len(current_date_rows) >= match_rule_num):
                purchase_record_column_list, purchase_record_value_list, xpath_list = visit_set_prob(rule,rule_parity_list,lotterys,lottery_minus_purchase_len)
                print "xpath_list ",xpath_list
                driver = get_driver()
                continue_flag = True
                while(continue_flag):
                    try :
                        if (len(xpath_list) > 0):
                            for i in range(len(xpath_list)):
                                input_1_big = driver.find_element_by_xpath(xpath_list[i])
                                input_1_big.send_keys(money)
                                time.sleep(1)
                            confirm = driver.find_element_by_xpath('//*[@id="memberMainContent"]/div[2]/table/tbody/tr/td[2]/a[1]')
                            confirm.click()
                            time.sleep(2)
                            #提交按钮
                            submit = driver.find_element_by_xpath('//*[@id="betSlipDivContent"]/table/tbody/tr[2]/td/a[1]')
                                                              # '//*[@id="betSlipDivContent"]/table/tbody/tr[3]/td/a[1]'
                                                              # '//*[@id="betSlipDivContent"]/table/tbody/tr[2]/td/a[1]'
                            submit.click()
                            time.sleep(2)
                            continue_flag = False
                            print "current visit over"
                        else:
                            print "无满足条件"
                            continue_flag = False
                    except:
                        print "封盘中...请稍后..."
                        time.sleep(10)
                        continue_flag = True
                for i in range(len(purchase_record_column_list)):
                    obj_pro = PurchaseRecord(purchase_record_id=lottery_purchase_id, purchase_record_rule=rule, purchase_record_money=money,
                                             purchase_record_column=purchase_record_column_list[i],purchase_record_value=purchase_record_value_list[i])
                    obj_pro.save()
            else:
                pass
        #有该买记录
        else:
            purchase_max_num = purchase_date_rows[0].purchase_record_id
            lottery_minus_purchase_len = lottery_max_num - purchase_max_num
            print "purchase is ",purchase_max_num, " lottery_max_num " ,lottery_max_num
            if(lottery_minus_purchase_len >= match_rule_num):
                purchase_record_column_list, purchase_record_value_list, xpath_list = visit_set_prob(rule,rule_parity_list,lotterys,lottery_minus_purchase_len)
                print "xpath_list ",xpath_list
                for i in range(len(purchase_record_column_list)):
                    obj_pro = PurchaseRecord(purchase_record_id=lottery_purchase_id, purchase_record_rule=rule, purchase_record_money=money,
                                             purchase_record_column=purchase_record_column_list[i],purchase_record_value=purchase_record_value_list[i])
                    obj_pro.save()
            else:
                pass


    prob_data = LotteryMonth.objects.filter(lottery_date=current_date)
    # prob_data = LotteryMonth.objects.all()
    return render_to_response('test.html',{"prob_data":prob_data})



def rule_upper_lower_trans(interval):
    for i in range(len(interval["rule_list"])):
        print "rule--------",interval["rule_list"][i]

    return 0

#正式
def auto_visit_commit(interval):
    rule = interval["rule"]
    money = interval["money"]
    money = money
    upper_money = interval["upper_money"]
    driver = interval["driver"]
    #清空购买记录
    # PurchaseRecord.objects.all().delete()

    #采集当天数据，需要考虑失败重新采集的情况
    spider_current_date_data()
    current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    print current_date
    lotterys = LotteryMonth.objects.filter(lottery_date=current_date)
    if len(lotterys) == 0:
        print "spider open pk10 faild"
        return 0
    rule_parity_list = get_rule(rule)
    #当天的开奖记录数
    current_date_rows = LotteryMonth.objects.filter(lottery_date=current_date).order_by("-lottery_id")
    print"len(current_date_rows)" , len(current_date_rows)

    #需要匹配的数目
    match_rule_num = len(rule_parity_list)-1
    #记录小于规则数
    if(len(current_date_rows) < match_rule_num):
        pass
    else:
        lottery_max_num = current_date_rows[0].lottery_id
        lottery_max_date = current_date_rows[0].lottery_date
        lottery_purchase_id = current_date_rows[0].lottery_id + 1

        #获取当天的该规则的记录
        purchase_date_rows = PurchaseRecord.objects.filter(purchase_record_date=current_date, purchase_record_rule=str(rule)).order_by("-purchase_record_id")
        purchase_date_rows_len = len(purchase_date_rows)
        #没有购买记录
        if(purchase_date_rows_len == 0):
            #直接匹配
            print "purchase is 0"
            sum_money = 0
            lottery_minus_purchase_len = len(lotterys)
            if (len(current_date_rows) >= match_rule_num):
                purchase_record_column_list, purchase_record_value_list, xpath_list = visit_set_prob(rule,rule_parity_list,lotterys)
                print "xpath_list ",xpath_list
                #购买并保存
                confirm_submit_save(driver, xpath_list, money, upper_money, purchase_record_column_list, purchase_record_value_list, lottery_purchase_id, rule, purchase_date_rows_len, current_date)
            else:
                pass
        #有该买记录
        else:
            #获取最大ID
            purchase_max_num = purchase_date_rows[0].purchase_record_id
            lottery_minus_purchase_len = lottery_max_num - purchase_max_num
            print "purchase is ",purchase_max_num, " lottery_max_num " ,lottery_max_num

            if (len(current_date_rows) >= match_rule_num):
                purchase_record_column_list, purchase_record_value_list, xpath_list = visit_set_prob(rule,rule_parity_list,lotterys)
                print "xpath_list ",xpath_list
                #购买并保存
                confirm_submit_save(driver, xpath_list, money, upper_money, purchase_record_column_list, purchase_record_value_list, lottery_purchase_id, rule, purchase_date_rows_len, current_date)


    # prob_data = LotteryMonth.objects.filter(lottery_date=current_date)
    # prob_data = LotteryMonth.objects.all()
    # return render_to_response('test.html',{"prob_data":prob_data})

# 返回满足的列和要购买的值，分别存入2个list
def visit_set_prob(rule,rule_parity_list,lotterys):
    #单双规则
    if (rule < 5):
        base_lottery_list, parity_lottery_list, larsma_lottery_list = parase_lotterys(lotterys)
        column = 1
        purchase_record_column_list = []
        purchase_record_value_list = []
        # 从第一名到第十名
        for parity_lottery in parity_lottery_list:
            #取差值过滤
            # target = parity_lottery[-lottery_minus_purchase_len:]
            target = parity_lottery
            #查看是否匹配
            result = check_single_match(target, rule_parity_list)
            if (result == -1):
                pass
                # print "not match ", column
            else:
                purchase_record_value = result
                purchase_record_value_list.append(purchase_record_value)
                purchase_record_column = column
                purchase_record_column_list.append(purchase_record_column)
                # print "match ", result, " ", column
            column = column + 1
        xpath_list = []
        for i in range(len(purchase_record_column_list)):
            #构造path
            if (purchase_record_value_list[i] == 0):
                xpath = '//*[@id="itmStakeInput20' + str(purchase_record_column_list[i]) + '302"]'
                xpath_list.append(xpath)
            else:
                xpath = '//*[@id="itmStakeInput20' + str(purchase_record_column_list[i]) + '301"]'
                xpath_list.append(xpath)
        return purchase_record_column_list, purchase_record_value_list, xpath_list

    #对子规则
    if (rule == 5):
        base_lottery_list, parity_lottery_list, larsma_lottery_list = parase_lotterys(lotterys)
        column = 1
        purchase_record_column_list = []
        purchase_record_value_list = []
        # 从第一名到第十名
        for base_lottery in base_lottery_list:
            #获取差值
            # target = base_lottery[-lottery_minus_purchase_len:]
            target = base_lottery
            #查看是否匹配,对子规则，[5,5,5]，规则长度为3，满足前两个相同，第三个购买
            result = check_double_match(target,3)
            # result = check_single_match(target, rule_parity_list)
            if (result == -1):
                pass
                print "not match ", column
            else:
                purchase_record_value = result
                purchase_record_value_list.append(purchase_record_value)
                purchase_record_column = column
                purchase_record_column_list.append(purchase_record_column)
                print "match ", result, " ", column
            column = column + 1
        xpath_list = []
        for i in range(len(purchase_record_column_list)):
            #构造path
            #补全2位列
            column = str(purchase_record_column_list[i]).zfill(2)
            #补全2位值
            value = str(purchase_record_value_list[i]).zfill(2)
            xpath = '//*[@id="itmStakeInput2' + column + '1' + value  +  '"]'
            xpath_list.append(xpath)
        return purchase_record_column_list, purchase_record_value_list, xpath_list

    #交叉规则
    if (rule == 6):
        # base_lottery_list, parity_lottery_list, larsma_lottery_list = parase_lotterys(lotterys)
        order_lottery_list = parase_lotterys_cross(lotterys)
        #定义计算的列和总列数
        column_num = 10
        calc_num = 2
        #格式化交叉数据
        order_lottery_list_cross_parase = tran_croos_data_auto(order_lottery_list,column_num, calc_num)
        #左右交换
        last_parity_lottery_list = change_r_l(order_lottery_list_cross_parase)

        column = 1
        purchase_record_column_list = []
        purchase_record_value_list = []
        # 从第一名到第十名，这里只获取前8行
        for parity_lottery in last_parity_lottery_list:
            if column > 8:
                break
            else:
                target = parity_lottery
                #查看是否匹配,对子规则，[5,5,5]，规则长度为3，满足前两个相同，第三个购买
                result = check_cross_match(target,3)
                # result = check_single_match(target, rule_parity_list)
                if (result == -1):
                    pass
                    print "not match ", column
                else:
                    purchase_record_value = result
                    purchase_record_value_list.append(purchase_record_value)
                    purchase_record_column = column + 2
                    purchase_record_column_list.append(purchase_record_column)
                    print "match ", result, " ", column
            column = column + 1
        xpath_list = []
        for i in range(len(purchase_record_column_list)):
            #构造path
            #补全2位列,后移2位
            column = str(purchase_record_column_list[i]).zfill(2)
            #补全2位值
            value = str(purchase_record_value_list[i]).zfill(2)
            xpath = '//*[@id="itmStakeInput2' + column + '1' + value  +  '"]'
            xpath_list.append(xpath)
        return purchase_record_column_list, purchase_record_value_list, xpath_list

#提交结果并保存
def confirm_submit_save(driver, xpath_list, money, upper_money, purchase_record_column_list, purchase_record_value_list, lottery_purchase_id, rule, purchase_date_rows_len, current_date):
    continue_flag = True
    exit_flag = 0
    while (continue_flag):
        exit_flag = exit_flag + 1
        if 1:
            # 重置
            driver.find_element_by_xpath('//*[@id="memberMainContent"]/div[2]/table/tbody/tr/td[2]/a[2]').click()
            if (len(xpath_list) > 0):
                for i in range(len(xpath_list)):
                    print "set element data ", xpath_list[i], "  ", money
                    if(purchase_date_rows_len == 0):
                        sum_money = 0
                    else:
                        #获取购买的总值,当前日期，当前规则，当前列即第几名的购买总值
                        if len(purchase_record_column_list) == i:
                            print "list index out of range",len(xpath_list),"  ",len(purchase_record_column_list)
                            continue_flag = False
                            break
                        purcahse_all = PurchaseRecord.objects.filter(purchase_record_date=current_date, purchase_record_rule=rule, purchase_record_column=purchase_record_column_list[i])
                        sum_money = 0
                        for purchase in purcahse_all:
                            sum_money = sum_money + purchase.purchase_record_money
                        print "purchase all money ",sum_money
                    #超出预算
                    if (sum_money > upper_money):
                        print purchase_record_column_list[i], " column over the budget"
                        purchase_record_column_list.remove(purchase_record_column_list[i])
                        purchase_record_value_list.remove(purchase_record_value_list[i])
                        continue
                    else:
                        input_1_big = driver.find_element_by_xpath(xpath_list[i])
                        input_1_big.send_keys(money)
                        time.sleep(2)
                print "click confirm"
                try:
                    confirm = driver.find_element_by_xpath('//*[@id="memberMainContent"]/div[2]/table/tbody/tr/td[2]/a[1]')
                    #'//*[@id="memberMainContent"]/div[2]/table/tbody/tr/td[2]/a[1]'
                    confirm.click()
                    time.sleep(3)
                    #提交按钮
                    print "click submit"
                    submit = driver.find_element_by_xpath('//*[@id="betSlipDivContent"]/table/tbody/tr[2]/td/a[1]')
                    # '//*[@id="betSlipDivContent"]/table/tbody/tr[3]/td/a[1]'
                    # '//*[@id="betSlipDivContent"]/table/tbody/tr[2]/td/a[1]'
                    submit.click()
                    time.sleep(3)
                    continue_flag = False
                    print "current visit over"
                    #保存
                    for i in range(len(purchase_record_column_list)):
                        # print "purchase message:",lottery_purchase_id,"  ",rule,"  ", money, "  ", purchase_record_column_list[i], "  ", purchase_record_value_list[i]
                        print "purchase message:","number:",lottery_purchase_id," rule: ",rule," money: ", money, " column ", purchase_record_column_list[i], " number ", purchase_record_value_list[i]
                        obj_pro = PurchaseRecord(purchase_record_date = current_date, purchase_record_id=lottery_purchase_id, purchase_record_rule=str(rule),
                                                     purchase_record_money=money,
                                                     purchase_record_column=purchase_record_column_list[i],
                                                     purchase_record_value=purchase_record_value_list[i])
                        obj_pro.save()
                    print "save purcahse record!"
                except:
                    print "no purchase"
                    continue_flag = False
            else:
                print "no any match"
                continue_flag = False
        else:
            print "close..wait..."
            # 重置'//*[@id="memberMainContent"]/div[2]/table/tbody/tr/td[2]/a[2]'
            driver.find_element_by_xpath('//*[@id="memberMainContent"]/div[2]/table/tbody/tr/td[2]/a[2]').click()
            print "wait 30s"
            time.sleep(30)
            continue_flag = False
        # 持续封盘 退出
        if (exit_flag > 8):
            continue_flag = False
