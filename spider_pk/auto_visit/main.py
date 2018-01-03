# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.shortcuts import render_to_response
# Create your views here.
def auto_admin(request):
    # ProbTotals.objects.all().delete()

    return render_to_response('auto_main.html')