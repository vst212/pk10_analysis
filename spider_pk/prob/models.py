# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Lottery(models.Model):
    lottery_date = models.CharField(max_length=100)
    lottery_time = models.CharField(max_length=100)
    lottery_id =  models.IntegerField()
    lottery_number = models.CharField(max_length=500)

class Probs(models.Model):
    prob_range = models.CharField(max_length=100)
    prob_rule = models.CharField(max_length=100)
    prob_match =  models.IntegerField()
    prob_nomatch = models.IntegerField()
    prob_bet =  models.IntegerField()

    prob_amount = models.IntegerField()

    prob_win = models.FloatField()
    prob_lose = models.FloatField()
    prob_gain = models.FloatField()

class ProbTotals(models.Model):
    probtotal_rule = models.CharField(max_length=100)

    probtotal_match = models.IntegerField()
    probtotal_nomatch = models.IntegerField()
    probtotal_bet = models.IntegerField()

    probtotal_amount = models.FloatField()
    probtotal_win = models.FloatField()
    probtotal_lose = models.FloatField()
    probtotal_gain = models.FloatField()


class LotteryMonth(models.Model):
    lottery_month = models.CharField(max_length=100)
    lottery_date = models.CharField(max_length=100)
    lottery_time = models.CharField(max_length=100)
    lottery_id =  models.IntegerField()
    lottery_number = models.CharField(max_length=500)

