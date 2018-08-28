# -*- coding: utf-8 -*-
__author__ = 'shifeixiang'

from django.views.decorators.csrf import csrf_exempt    #用于处理post请求出现的错误
from django.shortcuts import render_to_response
from append_predict.models import ProbUser
from append_predict.models import KillPredict,PredictLottery
from append_predict.thread import ThreadControl
import math
#追加方式规则，以最小的命中率的杀号作为购买号码--公司
#from append_predict.predict_append_rule_100_min import spider_predict_selenium,get_purchase_list
#追加方式规则，以最小的命中率的杀号作为购买号码，同一名次未命中则继续购买同一名次，如果有大于等于4的连中名次，则跳转。
#from append_predict.predict_append_rule_100_jump_continue4 import spider_predict_selenium,get_purchase_list
#基于购买最小的优化，有四个连中，跳转，次小比最小大8，使用次小
from append_predict.predict_append_rule_100_jump_continue4_base_min import spider_predict_selenium,get_purchase_list
#最小命中率 号码是6个 四期未中跳转
#from append_predict.predict_append_rule_100_jump_continue4_base_min_6zhu import spider_predict_selenium,get_purchase_list


from append_predict.spider_pk10 import get_html_result,get_lottery_id_number,load_lottery_predict
import time
import datetime

from pkten_log.pk_log import PkLog

pk_logger = PkLog('append_predict.main').log()

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

#主页面
def predict_main(request):
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
            #print prob_user.user_name, " not start"
            pk_logger.info("%s not start",prob_user.user_name)
            prob_user.user_status = 0
            prob_user.save()
    return render_to_response('append_predict_main.html',{"prob_user_list":prob_user_list})


@csrf_exempt   #处理Post请求出错的情况
def control_predict_thread(request):
    user_name = request.POST['user_name']
    control = request.POST['control']
    info_dict = {}

    #显示活跃状态
    prob_user = ProbUser.objects.get(user_name=user_name)
    if control == 'start':
        driver = spider_predict_selenium()
        info_dict["driver"] = driver
        #状态信息
        c  = ThreadControl()
        #出现错误，则线程不存在，因此启动线程
        try:
            status = c.is_alive(user_name)
            #print "thread is alive? ",status
            pk_logger.debug("thread is alive? %s",status)
            if status:
                #print "thread is alive,caonot start twice!"
                pk_logger.debug("thread is alive,caonot start twice!")
            else:
                #print "start ..........thread1"
                pk_logger.debug("start ..........thread1")
                c.start(user_name, info_dict)
        except:
            #print "thread is not alive start!!!"
            pk_logger.debug("thread is not alive start!!!")
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
            pk_logger.debug("not thread alive")
            #print "not thread alive"
    prob_user_list =  ProbUser.objects.all()
    return render_to_response('append_predict_main.html',{"prob_user_list":prob_user_list})



def spider_save_predict(interval):
    time.sleep(10)
    #爬取当天结果,存入objects
    html_json = get_html_result()
    if html_json == '':
        pass
    else:
        load_lottery_predict(html_json)

        #获取models predict最新值
        lottery_id, kill_predict_number, xiazhu_money = get_predict_model_value()
        pk_logger.debug("lottery_id: %s",lottery_id)
        #print "lottery_id",lottery_id
        if lottery_id == 0:
            #print "no predict record in history"
            pk_logger.debug("no predict record in history")
            last_purchase_hit = True
            xiazhu_nums = 1
            get_predict_kill_and_save(interval, last_purchase_hit, xiazhu_nums)
        else:
            #获取该期的开奖号码
            lottery_num,lottery_time = get_lottery_id_number(lottery_id)
            #print "lottery_num:",lottery_num
            pk_logger.info("lottery_num: %s",lottery_num)
            if (lottery_num):
                #计算命中率并更新models
                #print "save lottery_number"
                last_purchase_hit,xiazhu_nums = calculate_percisoin(lottery_id, lottery_num, kill_predict_number, lottery_time, xiazhu_money)
                pk_logger.info("last_purchase_hit: %s",last_purchase_hit)
                pk_logger.info("xiazhu_nums: %s",xiazhu_nums)
                #print "last_purchase_hit", last_purchase_hit , "xiazhu_nums" , xiazhu_nums
                get_predict_kill_and_save(interval, last_purchase_hit, xiazhu_nums)
            else:
                #print "pay interface lottery id request faild. continue...."
                pk_logger.error("pay interface lottery id request faild. continue....")
                time.sleep(10)
                spider_save_predict(interval)
                
    #get_predict_kill_and_save(interval)

