# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.shortcuts import render_to_response
from auto_visit.models import FianceRecord
# Create your views here.
import time
def auto_list(request):
    # ProbTotals.objects.all().delete()

    current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    obj_pro_fiance = FianceRecord.objects.filter(fiance_record_date=current_date)

    return render_to_response('auto_list.html',{"probs":obj_pro_fiance})