#coding=utf-8
__author__ = 'shifeixiang'


import time
from selenium import webdriver
from bs4 import BeautifulSoup
from append_predict_sandd.models import KillPredict

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from append_predict_sandd.models import PredictLottery

from pkten_log.pk_log import PkLog
pk_logger = PkLog('append_predict_sandd.predict_append_rule').log()
#获取predict driver
def spider_predict_selenium():

    driver_flag = True
    while(driver_flag):
        driver = webdriver.Firefox(executable_path = 'E:\\python\\webdriver\\firefox\\geckodriver.exe')

        driver.get("https://www.1399p.com/pk10/shdd")
        try:
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME , "lotteryNumber")))
            driver_flag = False
            return driver
        except:
            print "get driver time out"
            driver.quit()
            time.sleep(10)

#两面盘预测
def get_purchase_list_sandd():
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    #倒排序，开奖号码取最大值
    lotterys = PredictLottery.objects.filter(lottery_date=current_date).order_by("-lottery_id")
    for lottery in lotterys:
        lottery_id = lottery.lottery_id
        break
    lottery_id = lottery_id + 1
    #格式转换，评估
    base_lottery_list,parity_lottery_list,larsma_lottery_list = parase_lotterys(lotterys)

    purchase_number_list, beishu_number_list, purchase_number_list_str, beishu_number_list_str = evaluation(parity_lottery_list)

    return lottery_id, purchase_number_list, beishu_number_list, purchase_number_list_str, beishu_number_list_str



#格式转换
def parase_lotterys(lottery):
    # print lottery
    #定义行列矩阵,179行，10列，基础数组，原始数据
    base_lottery_list = [[0 for i in range(10)] for i in range(len(lottery))]
    #定义行列矩阵,179行，10列，奇偶数组，1表示奇，0表示偶
    parity_lottery_list = [[0 for i in range(10)] for i in range(len(lottery))]
    #定义行列矩阵,179行，10列，大小数组,1表示大，0表示小
    larsma_lottery_list = [[0 for i in range(10)] for i in range(len(lottery))]
    count = 0
    for loty in lottery:
        # print loty.lottery_number
        temp_lotys = loty.lottery_number.split(',')
        # print temp_lotys
        # print count,len(lottery)
        for i in range(len(temp_lotys)):
            sub_num = int(temp_lotys[i])
            base_lottery_list[len(lottery) - count - 1][i] = sub_num
            if (sub_num%2 == 1):
                parity_lottery_list[len(lottery) -1 - count][i] = 1
            if (sub_num > 5):
                larsma_lottery_list[len(lottery) -1 - count][i] = 1
        count = count + 1
    tran_base_lottery_list = map(list, zip(*base_lottery_list))

    return base_lottery_list,parity_lottery_list,larsma_lottery_list



def evaluation(parity_lottery_list):
    print "evaluation..."

    tran_parity_lottery_list = map(list, zip(*parity_lottery_list))
    total_prob_value = [[]] * 10
    predict_number_list = []
    beishu_number_list = []
    predict_number_list_str = ''
    beishu_number_list_str = ''
    for i in range(10):
        #第几名即 第几列写入prob_range
        prob_range = '第' + str(i+1) + '名'
        if 1:
            #填充规则数据
            target = tran_parity_lottery_list[i]
            prob_value = [0] * len(target)
            # print 'odd or even'
            #pk_logger.info("名次:%d",i+1)
            # result, predict_number, beishu_number = compute_rule110111011101(target, prob_value)
            result, predict_number, beishu_number = compute_rule1010(target, prob_value)
            predict_number_list.append(predict_number)
            predict_number_list_str = predict_number_list_str + str(predict_number) + ','
            beishu_number_list.append(beishu_number)
            beishu_number_list_str = beishu_number_list_str + str(beishu_number) + ','
            total_prob_value.append(prob_value)
    return predict_number_list, beishu_number_list, predict_number_list_str[:-1], beishu_number_list_str[:-1]



def compute_rule1010(target, prob_value):
    count = 0

    rule0 = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    rule1 = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    # rule0 = [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]
    # rule1 = [1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1]
    input_beishu = [0,0,0,0,0,0,1,2,4,8,16,33,68,138]
    index = 0
    max = len(target)
    hit_not_count = 0
    # input_beishu = [0,0,0,0,1,2,4,8,16,32,64,128]
    rule = rule0
    last_purchase_num = 0
    purchase_number = []
    index_list = []
    predict_list = []
    beishu_list = []
    while(count < max):
        #print target[count]
        #等于0的时候初始化规则
        # print "========================================="
        if count == 0:
            # print "本期:",target[count]
            if target[0] == 0:
                rule = rule0
                last_purchase_num = 1
                predict_list.append(0)
            else:
                rule = rule1
                last_purchase_num = 0
                predict_list.append(1)
            purchase_number.append("X")
            index_list.append("X")
        else:
            # print "上期:",target[count-1]," last_purchase_num:",last_purchase_num
            #如果上期未中  本期更新规则
            if index == 0:
                # if target[count-1] == 0 and last_purchase_num == 1:
                #     rule = rule0
                # if target[count-1] == 1 and last_purchase_num == 0:
                #     rule = rule1
                if target[count-1] == 0:
                    rule = rule0
                if target[count-1] == 1:
                    rule = rule1

            #根据规则判断本期盈利状态
            last_purchase_num = rule[index]
            index_list.append(index)
            # print "target",target[count]," index:",index, "rule:",rule
            if target[count] != rule[index]:
                index = (index + 1)
                if index == 13:
                    index = 0
                prob_value[count] = -1 * input_beishu[hit_not_count]
                hit_not_count = hit_not_count + 1
                if hit_not_count == 13:
                    hit_not_count = 0

            else:
                index = 0
                prob_value[count] = 0.95 * input_beishu[hit_not_count]
                hit_not_count = 0

            if index == 0:
                if target[count-1] == 0:
                    rule = rule0
                if target[count-1] == 1:
                    rule = rule1
            predict_list.append(rule[index])
            beishu_list.append(input_beishu[hit_not_count])
            purchase_number.append(last_purchase_num)

        count = count + 1
    # print "开奖号码  :",target
    # print "预测号码:",purchase_number
    pk_logger.info("predict:%s",str(predict_list))
    pk_logger.info("beishu:%s",str(beishu_list))
    if len(beishu_list) == 0:
        beishu_list.append(0)
    # print "index_list:" , index_list
    return prob_value, predict_list[-1], beishu_list[-1]



