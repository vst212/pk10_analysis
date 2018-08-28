#coding=utf-8
__author__ = 'shifeixiang'

import urllib2
import time
import simplejson
from append_predict_sandd.models import PredictLottery

from pkten_log.pk_log import PkLog

pk_logger = PkLog('append_predict_sandd.spider_pk10').log()

def get_html_result():
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    #就接口
    # url = "http://api.api68.com/pks/getPksHistoryList.do?date=" + current_date + "&lotCode=10001"
    flag = True
    count = 0
    while(flag):
        try:
            if count%2 == 1:
                url = "http://e.apiplus.net/daily.do?token=t3cffb3f43eb3c9b1k&code=bjpk10&format=json&date=" + current_date
            else:
                url = "http://z.apiplus.net/daily.do?token=t3cffb3f43eb3c9b1k&code=bjpk10&format=json&date=" + current_date
            print url
            pk_logger.info("url:%s",url)
            req = urllib2.Request(url = url, headers = headers)
            page = urllib2.urlopen(req, timeout=15)
                # page = urllib2.urlopen(url)
            html = page.read()
            # print html

            html_json = simplejson.loads(html)
            return html_json
        except:
            #if count > 2:
                #flag = False
            #print 'spider pay interface faild! please exit process......  over purchase!!!'
            pk_logger.error( 'spider pay interface faild! please exit process......  over purchase!!!')
            time.sleep(15)
        count = count + 1
    return ''


def load_lottery_predict(html_json):
    current_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    PredictLottery.objects.filter(lottery_date=current_date).delete()
    for i in range(len(html_json['data'])):
        lottery_month = html_json['data'][i]['opentime'][0:7]
        lottery_date = html_json['data'][i]['opentime'][0:10]
        lottery_time = html_json['data'][i]['opentime']
        lottery_id = html_json['data'][i]['expect']
        lottery_number = html_json['data'][i]['opencode']

        p = PredictLottery(lottery_month=lottery_month, lottery_date =lottery_date, lottery_time = lottery_time, lottery_id = lottery_id, lottery_number = lottery_number)
        p.save()

def get_lottery_id_number(lottery_id):
    try:
        lottery = PredictLottery.objects.get(lottery_id=lottery_id)
        return lottery.lottery_number, lottery.lottery_time
    except:
        return 0,'0'

def get_date_lottery(lottery_date):
    lotterys = PredictLottery.objects.filter(lottery_date = lottery_date)
    for lottery in lotterys:
        print lottery.lottery_id, lottery.lottery_number
