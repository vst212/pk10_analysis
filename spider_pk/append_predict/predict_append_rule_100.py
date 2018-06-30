#coding=utf-8
__author__ = 'shifeixiang'


import time
from selenium import webdriver
from bs4 import BeautifulSoup
from append_predict.models import KillPredict

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pkten_log.pk_log import PkLog
pk_logger = PkLog('append_predict.predict_append_rule_100').log()
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
            pk_logger.error("get driver time out")
            driver.quit()
            time.sleep(10)



#获取10个名次的soup 列表
def get_soup_list(interval):

    count = 0
    flag = True

    while(flag):
        try:
            soup_list = []
            driver = interval["driver"]
            driver.get("https://www.1399p.com/pk10/shdd")

            try:
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME , "lotteryNumber")))
                time.sleep(1)
                #driver.maximize_window();
                # driver.manage().window().maximize();
                time.sleep(1)
                js = "var q=document.documentElement.scrollTop=300"
                driver.execute_script(js)
                #print "scroll finish!"
                #pk_logger.info("scroll finish!")

                #处理100期
                #print 'click select'
                #pk_logger.info("click select")
                driver.find_element_by_class_name('colorWorld_selectJtou').click()
                time.sleep(1)
                #print 'click 10'
                #driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div[1]/div/div/div/div/span[1]').click()
                #print 'click 100'
                #pk_logger.info("click 100")
                driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div[1]/div/div/div/div/span[4]').click()
                time.sleep(2)
                #处理完成

                for i in range(10):
                    #'/html/body/div[3]/div[2]/div/div/div[2]/div[2]/span[1]/span'
                    driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div[2]/div[2]/span[' + str(i+1) + ']/span').click()
                    time.sleep(4)
                    soup = BeautifulSoup(driver.page_source)
                    soup_list.append(soup)
                return soup_list
            except:
                pk_logger.error("get sub driver time out")
                #print "get sub driver time out"
                driver.quit()
                pk_logger.error("spider predict faild!")
                #print "spider predict faild!"
                time.sleep(3)
                interval["driver"] = spider_predict_selenium()
                if count > 2:
                    flag = False
        except:
            driver.quit()
            #print "spider predict faild!"
            pk_logger.error("spider predict faild!")
            time.sleep(3)
            interval["driver"] = spider_predict_selenium()
            if count > 2:
                flag = False
        count = count + 1

    return []

#基于一个名次soup 获取预测号码列表 ，杀号率列表，期号
def get_kill_purchase_list(soup):
    count = 1
    percent_list = []
    number_list = []
    number_str_all_list = []
    prev_number_list = []
    hit_number = 0
    for tr in soup.find(class_='lotteryPublic_tableBlock').find_all('tr'):
        if count == 1:
            p_percent = 0
            current_percent_all = 30
            for td in tr.find_all(class_='font_red'):
                if p_percent < 10:
                    value = float(str(td.string).strip().replace("%",""))
                    percent_list.append(value)

                if p_percent == 10:
                    current_percent_all = float(str(td.string).strip().replace("%",""))
                p_percent = p_percent + 1

        if count == 5:
            p_number = 0
            for td in tr.find_all('td'):
                if p_number == 0:
                    protty_id = td.string
                if p_number > 1 and p_number < 12:
                    value = int(td.string)
                    number_list.append(value)
                    number_str_all_list.append(str(value))
                p_number = p_number + 1
        #前一期
        if count == 6:
            p_number = 0
            for td in tr.find_all('td'):
                if p_number == 0:
                    pre_protty_id = td.string
                if p_number == 1:
                    hit_number = td.string
                if p_number > 1 and p_number < 12:
                    value = int(td.string)
                    prev_number_list.append(str(value))
                p_number = p_number + 1
        count = count + 1

    #无论是否全部杀号正确，都计算
    #kill_flag = True
    #用于判断是否通过全中过滤
    kill_all_flag = False
    #print "number_list:",number_list
    pk_logger.info("number_list: %s" , number_list)
    #print "last hit_number is:",hit_number,'  ',prev_number_list
    #未全部杀中
    if hit_number in prev_number_list:
        kill_all_flag = False
    #全部杀中
    else:
        kill_all_flag = True
    return protty_id,percent_list,number_list,number_str_all_list,kill_all_flag,current_percent_all



#基于一个名次soup 获取预测号码列表 ，杀号率列表，期号
def get_min_current_percent_all(soup):
    count = 1
    for tr in soup.find(class_='lotteryPublic_tableBlock').find_all('tr'):
        if count == 1:
            p_percent = 0
            for td in tr.find_all(class_='font_red'):
                if p_percent == 10:
                    current_percent_all = float(str(td.string).strip().replace("%",""))
                p_percent = p_percent + 1
            #print "current_percent_all:",current_percent_all
        count = count + 1

    return current_percent_all


