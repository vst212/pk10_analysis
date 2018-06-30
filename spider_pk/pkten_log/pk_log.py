#coding=utf-8
__author__ = 'shifeixiang'
import logging
import time

base_date = time.strftime("%Y%m%d", time.localtime())
# 创建一个logger

class PkLog:
    pk_name = ''
    def __init__(self,pk_name):
        PkLog.pk_name = pk_name

    def log(self):
        logger = logging.getLogger(self.pk_name)
        logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler('./pkten_log/log_file/' + base_date + '_pk10.log')
        fh.setLevel(logging.DEBUG)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger