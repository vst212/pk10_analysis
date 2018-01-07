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