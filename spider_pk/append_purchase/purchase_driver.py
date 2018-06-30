#coding=utf-8
__author__ = 'shifeixiang'

# from __future__ import unicode_literals

from selenium import webdriver
import time

from pkten_log.pk_log import PkLog

pk_logger = PkLog('append_purchase.purchase_driver').log()

def get_driver(username,password):
    # chromedriver = "E:\\python\\webdriver\\chrome\\chromedriver37.exe"
    # options = webdriver.ChromeOptions()
    # options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
    # driver = webdriver.Chrome(executable_path=chromedriver,chrome_options=options )
    driver = webdriver.Firefox(executable_path = 'E:\\python\\webdriver\\firefox\\geckodriver.exe')


    driver.get("https://7989674523-bdgj.qq168.ws/login")
    # driver.find_element_by_class_name()
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
            button = driver.find_element_by_class_name("control")
            #button = driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[6]/input')
            button.click()
            time.sleep(2)

            agree = driver.find_element_by_xpath('/html/body/div/div/ul/li[2]/div/ul/li[15]/div/span/a[2]')
            agree.click()
            time.sleep(1)
            code_flag = False
        except:
            driver.quit()
            #print "please input code!"
            pk_logger.warn("请输入验证码")
            time.sleep(5)
            # chromedriver = "E:\\python\\webdriver\\chrome\\chromedriver37.exe"
            # options = webdriver.ChromeOptions()
            # options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
            # driver = webdriver.Chrome(executable_path=chromedriver,chrome_options=options )

            driver = webdriver.Firefox(executable_path = 'E:\\python\\webdriver\\firefox\\geckodriver.exe')
            driver.get("https://7989674523-bdgj.qq168.ws/login")
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
        pk_logger.warn("unfound button1")
        #print "unfound button1"

    try:
        driver.find_element_by_xpath('//*[@id="notice_button2"]/a').click()
        time.sleep(1)
    except:
        pk_logger.warn("unfound button2")

    try:
        driver.find_element_by_xpath('//*[@id="notice_button3"]/a').click()
        time.sleep(1)
    except:
        pk_logger.warn("unfound button3")

    try:
        driver.find_element_by_xpath('//*[@id="notice_button4"]/a').click()
        time.sleep(1)
    except:
        pk_logger.warn("unfound button4")

    #pk10
    pk10 = driver.find_element_by_xpath('//*[@id="l_BJPK10"]/span')
    pk10.click()
    time.sleep(1)

    # 1-10
    element_1_10 = driver.find_element_by_xpath('//*[@id="sub_BJPK10"]/a[2]')
    element_1_10.click()
    time.sleep(1)

    #print driver.current_url

    return driver

