import re

from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import render, redirect
from . import models
# Create your views here.
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

class Register(View):

    def get(self,request):

        return render(request, 'register.html')

    def post(self,request):
        # 1.功能分析
        #   .用户输入
        #   .前端form提交
        #   .后端获取数据并处理

        # 2.后端获取数据处理
        #  .request获取数据
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        pic_code = request.POST.get('pic_code')
        sms_code = request.POST.get('sms_code')
        #  .判断数据合法性

        # 1.数据不能为空
        # all([])迭代的对象为空,返回True
        # all([a,b,c])迭代对象里的元素不为空返回True
        if not all([username,password,password2,mobile,pic_code,sms_code]):
            return HttpResponseBadRequest('数据不能为空')
        # 2.用户名是否为5-20位
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseBadRequest('用户名是否为5-20位')
        # 3.密码是否为字母加数字加_-
        if not re.match(r'^[a-zA-Z0-9_-]{8,20}$', password):
            return HttpResponseBadRequest('请输入8-20位的密码')
        # 4.手机号是否为11位
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('手机号格式错误')
        # 5.密码判断
        if password != password2:
            return HttpResponseBadRequest('两次密码不一致')
        #  .合法存入数据库
        RegisterUsersmsCount().get()
        user = models.User.objects.create_user(username=username,
                                        password=password,
                                        mobile=mobile)

        # 返回合法信息
        # return redirect()
        # request.session['username'] = user.username
        # request.session['id'] = user.id

        from django.contrib.auth import login

        login(request,user)

        return redirect(reverse('user1:index'))
        #
        # return HttpResponse('您已经注册成功')


class RegisterUsernameCountView(View):

    def get(self,request,username):
        # ① 获取前端提交的数据
        # ② 查询数量
        count= models.User.objects.filter(username=username).count()
        #     数量为1: 重复
        #     数量为0: 不重复
        return JsonResponse({'count':count})


class RegisterUserPhoneCount(View):

    def get(self,request,mobile):

        count = models.User.objects.filter(mobile=mobile).count()

        return JsonResponse({"count":count})


class RegisterUsersmsCount(View):

    def get(self,request):
        mobile = request.GET.get('mobile')
        mobile = 'sms_%s' % mobile
        sms_code = request.GET.get('sms_code')
        redis_con = get_redis_connection('code')
        mobile1 = redis_con.get(mobile).decode()
        if sms_code != mobile1:
            return JsonResponse({"error_code":"输入的验证码错误重新输入!"})