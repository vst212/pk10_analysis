#coding=utf-8
__author__ = 'shifeixiang'

from selenium import webdriver
import time

from pkten_log.pk_log import PkLog

pk_logger = PkLog('append_purchase_jinsha.purchase_driver').log()
#'//*[@id="username"]'

def get_driver(username,password):
    #谷歌浏览器
    # chromedriver = "E:\\python\\webdriver\\chrome\\chromedriver37.exe"
    # options = webdriver.ChromeOptions()
    # options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
    # driver = webdriver.Chrome(executable_path=chromedriver,chrome_options=options )

    #火狐浏览器
    driver = webdriver.Firefox(executable_path = 'E:\\python\\webdriver\\firefox\\geckodriver.exe')

    driver.get('http://www.ag888xjs.net/Common/Index/login.html')

    driver.maximize_window();
    user_elem = driver.find_element_by_name("username")
    user_elem.send_keys(username)
    code_flag = True
    while(code_flag):
        if 1:
            pwd_elem = driver.find_element_by_name("pwd")
            pwd_elem.send_keys(password)
            #密码输入完毕后提供5s时间输入验证码
            time.sleep(10)
            #提交按钮

            js = "var q=document.documentElement.scrollTop=500"
            driver.execute_script(js)
            time.sleep(2)

            #button = driver.find_element_by_id('submit')
            #'//*[@id="submit"]'
            button = driver.find_element_by_xpath('//*[@id="submit"]')
            button.click()
            time.sleep(10)
            #不同意
            #'/html/body/div[1]/div[3]/div[2]/button[1]'

            #同意
            #'/html/body/div[1]/div[3]/div[2]/button[2]'
            #agree = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[2]/button[2]')
            #driver.find_element_by_link_text('')
            agrees = driver.find_elements_by_class_name('btn_agree')
            agree_count = 0
            for agree in agrees:
                if agree_count == 1:
                    pk_logger.info("click agree")
                    agree.click()
                    break
                else:
                    pass
                agree_count = agree_count + 1
            # agrees = driver.find_element_by_class_name('btn_agree')
            # agree.click()
            time.sleep(2)
            code_flag = False
        else:
            pk_logger.info("please input code!")
            time.sleep(5)
            code_flag = True

    time.sleep(1)
    #关闭提示
    try:
        pk_logger.info("click notice!")
        driver.find_element_by_class_name('xubox_setwin').click()
        time.sleep(2)
    except:
        pk_logger.info("not found xubox_setwin notice!")

    #世界杯弹窗
    #'btn_close_pop'
    try:
        driver.switch_to_frame('xubox_iframe1')
        time.sleep(2)
        pk_logger.info("click notice bool!")
        driver.find_element_by_id('btn_close_pop').click()
        time.sleep(2)
        driver.switch_to_default_content()
    except:
        pk_logger.info("not found btn_close_pop notice!")
    #pk10
    try:
        pk10 = driver.find_element_by_id('countdown_lt_3')
        pk10.click()
        time.sleep(2)
    except:
        pk_logger.error("not found PK10 link!")

    pk_logger.info("current_url:%s",driver.current_url)
    #print "current_url:",driver.current_url
    time.sleep(10)
    return driver

# def reload_pk10_url(driver):
#     #重新加载
#     pk_logger.info("reload pk10,url:%s",driver.current_url)
#     driver.get(driver.current_url)
#     return driver