def get_predict_kill_and_save(interval, last_purchase_hit, xiazhu_nums):
    #爬取下一期predict
    predict_lottery_id,purchase_number_list,purchase_number_list_desc,predict_number_all_list_str, current_percent_all_list_str, purchase_mingci_number = get_purchase_list(interval, last_purchase_hit, xiazhu_nums)
    if predict_lottery_id != 0:
        #更新models
        #print "save:",predict_lottery_id,'  ',purchase_number_list
        pk_logger.info("save predict_lottery_id : %s",predict_lottery_id)
        pk_logger.info("save purchase_number_list : %s", purchase_number_list)
        #current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))

        #根据时间判断日期是否加一天
        jump_flag_date = time.strftime("%H:%M:%S", time.localtime())
        if jump_flag_date > '23:57:59' or jump_flag_date <= '00:03:00':
            current_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        save_predict_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #基于前面开奖结果计算下注金额基础(1为基准值)
        #xiazhu_money = get_xiazhu_money_base_on_history_purchase_record(purchase_number_list, current_date)
        #基于前面开奖结果计算下注金额基础(1为基准值)  递增(n*(n+ 1))/2追加
        #xiazhu_money = get_xiazhu_money_base_on_history_purchase_record_increase(purchase_number_list, current_date)
        #基于前面开奖结果计算下注金额基础(1为基准值)  递增1追加
        #xiazhu_money = get_xiazhu_money_base_on_history_purchase_record_increase_one(purchase_number_list, current_date)
        #自定义倍数
        #xiazhu_money = get_xiazhu_money_base_on_history_purchase_record_increase_define(purchase_number_list, current_date)
        #保本追加
        xiazhu_money = get_xiazhu_money_base_on_history_purchase_record_baoben(purchase_number_list, current_date)

        #保存
        p = KillPredict(kill_predict_date=current_date, save_predict_time=save_predict_time, lottery_id = int(predict_lottery_id), kill_predict_number = purchase_number_list,
                            kill_predict_number_desc=purchase_number_list_desc, percent_all_list_desc=current_percent_all_list_str,
                            predict_total=0, target_total=0, predict_accuracy=0,
                            predict_number_all=predict_number_all_list_str, xiazhu_money=xiazhu_money, gain_money=0, is_xiazhu=0, input_money=0, xiazhu_nums=purchase_mingci_number)
        p.save()


#基于历史购买记录计算本期的下注金额基数--,递增追加1,3,6,10,15递增追加，未中加一，中了原数据保持
def get_xiazhu_money_base_on_history_purchase_record_increase(purchase_number_list, current_date):
    xiazhu_predicts = KillPredict.objects.filter(kill_predict_date=current_date).order_by("-lottery_id")
    for xiazhu_predict in xiazhu_predicts:
        last_xiazhu_predict = xiazhu_predict
        if last_xiazhu_predict.xiazhu_money != 0:
            break
    xiahu_money_result = 1
    gain_money_total = 0
    for xiazhu_predict in xiazhu_predicts:
        if (xiazhu_predict.is_xiazhu == 1):
            if (xiazhu_predict.xiazhu_money > 1):
                gain_money_total = gain_money_total + xiazhu_predict.gain_money
            elif xiazhu_predict.xiazhu_money == 1:
                gain_money_total = gain_money_total + xiazhu_predict.gain_money
                break

    pk_logger.info("gain_money_total total : %d",gain_money_total)
    current_purchase_length = 0
    column_count = 0
    for purchase_number in purchase_number_list.split(','):
        if purchase_number == '0':
            continue
        else:
            current_purchase_length = current_purchase_length + len(purchase_number.split('|'))
            column_count = column_count + 1
    pk_logger.debug("purchase_number_list len: %d",current_purchase_length)

    if gain_money_total < -450:
        gain_money_total = 0

    if gain_money_total < -1:
        #上一期命中，递增下注
        if last_xiazhu_predict.gain_money < 0:
            #平方增长
            #xiahu_money_result = math.pow((math.sqrt(last_xiazhu_predict.xiazhu_money) + 1),2)
            #n(n+1)/2增长
            xiahu_money_result = int(math.ceil(math.sqrt(last_xiazhu_predict.xiazhu_money * 2)) + last_xiazhu_predict.xiazhu_money)
        #否则保持不变
        else:
            # calc_xainzhu = math.ceil(math.fabs(gain_money_total/(10 - current_purchase_length)))
            # xiahu_money_result = min(last_xiazhu_predict.xiazhu_money,calc_xainzhu)
            #若本期不购买，则下注金额使用上一期
            if column_count == 0 or current_purchase_length == 0:
                xiahu_money_result = last_xiazhu_predict.xiazhu_money
            else:
                calc_xainzhu = math.ceil(math.fabs(gain_money_total/(10*column_count - current_purchase_length)))
                pk_logger.info("calc_xainzhu:%d, last_xiazhu:%d",calc_xainzhu, last_xiazhu_predict.xiazhu_money)
                xiahu_money_result = max(min(last_xiazhu_predict.xiazhu_money,calc_xainzhu),2)
    else:
        xiahu_money_result = 1

    xiahu_money_result = int(xiahu_money_result)
    pk_logger.info("result xiazhu : %d",xiahu_money_result)
    return xiahu_money_result



