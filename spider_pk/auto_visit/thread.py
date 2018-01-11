#coding=utf-8
__author__ = 'shifeixiang'
import time
import thread
import threading
from auto_visit.driver import get_driver
import auto_visit.main
import datetime

class Spider(threading.Thread):
    # __metaclass__ = Singleton
    thread_stop = False
    thread_num = 0
    interval = {}
    behavior = None
    def run(self):
        self.behavior(self,self.thread_num,self.interval)
    def stop(self):
        self.thread_stop = True

class ThreadControl():
    thread_stop = False
    current_thread = {}
    def start(self,thread_num,interval):
        spider = Spider()
        spider.behavior = loaddata
        spider.thread_num = thread_num
        spider.interval = interval
        spider.start()
        self.current_thread[str(thread_num)] = spider
    #判断进程是否活跃
    def is_alive(self,thread_num):
        tt = self.current_thread[str(thread_num)]
        return tt.isAlive()
    #获取当前线程名称
    # def get_name(self):
    def stop(self,thread_num):
        print "stop"
        spider = self.current_thread[str(thread_num)]
        spider.stop()

def loaddata(c_thread,thread_num,interval):
    log_name_title = str(thread_num) + "_tencent_qzone_info_"
    base_date = time.strftime("%Y%m%d", time.localtime())
    print thread_num
    # driver = qzone_login()
    time.sleep(1)
    if 0 :
        return 0
    else:
        count = 0
        #初次启动开始购买---可以通过购买记录来初始化last_minute
        last_minute = -1
        while not c_thread.thread_stop:
            current_minute = (datetime.datetime.now()).minute
            # print "current_minute ",current_minute
            if current_minute<5 and last_minute> 0:
                last_minute = last_minute - 60
            if current_minute - last_minute > 3:
                judge_num = (current_minute%5)
                if judge_num>2 :
                    current_date = time.strftime("%Y%m%d %H:%m:%S", time.localtime())
                    print current_date," ",interval["money"], " ", interval["rule"]
                    print "start purchase"
                    auto_visit.main.auto_visit_commit(interval)
                    time.sleep(3)
                    # print "purchase finish"
                    last_minute = current_minute
                    # print "last_minute ",last_minute
                    #time.sleep(3)
                    count = count + 1
                else:
                    # print current_minute, " ", last_minute," wait open prob"
                    time.sleep(10)
            else:
                # print current_minute, " ", last_minute," current prob already purchase"
                time.sleep(10)

        # interval["driver"].close()
        # interval["driver"].quit()
        # auto_visit.main.auto_visit_commit(interval,0)

        # driver.quit()
        #数据库状态更新,根据线程名称
        # thread = ThreadQzoneInfo.objects.get(thread_name=thread_num)
        # thread.thread_status = 0
        # thread.save()

