#coding=utf-8
__author__ = 'shifeixiang'
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


def get_driver(username,password):
    chromedriver = "E:\\python\\webdriver\\chrome\\chromedriver37.exe"
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
    driver = webdriver.Chrome(executable_path=chromedriver,chrome_options=options )

    #driver  = webdriver.PhantomJS('E:\\python\\webdriver\\phantomjs\\phantomjs')

    # driver.get("http://pxiagme1.lot1068.net/member/Welcome.action?searchKeyword=99935")
    driver.get('http://pxkagme1.lot1068.net:8082/member/Welcome.action?searchKeyword=99935')
    # driver.get('http://pxsagme1.lot1068.net:8082/member/Welcome.action?searchKeyword=99935')
    #driver.get('http://pxiagme1.lot1068.net/member/b56f0ov1vhtqptofg9530s939a/Welcome.action')
    # driver.get("http://pxiagme1.lot1068.net/member/fouvrh5q0rhl2edlk9m7jong3e/Welcome.action")
    driver.maximize_window();
    user_elem = driver.find_element_by_name("userCode")
    #user_elem.send_keys("abab2233")
    user_elem.send_keys(username)
    code_flag = True
    while(code_flag):
        try:
            pwd_elem = driver.find_element_by_name("password")
            # pwd_elem.send_keys("ABCd1234")
            pwd_elem.send_keys(password)
            # elem.send_keys(Keys.RETURN)
            #密码输入完毕后提供5s时间输入验证码
            time.sleep(10)
            #提交按钮

            js = "var q=document.documentElement.scrollTop=500"
            driver.execute_script(js)
            time.sleep(2)

            button = driver.find_element_by_xpath('//*[@id="loginForm"]/button')
            #button = driver.find_element_by_xpath('//*[@id="loginForm"]/div[2]/table/tbody/tr[5]/td[2]/input')
            button.click()
            time.sleep(2)

            agree = driver.find_element_by_xpath('/html/body/div/div/a[1]')
            agree.click()
            time.sleep(2)
            code_flag = False
        except:
            print "please input code!"
            time.sleep(5)
            code_flag = True
    # driver.get("http://pxiagme1.lot1068.net/member/pvn70lug1fsv2r3vng7cn049en/Home/Index.action")
    time.sleep(1)
    #跳转到top框架，获取北京10
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


    continue_flag = True
    while(continue_flag):
        try:
            for i in range(3):
                xpath = '//*[@id="itmStakeInput20' + str(i+1) + '201"]'
                #第一名 big
                input_1_big = driver.find_element_by_xpath(xpath)
                input_1_big.send_keys(10-i)
                time.sleep(3)
             #确认按钮
            confirm = driver.find_element_by_xpath('//*[@id="memberMainContent"]/div[2]/table/tbody/tr/td[2]/a[1]')
            confirm.click()
            time.sleep(3)
            #提交按钮
            submit = driver.find_element_by_xpath('//*[@id="betSlipDivContent"]/table/tbody/tr[2]/td/a[1]')
                                                  # '//*[@id="betSlipDivContent"]/table/tbody/tr[3]/td/a[1]'
                                                  # '//*[@id="betSlipDivContent"]/table/tbody/tr[2]/td/a[1]'
            submit.click()
            time.sleep(3)
        except:
            print "封盘中...请稍后..."
            time.sleep(10)
            continue_flag = True



def reload_pk10_url(driver):
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

