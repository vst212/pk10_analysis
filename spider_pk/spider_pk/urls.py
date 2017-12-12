#coding=utf-8
"""spider_pk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from prob.views import index,admin
from prob.views_month import admin_month,index_month,index_month_evaluation
import prob.views_times
import prob.views_month_times

######################
import cross.cross_day
import cross.cross_month



urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    ##########################################V8版本#####################################
    url(r'^admin/$', admin),
    url(r'^index/$', index),


    url(r'^admin_month/$', admin_month),
    url(r'^index_month/$', index_month),
    url(r'^index_month_evaluation/$', index_month_evaluation),

    url(r'^admin_times/$', prob.views_times.admin),
    url(r'^index_times/$', prob.views_times.index),
    # url(r'^index_month_times/$', index_month),
    url(r'^admin_month_times/$', prob.views_month_times.admin_month_times),
    url(r'^index_month_times/$', prob.views_month_times.index_month_times),
    url(r'^index_month_times_evaluation/$', prob.views_month_times.index_month_times_evaluation),
    ########################################V9版本  交叉分析与直线分析###########################################
    url(r'^cross_day_admin/$', cross.cross_day.admin),
    url(r'^cross_day_index/$', cross.cross_day.index),

    url(r'^cross_month_admin/$', cross.cross_month.admin_month),
    url(r'^cross_month_index/$', cross.cross_month.index_month),
    url(r'^cross_month_evaluation/$', cross.cross_month.index_month_evaluation),

]
