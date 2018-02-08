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
import predict.main
import predict.report

######################
import cross.cross_day
import cross.cross_month

########################
import auto_visit.main
import auto_visit.list




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

    ########################################v1.0版本，自动化####################################
    url(r'^auto_main/$', auto_visit.main.auto_admin),
    url(r'^control_probuser_thread/$', auto_visit.main.control_probuser_thread),
    # url(r'^stop_probuser_thread/$', auto_visit.main.stop_probuser_thread),
    url(r'^auto_list/$', auto_visit.list.auto_list),
    url(r'^auto_list_refresh/$', auto_visit.list.auto_list_refresh),

    url(r'^set_user/$', auto_visit.list.set_user),
    # url(r'^get_prob_data/$', auto_visit.main.get_prob_data),
    url(r'^get_purchase_data/$', auto_visit.main.get_purchase_data),
    url(r'^get_fiance_data/$', auto_visit.main.get_fiance_data),

    #######################################v1.1  ,预测###########################################
    url(r'^predict_main/$', predict.main.predict_main),
    url(r'^control_predict_thread/$', predict.main.control_predict_thread),
    url(r'^predict_report/$', predict.report.predict_report),
    url(r'^control_predict_report/$', predict.report.control_predict_report),
    #测试
    url(r'^set_predict/$', predict.main.set_predict),
    # url(r'^get_predict/$', predict.main.get_predict),

]
