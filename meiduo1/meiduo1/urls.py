"""meiduo1 URL Configuration

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
from django.http import HttpResponse


def t1(request):

    return HttpResponse('haha')

def t2(request):
    import logging
    # 创建日志记录器
    logger = logging.getLogger('django')
    # 输出日志
    logger.debug('测试logging模块debug')
    logger.info('测试logging模块info')
    logger.error('测试logging模块error')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^t1/', t1),
    url(r'^t2/', t2),

]
