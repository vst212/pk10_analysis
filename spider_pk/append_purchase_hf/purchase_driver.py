#coding=utf-8
__author__ = 'shifeixiang'

# from __future__ import unicode_literals

from selenium import webdriver
import time

from pkten_log.pk_log import PkLog

pk_logger = PkLog('append_purchase_hf.purchase_driver').log()

def get_driver(username,password):
    chromedriver = "./pkten_log/chromedriver37.exe"
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
    driver = webdriver.Chrome(executable_path=chromedriver,chrome_options=options )
    # driver = webdriver.Firefox(executable_path = 'E:\\python\\webdriver\\firefox\\geckodriver.exe')

    # driver.get("http://92.hf666.net/login_page.jsp?p=QWERTYUNjI0MTc1OTM1MT14ZWRuaV84ODhmciZuYz1YR05BTCY4ODhmcj1scHQmPWhy")
    driver.get("http://96.m1888.net/login_page.jsp?p=QWERTYUMjA4NDcxMDQ1MT14ZWRuaV84NjFvcyZuYz1YR05BTCY4NjFvcz1scHQmPWhy")
    # driver.find_element_by_class_name()
    # driver.get("http://pxiagme1.lot1068.net/member/fouvrh5q0rhl2edlk9m7jong3e/Welcome.action")
    driver.maximize_window();
    time.sleep(5)

    # driver.switch_to.frame(driver.find_element_by_xpath('/html/frameset/frame'))
    try:
        driver.switch_to.frame("mem_index")
        #driver.find_element_by_xpath('/html/frameset/frame')
        time.sleep(2)
    except:
        pk_logger.error("login error, relogin")
        driver.quit()
        time.sleep(3)
        get_driver(username,password)

    #user_elem = driver.find_element_by_name("account")
    user_elem = driver.find_element_by_id("Account")
    # user_elem.send_keys("abab2233")
    user_elem.send_keys(username)

    #pwd_elem = driver.find_element_by_name("password")
    pwd_elem = driver.find_element_by_id("PassWD")
    # pwd_elem.send_keys("ABCd1234")
    pwd_elem.send_keys(password)

    code_flag = True
    while(code_flag):
        try:
            # elem.send_keys(Keys.RETURN)
            #密码输入完毕后提供5s时间输入验证码
            time.sleep(1)
            #提交按钮
            # button = driver.find_element_by_class_name("btn1")

            button = driver.find_element_by_xpath('/html/body/form/div[1]/div/div[1]/div/div/ul/div[4]')
            button.click()
            time.sleep(2)

            # try:
            #     notice = driver.find_element_by_xpath('//*[@id="myLayer_19841012"]/tbody/tr/td/div[1]/a')
            #     notice.click()
            #     time.sleep(2)
            #     pk_logger.info("click notice ok")
            # except:
            #     pk_logger.warn("no notice or click notice error!")

            # agree = driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/input[2]')
            agree = driver.find_element_by_class_name('agree-bouttn-nextpage')
            agree.click()
            time.sleep(1)
            pk_logger.info("click agree ok")
            code_flag = False
        except:
            driver.quit()
            #print "please input code!"
            pk_logger.warn("登录异常，重新登录")
            time.sleep(5)
            chromedriver = "E:\\python\\webdriver\\chrome\\chromedriver37.exe"
            options = webdriver.ChromeOptions()
            options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
            driver = webdriver.Chrome(executable_path=chromedriver,chrome_options=options )

            # driver = webdriver.Firefox(executable_path = 'E:\\python\\webdriver\\firefox\\geckodriver.exe')
            driver.get("http://92.hf666.net/login_page.jsp?p=QWERTYUNjI0MTc1OTM1MT14ZWRuaV84ODhmciZuYz1YR05BTCY4ODhmcj1scHQmPWhy")
            driver.maximize_window();
            time.sleep(2)

            driver.switch_to.frame("mem_index")
            #driver.find_element_by_xpath('/html/frameset/frame')
            time.sleep(2)

            user_elem = driver.find_element_by_id("Account")
            user_elem.send_keys(username)

            pwd_elem = driver.find_element_by_id("PassWD")
            pwd_elem.send_keys(password)
            code_flag = True
    # driver.get("http://pxiagme1.lot1068.net/member/pvn70lug1fsv2r3vng7cn049en/Home/Index.action")
    time.sleep(2)
    #跳转到top框架，获取北京10
    # driver.switch_to_frame("topFrame")
    # print "top frameset1"
    # time.sleep(1)

    try:
        driver.find_element_by_id('toclose').click()
        time.sleep(2)
        pk_logger.info("close ad!")

        driver.switch_to.frame("mainFrame")
        time.sleep(2)
        pk_logger.info("switch  mainFrame ok !")

        #pk10
        driver.find_element_by_xpath('//*[@id="gametable"]/table/tbody/tr[4]/td[2]/a[1]').click()
        #driver.find_element_by_id('game_table24').click()
        time.sleep(2)
        pk_logger.info("click pk10!")

        driver.switch_to.default_content()
        pk_logger.info("switch  default ok !")
        time.sleep(2)

        #子服务控制开始
        #点击菜单
        # driver.switch_to.frame("mem_index")
        # time.sleep(1)
        # pk_logger.info("switch  mem_index ok !")
        # driver.switch_to.frame("mainFrame")
        # time.sleep(1)
        # pk_logger.info("switch  mainFrame ok !")
        # driver.switch_to.frame("IndexFrame")
        # time.sleep(1)
        # pk_logger.info("switch IndexFrame ok !")
        #
        # menu = driver.find_element_by_xpath('//*[@id="NUMERIC"]')
        # menu.click()
        # time.sleep(2)
        # pk_logger.info("click NUMERIC ok")
        #
        # xpath = '//*[@id="NUM-N0102-TD2"]/input'
        # driver.find_element_by_xpath(xpath).send_keys('2')
        # pk_logger.info("send keys ok.....")
        #
        # confirm_button = driver.find_element_by_xpath('//*[@id="BetType-NUMERIC"]/div/input[2]')
        # confirm_button.click()
        # time.sleep(2)
        # pk_logger.info("commit ok")
        #
        # driver.find_element_by_xpath('//*[@id="submitbtn"]').click()
        # pk_logger.info("confirm ok")
        # time.sleep(10)

    except:
        pk_logger.error("login error, relogin")
        driver.quit()
        time.sleep(3)
        get_driver(username,password)

    return driver

