#coding=utf-8
__author__ = 'shifeixiang'

# from __future__ import unicode_literals

from selenium import webdriver
import time

from pkten_log.pk_log import PkLog

pk_logger = PkLog('append_purchase_lide.purchase_driver').log()

def get_driver(username,password):
    # chromedriver = "E:\\python\\webdriver\\chrome\\chromedriver37.exe"
    # options = webdriver.ChromeOptions()
    # options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
    # driver = webdriver.Chrome(executable_path=chromedriver,chrome_options=options )
    driver = webdriver.Firefox(executable_path = 'E:\\python\\webdriver\\firefox\\geckodriver.exe')

    driver.get("http://mem5.tfnvhg606.lexinsoft.com/")
    # driver.find_element_by_class_name()
    # driver.get("http://pxiagme1.lot1068.net/member/fouvrh5q0rhl2edlk9m7jong3e/Welcome.action")
    driver.maximize_window();
    time.sleep(2)


    #user_elem = driver.find_element_by_name("account")
    user_elem = driver.find_element_by_id("loginName")
    # user_elem.send_keys("abab2233")
    user_elem.send_keys(username)

    #pwd_elem = driver.find_element_by_name("password")
    pwd_elem = driver.find_element_by_id("loginPwd")
    # pwd_elem.send_keys("ABCd1234")
    pwd_elem.send_keys(password)

    code_flag = True
    while(code_flag):
        try:
            # elem.send_keys(Keys.RETURN)
            #密码输入完毕后提供5s时间输入验证码
            time.sleep(1)
            #提交按钮
            #button = driver.find_element_by_class_name("control")
            button = driver.find_element_by_id("login_btn")
            #button = driver.find_element_by_xpath('/html/body/div[2]/div/div/form/div[6]/input')
            button.click()
            time.sleep(2)

            try:
                notice = driver.find_element_by_xpath('//*[@id="myLayer_19841012"]/tbody/tr/td/div[1]/a')
                notice.click()
                time.sleep(2)
                pk_logger.info("click notice ok")
            except:
                pk_logger.warn("no notice or click notice error!")

            agree = driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/input[2]')
            agree.click()
            time.sleep(1)
            pk_logger.info("click agree ok")
            code_flag = False
        except:
            driver.quit()
            #print "please input code!"
            pk_logger.warn("登录异常，重新登录")
            time.sleep(5)
            # chromedriver = "E:\\python\\webdriver\\chrome\\chromedriver37.exe"
            # options = webdriver.ChromeOptions()
            # options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
            # driver = webdriver.Chrome(executable_path=chromedriver,chrome_options=options )

            driver = webdriver.Firefox(executable_path = 'E:\\python\\webdriver\\firefox\\geckodriver.exe')
            driver.get("http://mem4.bbafon311.lbjthg.com/")
            driver.maximize_window();
            time.sleep(2)

            user_elem = driver.find_element_by_id("loginName")
            user_elem.send_keys(username)

            pwd_elem = driver.find_element_by_id("loginPwd")
            pwd_elem.send_keys(password)
            code_flag = True
    # driver.get("http://pxiagme1.lot1068.net/member/pvn70lug1fsv2r3vng7cn049en/Home/Index.action")
    time.sleep(2)
    #跳转到top框架，获取北京10
    # driver.switch_to_frame("topFrame")
    # print "top frameset1"
    # time.sleep(1)

    try:
        #点击菜单
        menu = driver.find_element_by_id('menuText')
        menu.click()
        time.sleep(2)
        pk_logger.info("click menu ok")

        driver.find_element_by_link_text('北京賽車(PK10)').click()
        time.sleep(2)
        pk_logger.info("click pk10 ok")


        # menu_element = driver.find_element_by_link_text(u'廣東快樂十分')
        # time.sleep(2)
        # pk_logger.info("click menu ok")
        # webdriver.ActionChains(driver).move_to_element(menu_element).perform()
        # time.sleep(2)
        # driver.find_element_by_link_text(u'北京賽車(PK10)').click()
        # time.sleep(2)
        # pk_logger.info("click pk10 ok")

        #pk10
        # pk10 = driver.find_element_by_xpath('//*[@id="l_BJPK10"]/span')
        # pk10.click()
        # time.sleep(1)

        #切换frame
        # 'mainIframe'
        driver.switch_to_frame("mainIframe")
        time.sleep(2)
        pk_logger.info("switch mainFrame ok")

        # 1-10
        element_1_10 = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[1]/div[1]/div/div[1]/ul/li[2]/a')
        element_1_10.click()
        time.sleep(3)
        pk_logger.info("click 1-10 ok")
    except:
        pk_logger.error("login error, relogin")
        driver.quit()
        time.sleep(3)
        get_driver(username,password)

    return driver