#号码处理，排名前6的号码过滤，剩余的号码购买
def max_min_deal(percent_list,number_list, kill_list, purchase_list, current_percent_all):
    if current_percent_all < 45:
        last_number = list(set(number_list))
    # elif current_percent_all>= 40:
    #     #杀掉号码，取前6名作为杀号码
    #     for i in range(10):
    #         max_percent = max(percent_list)
    #         index = percent_list.index(max_percent)
    #         percent_list.remove(max_percent)
    #         number_value = number_list.pop(index)
    #         kill_list.append(number_value)
    #     #预留号码
    #     for i  in range(10):
    #         purchase_list.append(int(i+1))
    #     last_number = list(set(purchase_list) - set(kill_list))
    else:
        last_number = []

    number_str = ''
    if len(last_number)>0:
        count = 0
        for number in last_number:
            if count == len(last_number)-1:
                number_str = number_str + str(number)
            else:
                number_str = number_str + str(number) + '|'
            count = count + 1
        return number_str
    else:
        return '0'

#获取需要购买的号码列表，每一名次为一个小列表
def get_purchase_list(interval, last_purchase_hit, xiazhu_nums):

    soup_list = get_soup_list(interval)
    purchase_number_list = ''
    purchase_number_list_desc = ''
    predict_number_all_list = []
    protty_id = 0
    count = 0
    page_count_index = 1
    purchase_mingci_number = 1

    #获取最小的总百分比
    current_percent_all_min = 50
    current_percent_all_list = []
    for soup in soup_list:
        current_percent_all = get_min_current_percent_all(soup)
        current_percent_all_list.append(current_percent_all)
        #print "current_percent_all:",current_percent_all
        pk_logger.info("current_percent_all: %s" , current_percent_all)
        if current_percent_all_min > current_percent_all:
            current_percent_all_min = current_percent_all
    current_percent_all_list_str = str(current_percent_all_list)
    #print "current_percent_all_min:",current_percent_all_min
    pk_logger.info("current_percent_all_min: %s" , current_percent_all_min)
    #循环遍历，满足条件的提取出来
    for soup in soup_list:
        protty_id, percent_list,number_list,number_str_all_list,kill_all_flag,current_percent_all = get_kill_purchase_list(soup)
        current_number_all = "|".join(number_str_all_list)
        predict_number_all_list.append(current_number_all)
        kill_list = []
        purchase_list = []

        #上期命中情况
        if (last_purchase_hit):
            if current_percent_all == current_percent_all_min:
                #print "last hit"
                pk_logger.info("last hit")
                purchase_number = max_min_deal(percent_list, number_list, kill_list, purchase_list, current_percent_all)
                purchase_mingci_number = page_count_index
                current_percent_all_min = 0
            else:
                purchase_number = '0'
        #上期未命中情况
        else:
            #使用同一未中名次
            #if xiazhu_nums == page_count_index:
            #按照排名最小的取值
            if current_percent_all == current_percent_all_min:
                #print "last not hit"
                pk_logger.info("last not hit")
                purchase_number = max_min_deal(percent_list, number_list, kill_list, purchase_list, current_percent_all)
                purchase_mingci_number = page_count_index
                current_percent_all_min = 0
            else:
                purchase_number = '0'

        if count == len(soup_list) - 1:
            purchase_number_list = purchase_number_list + str(purchase_number)
            purchase_number_list_desc = purchase_number_list_desc +  '[' + str(purchase_number) + ']'
        else:
            purchase_number_list = purchase_number_list + str(purchase_number) + ','
            purchase_number_list_desc = purchase_number_list_desc + '[' + str(purchase_number) + ']---,'
        count = count + 1
        page_count_index = page_count_index + 1
    predict_number_all_list_str = ",".join(predict_number_all_list)

    return protty_id, purchase_number_list, purchase_number_list_desc, predict_number_all_list_str, current_percent_all_list_str, purchase_mingci_number

def get_last_number_predict_kill_result(protty_id,index):
    last_protty_id = int(protty_id) - 1
    try:
        p = KillPredict.objects.get(lottery_id=last_protty_id)
        number_all_list = p.predict_number_all.split(',')[index]
        number_hit = str(int(p.lottery_number.split(',')[index]))
        #print "number_hit,number_all_list ",number_hit,number_all_list
        pk_logger.info("number_hit:%s", number_hit)
        pk_logger.info("number_all_list:%s", number_all_list)
        if number_hit in number_all_list:
            # print "no kill all"
            return False
        else:
            # print "kill all"
            return True
    except:
        #print "kill error"
        pk_logger.info("kill error")
        return False