#基于历史购买记录计算本期的下注金额基数--1  3  6 12  25，中了递减，不中递增，6/12两次 25 2次
def get_xiazhu_money_base_on_history_purchase_record_increase_define(purchase_number_list, current_date):
    xiazhu_predicts = KillPredict.objects.filter(kill_predict_date=current_date).order_by("-lottery_id")
    record_index = 0
    for xiazhu_predict in xiazhu_predicts:
        if xiazhu_predict.is_xiazhu == 1 and record_index == 0:
            last_xiazhu_predict = xiazhu_predict
            record_index = record_index + 1
            continue
        if xiazhu_predict.is_xiazhu == 1 and record_index == 1:
            last_last_xiazhu_predict = xiazhu_predict
            record_index = record_index + 1
            continue
    xiahu_money_result = 1
    gain_money_total = 0
    for xiazhu_predict in xiazhu_predicts:
        if (xiazhu_predict.is_xiazhu == 1):
            if (xiazhu_predict.xiazhu_money > 1):
                gain_money_total = gain_money_total + xiazhu_predict.gain_money
            elif xiazhu_predict.xiazhu_money == 1:
                gain_money_total = gain_money_total + xiazhu_predict.gain_money
                break

    pk_logger.info("gain_money_total total : %d",gain_money_total)
    #总长度，即总购买个数
    current_purchase_length = 0
    #名次个数，考虑名次相同的情况或者同事有4期未中的情况
    column_count = 0
    for purchase_number in purchase_number_list.split(','):
        if purchase_number == '0':
            continue
        else:
            current_purchase_length = current_purchase_length + len(purchase_number.split('|'))
            column_count = column_count + 1
    pk_logger.debug("purchase_number_list len: %d",current_purchase_length)
    if gain_money_total < -500:
        gain_money_total = 0
    if record_index > 1:
        pk_logger.info("last_xiazhu_predict.xiazhu_money:%s",last_xiazhu_predict.xiazhu_money)
        pk_logger.info("last_xiazhu_predict.gain_money:%s", last_xiazhu_predict.gain_money)
        pk_logger.info("last_last_xiazhu_predict.xiazhu_money:%s",last_last_xiazhu_predict.xiazhu_money)
    else:
        pk_logger.info("no predict record")
    if gain_money_total < -1:
        #上一期命中，递增下注
        if last_xiazhu_predict.xiazhu_money == 1:
            if last_xiazhu_predict.gain_money < 0:
                xiahu_money_result = 3
            else:
                xiahu_money_result = 3
        if last_xiazhu_predict.xiazhu_money == 3:
            if last_xiazhu_predict.gain_money < 0:
                xiahu_money_result = 6
            else:
                xiahu_money_result = 1

        if last_xiazhu_predict.xiazhu_money == 6:
            if last_last_xiazhu_predict.xiazhu_money == 6 or last_last_xiazhu_predict.xiazhu_money == 3:
                if last_xiazhu_predict.gain_money < 0:
                    xiahu_money_result = 12
                else:
                    xiahu_money_result = 3
            else:
                if last_xiazhu_predict.gain_money < 0:
                    xiahu_money_result = 12
                else:
                    xiahu_money_result = 6

        if last_xiazhu_predict.xiazhu_money == 12:
            if last_last_xiazhu_predict.xiazhu_money == 12 or last_last_xiazhu_predict.xiazhu_money == 6:
                if last_xiazhu_predict.gain_money < 0:
                    xiahu_money_result = 25
                else:
                    xiahu_money_result = 6

            else:
                if last_xiazhu_predict.gain_money < 0:
                    xiahu_money_result = 25
                else:
                    xiahu_money_result = 12

        if last_xiazhu_predict.xiazhu_money == 25:
            if last_last_xiazhu_predict.xiazhu_money == 25:
                if last_xiazhu_predict.gain_money < 0:
                    xiahu_money_result = 1
                else:
                    xiahu_money_result = 12
            else:
                if last_xiazhu_predict.gain_money < 0:
                    xiahu_money_result = 25
                else:
                    xiahu_money_result = 12

    else:
        xiahu_money_result = 1

    xiahu_money_result = int(xiahu_money_result)
    pk_logger.info("result xiazhu : %d",xiahu_money_result)
    return xiahu_money_result



