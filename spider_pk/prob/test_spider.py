#coding=utf-8
import urllib2
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
}

url = 'http://api.api68.com/pks/getPksHistoryList.do?date=2017-10-02&lotCode=10001'

req = urllib2.Request(url = url, headers = headers)
try:
    page = urllib2.urlopen(req,timeout = 10)
    print 'ok'
    html = page.read()
    print html
except:
    print 'TIME out.....'
    html = None
    # page = urllib2.urlopen(url)


if (html):
    print "1111"
    print html
else:
    print  "0000"
    print html