# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

#用户表
class ProbUser(models.Model):
    user_id =  models.IntegerField()
    user_name = models.CharField(max_length=30)    #主键
    user_password =  models.CharField(max_length=30)
    user_status = models.BooleanField()

class PurchaseRecord(models.Model):
    purchase_record_month = models.CharField(max_length=100)
    purchase_record_date = models.CharField(max_length=100)
    purchase_record_time = models.CharField(max_length=100)
    purchase_record_id =  models.IntegerField()
    purchase_record_lottery_number = models.CharField(max_length=500)
    #规则
    purchase_record_rule = models.CharField(max_length=100)
    #金额
    purchase_record_money = models.IntegerField()
    #第几列
    purchase_record_column = models.IntegerField()
    #购买的值
    purchase_record_value = models.IntegerField()

class FianceRecord(models.Model):
    fiance_record_month = models.CharField(max_length=100)
    fiance_record_date = models.CharField(max_length=100)
    fiance_record_time = models.CharField(max_length=100)
    fiance_record_id =  models.IntegerField()
    #开奖号码
    fiance_record_lottery_number = models.CharField(max_length=500)
    # 规则
    fiance_record_rule_id = models.CharField(max_length=100)
    #规则
    fiance_record_rule = models.CharField(max_length=100)
    #第几名
    purchase_record_column = models.CharField(max_length=100)
    #购买号码
    fiance_record_value = models.IntegerField()
    # 购买号码描述
    fiance_record_value_desc = models.CharField(max_length=100)
    #下注金额
    fiance_record_money = models.FloatField()
    #赔率
    fiance_record_odds = models.FloatField()
    #盈利
    fiance_record_profit = models.FloatField()
    #输赢
    fiance_lose_win = models.IntegerField()


class FianceRecordTotal(models.Model):
    fiance_record_month = models.CharField(max_length=100)
    fiance_record_date = models.CharField(max_length=100)
    fiance_record_time = models.CharField(max_length=100)
    fiance_record_id =  models.IntegerField()
    #开奖号码
    fiance_record_lottery_number = models.CharField(max_length=500)
    # 规则
    fiance_record_rule_id = models.CharField(max_length=100)
    #规则
    fiance_record_rule = models.CharField(max_length=100)
    #第几名
    fiance_record_column = models.CharField(max_length=100)
    #购买号码
    fiance_record_value = models.IntegerField()
    # 购买号码描述
    fiance_record_value_desc = models.CharField(max_length=100)
    #下注金额
    fiance_record_money = models.FloatField()
    #赔率
    fiance_record_odds = models.FloatField()
    #盈利
    fiance_record_profit_all = models.FloatField()
    #输赢
    fiance_lose_win = models.IntegerField()