#基于历史购买记录计算本期的下注金额基数--,递增追加1,2,3,4,5递增追加，未中加一，中了原数据保持
def get_xiazhu_money_base_on_history_purchase_record_increase_one(purchase_number_list, current_date):
    xiazhu_predicts = KillPredict.objects.filter(kill_predict_date=current_date).order_by("-lottery_id")
    for xiazhu_predict in xiazhu_predicts:
        last_xiazhu_predict = xiazhu_predict
        if last_xiazhu_predict.xiazhu_money != 0:
            break
    xiahu_money_result = 1
    gain_money_total = 0
    for xiazhu_predict in xiazhu_predicts:
        if (xiazhu_predict.is_xiazhu == 1):
            if (xiazhu_predict.xiazhu_money > 1):
                gain_money_total = gain_money_total + xiazhu_predict.gain_money
            elif xiazhu_predict.xiazhu_money == 1:
                gain_money_total = gain_money_total + xiazhu_predict.gain_money
                break

    pk_logger.info("gain_money_total total : %d",gain_money_total)
    #总长度，即总购买个数
    current_purchase_length = 0
    #名次个数，考虑名次相同的情况或者同事有4期未中的情况
    column_count = 0
    for purchase_number in purchase_number_list.split(','):
        if purchase_number == '0':
            continue
        else:
            current_purchase_length = current_purchase_length + len(purchase_number.split('|'))
            column_count = column_count + 1
    pk_logger.debug("purchase_number_list len: %d",current_purchase_length)
    if gain_money_total < -300:
        gain_money_total = 0
    if gain_money_total < -1:
        #上一期命中，递增下注
        if last_xiazhu_predict.gain_money < 0:
            #平方增长
            #xiahu_money_result = math.pow((math.sqrt(last_xiazhu_predict.xiazhu_money) + 1),2)
            #n(n+1)/2增长
            #xiahu_money_result = int(math.ceil(math.sqrt(last_xiazhu_predict.xiazhu_money * 2)) + last_xiazhu_predict.xiazhu_money)
            #3的倍数增长
            # if last_xiazhu_predict.xiazhu_money == 1:
            #     xiahu_money_result = last_xiazhu_predict.xiazhu_money + 2
            # else:
            #     xiahu_money_result = last_xiazhu_predict.xiazhu_money + 3
            #加一增长
            calc_xainzhu = math.ceil(math.fabs(gain_money_total/(10*column_count - current_purchase_length)))
            xiahu_money_result = last_xiazhu_predict.xiazhu_money + 2
            pk_logger.info("calc_xainzhu:%d, last_xiazhu increase:%d",calc_xainzhu, xiahu_money_result)
            xiahu_money_result = min(max(calc_xainzhu,2), xiahu_money_result)
        #否则保持不变
        else:
            #若本期不购买，则下注金额使用上一期
            if column_count == 0 or current_purchase_length == 0:
                xiahu_money_result = last_xiazhu_predict.xiazhu_money
            else:
                calc_xainzhu = math.ceil(math.fabs(gain_money_total/(10*column_count - current_purchase_length)))
                pk_logger.info("calc_xainzhu:%d, last_xiazhu:%d",calc_xainzhu, last_xiazhu_predict.xiazhu_money)
                xiahu_money_result = max(min(last_xiazhu_predict.xiazhu_money,calc_xainzhu),2)
    else:
        xiahu_money_result = 1

    xiahu_money_result = int(xiahu_money_result)
    pk_logger.info("result xiazhu : %d",xiahu_money_result)
    return xiahu_money_result