def compute_rule11111(target, prob_value):
    count = 0

    rule0 = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
    rule1 = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    # rule0 = [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]
    # rule1 = [1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1]
    input_beishu = [0,0,0,0,0,1,2,4,8,16,33,68,138]

    index = 0
    max = len(target)
    hit_not_count = 0
    # input_beishu = [0,0,0,0,1,2,4,8,16,32,64,128]
    rule = rule0
    last_purchase_num = 0
    purchase_number = []
    index_list = []
    predict_list = []
    beishu_list = []
    while(count < max):
        #print target[count]
        #等于0的时候初始化规则
        # print "========================================="
        if count == 0:
            # print "本期:",target[count]
            if target[0] == 0:
                rule = rule0
                last_purchase_num = 1
                predict_list.append(0)
            else:
                rule = rule1
                last_purchase_num = 0
                predict_list.append(1)
            purchase_number.append("X")
            index_list.append("X")
        else:
            # print "上期:",target[count-1]," last_purchase_num:",last_purchase_num
            #如果上期未中  本期更新规则
            if index == 0:
                # if target[count-1] == 0 and last_purchase_num == 1:
                #     rule = rule0
                # if target[count-1] == 1 and last_purchase_num == 0:
                #     rule = rule1
                if target[count-1] == 0:
                    rule = rule0
                if target[count-1] == 1:
                    rule = rule1

            #根据规则判断本期盈利状态
            last_purchase_num = rule[index]
            index_list.append(index)
            # print "target",target[count]," index:",index, "rule:",rule
            if target[count] != rule[index]:
                index = (index + 1)
                if index == 13:
                    index = 0
                prob_value[count] = -1 * input_beishu[hit_not_count]
                hit_not_count = hit_not_count + 1
                if hit_not_count == 13:
                    hit_not_count = 0

            else:
                index = 0
                prob_value[count] = 0.95 * input_beishu[hit_not_count]
                hit_not_count = 0

            if index == 0:
                if target[count-1] == 0:
                    rule = rule0
                if target[count-1] == 1:
                    rule = rule1
            predict_list.append(rule[index])
            beishu_list.append(input_beishu[hit_not_count])
            purchase_number.append(last_purchase_num)

        count = count + 1
    # print "开奖号码  :",target
    # print "预测号码:",purchase_number
    pk_logger.info("predict:%s",str(predict_list))
    pk_logger.info("beishu:%s",str(beishu_list))
    # print "index_list:" , index_list
    return prob_value, predict_list[-1], beishu_list[-1]



def compute_rule1010_test(target, prob_value):
    count = 0

    rule0 = [ 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    rule1 = [ 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    # rule0 = [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]
    # rule1 = [1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1]
    input_beishu = [0,0,1,2,3,4,5,6,7,8]
    index = 0
    max = len(target)
    hit_not_count = 0
    # input_beishu = [0,0,0,0,1,2,4,8,16,32,64,128]
    rule = rule0
    last_purchase_num = 0
    purchase_number = []
    index_list = []
    predict_list = []
    beishu_list = []
    while(count < max):
        #print target[count]
        #等于0的时候初始化规则
        # print "========================================="
        if count == 0:
            # print "本期:",target[count]
            if target[0] == 0:
                rule = rule0
                last_purchase_num = 1
                predict_list.append(0)
            else:
                rule = rule1
                last_purchase_num = 0
                predict_list.append(1)
            purchase_number.append("X")
            index_list.append("X")
        else:
            # print "上期:",target[count-1]," last_purchase_num:",last_purchase_num
            #如果上期未中  本期更新规则
            if index == 0:
                # if target[count-1] == 0 and last_purchase_num == 1:
                #     rule = rule0
                # if target[count-1] == 1 and last_purchase_num == 0:
                #     rule = rule1
                if target[count-1] == 0:
                    rule = rule0
                if target[count-1] == 1:
                    rule = rule1

            #根据规则判断本期盈利状态
            last_purchase_num = rule[index]
            index_list.append(index)
            # print "target",target[count]," index:",index, "rule:",rule
            if target[count] != rule[index]:
                index = (index + 1)
                if index == 10:
                    index = 0
                prob_value[count] = -1 * input_beishu[hit_not_count]
                hit_not_count = hit_not_count + 1
                if hit_not_count == 10:
                    hit_not_count = 0

            else:
                index = 0
                prob_value[count] = 0.95 * input_beishu[hit_not_count]
                hit_not_count = 0

            if index == 0:
                if target[count-1] == 0:
                    rule = rule0
                if target[count-1] == 1:
                    rule = rule1
            predict_list.append(rule[index])
            beishu_list.append(input_beishu[hit_not_count])
            purchase_number.append(last_purchase_num)

        count = count + 1
    # print "开奖号码  :",target
    # print "预测号码:",purchase_number
    # print "predict:",predict_list
    # print "beishu:",beishu_list
    return prob_value, predict_list[-1], beishu_list[-1]
