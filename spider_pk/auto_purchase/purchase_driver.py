#coding=utf-8
__author__ = 'shifeixiang'

# from __future__ import unicode_literals

import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


def get_driver(username,password):
    chromedriver = "E:\\python\\webdriver\\chrome\\chromedriver37.exe"
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
    driver = webdriver.Chrome(executable_path=chromedriver,chrome_options=options )


    driver.get("https://7989674523-bdgj.qq168.ws/login")
    # driver.get("http://pxiagme1.lot1068.net/member/fouvrh5q0rhl2edlk9m7jong3e/Welcome.action")
    driver.maximize_window();
    time.sleep(2)


    user_elem = driver.find_element_by_name("account")
    # user_elem.send_keys("abab2233")
    user_elem.send_keys(username)

    pwd_elem = driver.find_element_by_name("password")
    # pwd_elem.send_keys("ABCd1234")
    pwd_elem.send_keys(password)

    code_flag = True
    while(code_flag):
        try:
            # elem.send_keys(Keys.RETURN)
            #密码输入完毕后提供5s时间输入验证码
            time.sleep(10)
            #提交按钮
            button = driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[4]/input')
            button.click()
            time.sleep(2)

            agree = driver.find_element_by_xpath('/html/body/div/div/ul/li[2]/div/ul/li[15]/div/span/a[2]')
            agree.click()
            time.sleep(1)
            code_flag = False
        except:
            driver.quit()
            print "please input code!"
            time.sleep(5)
            chromedriver = "E:\\python\\webdriver\\chrome\\chromedriver37.exe"
            options = webdriver.ChromeOptions()
            options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
            driver = webdriver.Chrome(executable_path=chromedriver,chrome_options=options )
            driver.get("https://7989674523-bdgj.qq168.ws/login")
            # driver.get("http://pxiagme1.lot1068.net/member/fouvrh5q0rhl2edlk9m7jong3e/Welcome.action")
            driver.maximize_window();
            time.sleep(2)

            user_elem = driver.find_element_by_name("account")
            user_elem.send_keys(username)

            pwd_elem = driver.find_element_by_name("password")
            pwd_elem.send_keys(password)
            code_flag = True
    # driver.get("http://pxiagme1.lot1068.net/member/pvn70lug1fsv2r3vng7cn049en/Home/Index.action")
    time.sleep(1)
    #跳转到top框架，获取北京10
    # driver.switch_to_frame("topFrame")
    # print "top frameset1"
    # time.sleep(1)

    #点击广告
    try:
        driver.find_element_by_xpath('//*[@id="notice_button1"]/a').click()
        time.sleep(1)
    except:
        print "unfound button1"

    try:
        driver.find_element_by_xpath('//*[@id="notice_button2"]/a').click()
        time.sleep(1)
    except:
        print "unfound button2"

    try:
        driver.find_element_by_xpath('//*[@id="notice_button3"]/a').click()
        time.sleep(1)
    except:
        print "unfound button3"

    try:
        driver.find_element_by_xpath('//*[@id="notice_button4"]/a').click()
        time.sleep(1)
    except:
        print "unfound button4"

    #pk10
    pk10 = driver.find_element_by_xpath('//*[@id="l_BJPK10"]/span')
    pk10.click()
    time.sleep(1)

    # 1-10
    element_1_10 = driver.find_element_by_xpath('//*[@id="sub_BJPK10"]/a[2]')
    element_1_10.click()
    time.sleep(1)

    print driver.current_url

    return driver

    driver.switch_to_frame("frame")
    time.sleep(2)

    input_1_big = driver.find_element_by_xpath('//*[@id="a_B1_2"]/input')
    input_1_big.send_keys(12)

    input_1_big = driver.find_element_by_xpath('//*[@id="a_B1_3"]/input')
    input_1_big.send_keys(12)

    input_1_big = driver.find_element_by_xpath('//*[@id="a_B2_1"]/input')
    input_1_big.send_keys(12)

    input_1_big = driver.find_element_by_xpath('//*[@id="header"]/div[2]/div/input[1]')
    input_1_big.click()
    time.sleep(1)

    #返回原始框架
    driver.switch_to_default_content()
    time.sleep(1)

    input_1_big = driver.find_element_by_xpath('/html/body/div[6]/div[3]/div/button[1]/span')
    input_1_big.click()
    time.sleep(10)

    return driver


    continue_flag = True

    '1-1://*[@id="a_B1_1"]/input'
    '1-2://*[@id="a_B1_2"]/input'
    '2-1://*[@id="a_B2_1"]/input'
    '3-6://*[@id="a_B3_6"]/input'

    '确定://*[@id="header"]/div[2]/div/input[1]'

    '弹窗确定：/html/body/div[6]/div[3]/div/button[1]/span'