#保本追加  总金额超过一定数目初始化
def get_xiazhu_money_base_on_history_purchase_record_baoben(purchase_number_list, current_date):
    xiazhu_predicts = KillPredict.objects.filter(kill_predict_date=current_date).order_by("-lottery_id")
    for xiazhu_predict in xiazhu_predicts:
        last_xiazhu_predict = xiazhu_predict
        if last_xiazhu_predict.xiazhu_money != 0 and last_xiazhu_predict.is_xiazhu == 1:
            break
    xiahu_money_result = 1
    gain_money_total = 0
    for xiazhu_predict in xiazhu_predicts:
        if (xiazhu_predict.is_xiazhu == 1):
            if (xiazhu_predict.xiazhu_money > 1):
                gain_money_total = gain_money_total + xiazhu_predict.gain_money
            elif xiazhu_predict.xiazhu_money == 1:
                gain_money_total = gain_money_total + xiazhu_predict.gain_money
                break

    pk_logger.info("gain_money_total total : %d",gain_money_total)
    #总长度，即总购买个数
    current_purchase_length = 0
    #名次个数，考虑名次相同的情况或者同事有4期未中的情况
    column_count = 0
    for purchase_number in purchase_number_list.split(','):
        if purchase_number == '0':
            continue
        else:
            current_purchase_length = current_purchase_length + len(purchase_number.split('|'))
            column_count = column_count + 1
    pk_logger.debug("purchase_number_list len: %d",current_purchase_length)
    # if gain_money_total < -300:
    #     gain_money_total = 0
    if gain_money_total < -1:
        #上一期命中，递增下注
        if last_xiazhu_predict.gain_money < 0:

            calc_xainzhu = round(math.fabs(gain_money_total/(9.9*column_count - current_purchase_length)))
            pk_logger.info("calc_xainzhu:%d, last_xiazhu increase:%d",calc_xainzhu, xiahu_money_result)
            xiahu_money_result = max(calc_xainzhu,2)
        else:
            xiahu_money_result = 1
    else:
        xiahu_money_result = 1
    next_xiazhu_all = gain_money_total - current_purchase_length * xiahu_money_result
    pk_logger.info("next_xiazhu_all total : %d",next_xiazhu_all)
    if next_xiazhu_all < -350:
        xiahu_money_result = 1

    xiahu_money_result = int(xiahu_money_result)

    #临时测试使用
    #xiahu_money_result = 1
    pk_logger.info("result xiazhu : %d",xiahu_money_result)
    return xiahu_money_result

#基于历史购买记录计算本期的下注金额基数,---追加方案，无损追加，风险极高，6期以上连中必死
def get_xiazhu_money_base_on_history_purchase_record(purchase_number_list, current_date):
    xiazhu_predicts = KillPredict.objects.filter(kill_predict_date=current_date).order_by("-lottery_id")
    xiahu_money_result = 1
    gain_money_total = 0
    lose_times = 0
    for xiazhu_predict in xiazhu_predicts:
        if (xiazhu_predict.is_xiazhu == 1 and xiazhu_predict.gain_money > 0):
            break
        if (xiazhu_predict.is_xiazhu == 1 and xiazhu_predict.gain_money < 0):
            gain_money_total = gain_money_total + xiazhu_predict.gain_money
            lose_times = lose_times + 1
            #print "gain_money_total sub:",gain_money_total
            pk_logger.debug("gain_money_total sub: %d",gain_money_total)
    #print "gain_money_total total:",gain_money_total
    pk_logger.debug("gain_money_total total: %d",gain_money_total)

    chaoqi_count = 0
    #连续未中大于6期处理
    if lose_times > 6:
        #print "lose times over!!!!",lose_times
        pk_logger.debug("lose times over!!!!: %d",lose_times)
        gain_money_total = 0
        #取余
        lose_times = lose_times % 7
        #print "lose times init !!!!",lose_times
        pk_logger.debug("lose times init : %d",lose_times)
        for xiazhu_predict in xiazhu_predicts:
            if (xiazhu_predict.is_xiazhu == 1 and xiazhu_predict.gain_money > 0):
                break
            if (xiazhu_predict.is_xiazhu == 1 and xiazhu_predict.gain_money < 0):
            #只计算6期以后的赔的金额
                if lose_times > chaoqi_count:
                    gain_money_total = gain_money_total + xiazhu_predict.gain_money
                    chaoqi_count = chaoqi_count + 1
    else:
        pk_logger.debug("lose times less 6 : %d",lose_times)

    current_purchase_length = 0
    for purchase_number in purchase_number_list.split(','):
        if purchase_number == '0':
            continue
        else:
            current_purchase_length = len(purchase_number.split('|'))
            break
    #print "current_purchase_length:",current_purchase_length
    pk_logger.debug("current_purchase_length : %d",current_purchase_length)
    if current_purchase_length == 0:
        xiahu_money_result = 0
    else:
        if gain_money_total < 0:
            xiahu_money_result = math.fabs(gain_money_total/(9.9 - current_purchase_length))
        else:
            xiahu_money_result = 1
        #print "xiahu_money_result:",xiahu_money_result
    #print "base xiazhu:",xiahu_money_result
    pk_logger.debug("base xiazhu: %d",xiahu_money_result)
    
    xiahu_money_result = round(xiahu_money_result)
    lose_times_money = pow(2, (lose_times + 1))
    #print "lose_times_money:",lose_times_money
    pk_logger.debug("lose_times_money: %d",lose_times_money)
    if lose_times > 3:
    	#print "lose_times:",lose_times
        pk_logger.debug("lose_times: %d",lose_times)
        xiahu_money_result = int((lose_times_money + xiahu_money_result)/2)
    #xiahu_money_result = min(xiahu_money_result,lose_times_money)
    xiahu_money_result = int(xiahu_money_result)
    #print "result xiazhu:",xiahu_money_result
    pk_logger.debug("result xiazhu: %d",xiahu_money_result)
    return xiahu_money_result

