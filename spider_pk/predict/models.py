# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class KillPredict(models.Model):
    kill_predict_date = models.CharField(max_length=100)
    kill_predict_time = models.CharField(max_length=100)
    lottery_id =  models.IntegerField()
    kill_predict_number = models.CharField(max_length=200)
    lottery_number = models.CharField(max_length=200)
    predict_total = models.IntegerField(null=True, blank=True)
    target_total = models.IntegerField(null=True, blank=True)
    predict_accuracy = models.FloatField(null=True, blank=True)

class PredictLottery(models.Model):
    lottery_month = models.CharField(max_length=100)
    lottery_date = models.CharField(max_length=100)
    lottery_time = models.CharField(max_length=100)
    lottery_id =  models.IntegerField()
    lottery_number = models.CharField(max_length=500)

class KillPredictTotal(models.Model):
    kill_predict_date = models.CharField(max_length=100)
    kill_predict_time = models.CharField(max_length=100)
    lottery_id =  models.IntegerField(null=True, blank=True)
    kill_predict_number = models.CharField(max_length=200)
    lottery_number = models.CharField(max_length=200)
    predict_total = models.IntegerField(null=True, blank=True)
    target_total = models.IntegerField(null=True, blank=True)
    predict_accuracy = models.FloatField(null=True, blank=True)
    predict_column_number = models.IntegerField(null=True, blank=True)
    predict_column_desc = models.CharField(max_length=200)