#获取最新一期的预测值得相关信息
def get_predict_model_value():
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    predicts = KillPredict.objects.filter(kill_predict_date=current_date).order_by("-lottery_id")
    lottery_id = 0
    kill_predict_number = 0
    xiazhu_money = 0
    if len(predicts) == 0:
        #print "predicts is null"
        pk_logger.debug("predicts is null")
    else:
        lottery_id = predicts[0].lottery_id
        kill_predict_number = predicts[0].kill_predict_number
        xiazhu_money = predicts[0].xiazhu_money
    return lottery_id, kill_predict_number, xiazhu_money


def calculate_percisoin(lottery_id, lottery_num, kill_predict_number, lottery_time, xiazhu_money):
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
                pass
            else:
                #print " result_data[i],purchase_number_list[i]:", str(int(result_data[i])),purchase_number_list[i]
                pk_logger.debug("mingci [%d]: %s",(i+1),str(int(result_data[i])))
                pk_logger.debug("purchase_number_list[i]: %s",purchase_number_list[i])
                if str(int(result_data[i])) in purchase_number_list[i]:
                    target_count = target_count +  1
                all_count = all_count + len(purchase_number_list[i])
        #print "all_count,target_count:", all_count,target_count
        pk_logger.debug("------all_count: %d  ----target_count: %d ",all_count,target_count)
        if all_count == 0:
            predict_accuracy = 0
            gain_money = 0
        else:
            predict_accuracy = float(float(target_count)/float(all_count))
            gain_money = (target_count * 9.9 - all_count) * xiazhu_money
            #print float(float(target_count)/float(all_count))
            pk_logger.debug("target_count: %f",float(float(target_count)/float(all_count)))
        try:
            p = KillPredict.objects.get(lottery_id=lottery_id)
            xiazhu_nums = p.xiazhu_nums
            p.kill_predict_time = lottery_time
            p.lottery_number = lottery_num
            p.predict_total = all_count
            p.target_total = target_count
            p.predict_accuracy = predict_accuracy
            if p.is_xiazhu == 1:
                p.gain_money = gain_money
            #p.input_money = all_count * xiazhu_money
            #p.is_xiazhu = 1
            p.save()
            #判断上一期是否盈利，未盈利，则记录该名词，以后每期购买该名次，知道买中
            if gain_money<0:
                return False, xiazhu_nums
            else:
                return True, xiazhu_nums
        except:
            #print "the ",lottery_id," is repeat!!!"
            pk_logger.debug("the %d is repeat!!!",lottery_id)
            return True,1
    else:
        #print 'length error'
        pk_logger.debug("length error")
        return True,1

#删除当天的信息
def delete_kill_predict_current_date(request):

    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))

    KillPredict.objects.filter(kill_predict_date=current_date).delete()

    obj_pro_predict = KillPredict.objects.filter(kill_predict_date=current_date)
    return render_to_response('test.html',{"obj_pro_predict":obj_pro_predict})


import json
from django.http import HttpResponse
#获取杀号预测数据接口
def get_predict(request):
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    result_info = {}
    # lotterys = KillPredict.objects.filter(lottery_date=current_date)
    #获取预测的lottery id 和预测的号码
    obj_pro_predict = KillPredict.objects.filter(kill_predict_date=current_date).order_by("-lottery_id")
    if len(obj_pro_predict) == 0:
        pass
    else:
        result_info['predict_lottery_id'] = int(obj_pro_predict[0].lottery_id)
        result_info['predict_number_list'] = obj_pro_predict[0].kill_predict_number
        result_info['predict_number_list_desc'] = obj_pro_predict[0].kill_predict_number_desc
        pk_logger.debug("obj_pro_predict[0].lottery_id: %d",obj_pro_predict[0].lottery_id)
        pk_logger.debug("obj_pro_predict[0].kill_predict_number: %s",obj_pro_predict[0].kill_predict_number)
        #print obj_pro_predict[0].lottery_id
        #print obj_pro_predict[0].kill_predict_number

    #获取目前最新的开奖lottery id
    # html_json = get_html_result()
    # if html_json == '':
    #     result_info['last_lottery_id'] = 999999
    #     #pass
    # else:
    #     load_lottery_predict(html_json)
    obj_pro_lottery = PredictLottery.objects.filter(lottery_date=current_date).order_by("-lottery_id")
    if len(obj_pro_lottery) == 0:
        result_info['last_lottery_id'] = 0
        pass
    else:
        result_info['last_lottery_id'] = int(obj_pro_lottery[0].lottery_id)
        result_info['lottery_number'] = obj_pro_lottery[0].lottery_number
        #print obj_pro_lottery[0].lottery_id
        pk_logger.debug("obj_pro_lottery[0].lottery_id: %d",obj_pro_lottery[0].lottery_id)
    #print "obj_pro",obj_pro_predict
    return HttpResponse(json.dumps(result_info), content_type="application/json")


#删除当天的信息
def delete_kill_predict_current_date(request):

    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))

    KillPredict.objects.filter(kill_predict_date=current_date).delete()

    obj_pro_predict = KillPredict.objects.filter(kill_predict_date=current_date)
    return render_to_response('test.html',{"obj_pro_predict":obj_pro_predict})




import json
from django.http import HttpResponse
#获取杀号预测数据接口
def get_predict(request):
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    result_info = {}
    # lotterys = KillPredict.objects.filter(lottery_date=current_date)
    #获取预测的lottery id 和预测的号码
    obj_pro_predict = KillPredict.objects.filter(kill_predict_date=current_date).order_by("-lottery_id")
    if len(obj_pro_predict) == 0:
        pass
    else:
        result_info['predict_lottery_id'] = int(obj_pro_predict[0].lottery_id)
        result_info['predict_number_list'] = obj_pro_predict[0].kill_predict_number
        result_info['predict_number_list_desc'] = obj_pro_predict[0].kill_predict_number_desc
        result_info['xiazhu_money'] = obj_pro_predict[0].xiazhu_money
        result_info['save_predict_time'] = obj_pro_predict[0].save_predict_time
        #print "predict lottery_id:",obj_pro_predict[0].lottery_id

        #pk_logger.info("predict lottery_id: %d",obj_pro_predict[0].lottery_id)
        #pk_logger.info("kill_predict_number: %s",obj_pro_predict[0].kill_predict_number)
        #print "kill_predict_number:",obj_pro_predict[0].kill_predict_number

    obj_pro_lottery = PredictLottery.objects.filter(lottery_date=current_date).order_by("-lottery_id")
    if len(obj_pro_lottery) == 0:
        result_info['last_lottery_id'] = 0
        pass
    else:
        result_info['last_lottery_id'] = int(obj_pro_lottery[0].lottery_id)
        result_info['lottery_number'] = obj_pro_lottery[0].lottery_number
        #print "last lottery_id:",obj_pro_lottery[0].lottery_id
        #pk_logger.info("last lottery_id: %d",obj_pro_lottery[0].lottery_id)
    return HttpResponse(json.dumps(result_info), content_type="application/json")