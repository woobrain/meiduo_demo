import json
import re

from django.contrib.auth import logout
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import render, redirect

from apps.myaddr.models import Address
from apps.user.models import User
from apps.user.utils import check_active_email_url
from celery_tasks.email.tasks import send_active_email
from . import models
# Create your views here.
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection


class Register(View):
    def get(self, request):

        return render(request, 'register.html')

    def post(self, request):
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
        if not all([username, password, password2, mobile, pic_code, sms_code]):
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
        # .合法存入数据库
        # RegisterUsersmsCount().get()
        user = models.User.objects.create_user(username=username,
                                               password=password,
                                               mobile=mobile)

        # 返回合法信息
        # return redirect()
        # request.session['username'] = user.username
        # request.session['id'] = user.id

        from django.contrib.auth import login

        login(request, user)

        return redirect(reverse('user1:index'))
        #
        # return HttpResponse('您已经注册成功')


class RegisterUsernameCountView(View):
    def get(self, request, username):
        # ① 获取前端提交的数据
        # ② 查询数量
        count = models.User.objects.filter(username=username).count()
        #     数量为1: 重复
        #     数量为0: 不重复
        return JsonResponse({'count': count})


class RegisterUserPhoneCount(View):
    def get(self, request, mobile):
        count = models.User.objects.filter(mobile=mobile).count()

        return JsonResponse({"count": count})


# class RegisterUsersmsCount(View):
#
#     def get(self,request):
#         mobile = request.GET.get('mobile')
#         mobile = 'sms_%s' % mobile
#         sms_code = request.GET.get('sms_code')
#         redis_con = get_redis_connection('code')
#         mobile1 = redis_con.get(mobile).decode()
#         if sms_code != mobile1:
#             return JsonResponse({"error_code":"输入的验证码错误重新输入!"})


class LoginView(View):
    def get(self, request):

        return render(request, 'login.html')

    # 405 Method Not Allowed
    # 请求方式没有被允许,一般是未写此请求函数
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remember = request.POST.get('remembered')

        if not all([username, password]):
            # return JsonResponse({"code":"4002","errmsg":"参数不全"})
            return HttpResponseBadRequest("参数不全")
            # 2.用户名是否为5-20位
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseBadRequest('用户名是否为5-20位')
        # 3.密码是否为字母加数字加_-
        if not re.match(r'^[a-zA-Z0-9_-]{8,20}$', password):
            return HttpResponseBadRequest('请输入8-20位的密码')
        from django.contrib.auth import login, authenticate
        from django.contrib.auth.backends import ModelBackend
        # mobile = re.match(r'^1[3-9]\d{9}$',username).group()
        # username = User.objects.get(mobile=mobile).username
        user = authenticate(username=username, password=password)
        if user is None:
            return HttpResponseBadRequest("用户名或者密码不匹配")

        login(request, user)

        if remember:
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)
        # request.user = username

        response = redirect(reverse("user1:index"))
        response.set_cookie('username', user.username, max_age=3600 * 24)
        return response


class LogoutView(View):
    def get(self, request):
        # 清理session
        logout(request)

        response = redirect(reverse('user1:index'))
        # 清理cookie
        # response.set_cookie('username',None,max_age=0)
        response.delete_cookie('username')
        return response


from django.contrib.auth.mixins import LoginRequiredMixin


class CenterView(LoginRequiredMixin, View):
    def get(self, request):
        # if request.user.is_authenticated:
        #     return render(request,'user_center_info.html')
        # else:
        #     return redirect(reverse('user:login'))
        context = {
            "username": request.user.username,
            "mobile": request.user.mobile,
            "email": request.user.email,
            "email_active": request.user.email_active,
        }
        return render(request, 'user_center_info.html', context=context)


class SiteView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_center_site.html')


class EmailView(LoginRequiredMixin, View):
    def put(self, request):
        body = request.body.decode()
        data = json.loads(body)

        email = data.get('email')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return JsonResponse({'code': 5006, 'errmsg': '邮箱不符合规则'})
        request.user.email = email
        request.user.save()

        from django.core.mail import send_mail
        #
        # def send_mail(subject, message, from_email, recipient_list,
        #               fail_silently=False, auth_user=None, auth_password=None,
        #               connection=None, html_message=None):
        # subject, message, from_email, recipient_list,
        # subject        主题
        # subject = '美多商场激活邮件'
        # # message,       内容
        # message = ''
        # # from_email,  谁发的
        # from_email = '欢乐玩家<15893775982@163.com>'
        # # recipient_list,  收件人列表
        # recipient_list = ['15893775982@163.com']
        #
        # html_mesage = "<a href='http://www.meiduo.site:8000/emailsactive/?token_id=1'>戳我有惊喜</a>"
        #
        # send_mail(subject=subject,
        #           message=message,
        #           from_email=from_email,
        #           recipient_list=recipient_list,
        #           html_message=html_mesage)
        send_active_email.delay(request.user.id, email)
        # ⑤ 返回相应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class Emailactive(View):
    def get(self, request):
        token_id = request.GET.get('token')
        if token_id is None:
            return HttpResponseBadRequest('激活失败')
        data = check_active_email_url(token_id)
        if data is None:
            return HttpResponseBadRequest('验证失败')
        id = data.get('id')
        email = data.get('email')

        try:
            user = User.objects.get(id=id, email=email)
        except User.DoesNotExist:
            return HttpResponseBadRequest('验证失败')
        user.email_active = True
        user.save()
        return redirect(reverse("user:center"))
        # return HttpResponse('激活成功')


class AddView(LoginRequiredMixin, View):
    def post(self, request):
        # count = request.user.addresses.count()
        # print(Address.objects.filter(user=request.user).count())
        user = request.user
        count = Address.objects.filter(user_id=request.user.id).count()
        if count > 20:
            return JsonResponse({"code": 5555, "errmsg": "最多可创建20个地址"})
        data_b = request.body.decode()
        data = json.loads(data_b)
        email = data.get('email')
        mobile = data.get('mobile')
        district_id = data.get('district_id')
        city_id = data.get('city_id')
        province_id = data.get('province_id')
        place = data.get('place')
        receiver = data.get('receiver')
        tel = data.get('tel')
        title = data.get('title')
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseBadRequest('缺少必传参数')
        # if not re.match(r'^1[3-9]\d{9}$', mobile):
        #     return JsonResponse({"code": 4007, "errmsg": "最多可创建20个地址"})
        # if tel:
        #     if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
        #         return JsonResponse({"code": 5002, "errmsg": "最多可创建20个地址"})
        # if email:
        #     if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        #         return JsonResponse({"code": 5001, "errmsg": "最多可创建20个地址"})

        try:
            addr = Address.objects.create(
                user=request.user,
                email=email,
                mobile=mobile,
                district_id=district_id,
                city_id=city_id,
                province_id=province_id,
                tel=tel,
                place=place,
                receiver=receiver,
                title=title,

            )
        except Exception as e:
            return JsonResponse({"code": 5555, "errmsg": "新增地指出错"})
        a = addr.province.name

        address = {
            "id": addr.id,
            "title": addr.title,
            "receiver": addr.receiver,
            "province": addr.province.name,
            "city": addr.city.name,
            "district": addr.district.name,
            "place": addr.place,
            "mobile": addr.mobile,
            "tel": addr.tel,
            "email": addr.email
        }

        return JsonResponse({"code": 0, "errmsg": "ok", "address": address})


class AddressView(LoginRequiredMixin, View):
    """用户收货地址"""

    def get(self, request):
        """提供收货地址界面"""
        # 获取用户地址列表
        login_user = request.user
        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        address_dict_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "province_id": address.province_id,
                "city": address.city.name,
                "city_id": address.city_id,
                "district": address.district.name,
                "district_id": address.district_id,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)

        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_dict_list,
        }

        return render(request, 'user_center_site.html', context)


class UpdateDestroyAddressView(LoginRequiredMixin, View):
    """修改和删除地址"""

    def put(self, request, address_id):
        """修改地址"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return HttpResponseBadRequest('参数email有误')

        # 判断地址是否存在,并更新地址信息
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:

            return JsonResponse({'code': 5555, 'errmsg': '更新地址失败'})

        # 构造响应数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        return JsonResponse({'code': 0, 'errmsg': '更新地址成功', 'address': address_dict})

    def delete(self, request, address_id):
        """删除地址"""
        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)

            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:

            return JsonResponse({'code': 7777, 'errmsg': '删除地址失败'})

        # 响应删除地址结果
        return JsonResponse({'code': 0, 'errmsg': '删除地址成功'})


class DefaultAddressView(LoginRequiredMixin, View):
    """设置默认地址"""

    def put(self, request, address_id):
        """设置默认地址"""
        try:
            # 接收参数,查询地址
            address = Address.objects.get(id=address_id)

            # 设置地址为默认地址
            request.user.default_address = address
            request.user.save()
        except Exception as e:

            return JsonResponse({'code': 5555, 'errmsg': '设置默认地址失败'})

        # 响应设置默认地址结果
        return JsonResponse({'code': 0, 'errmsg': '设置默认地址成功'})


class UpdateTitleAddressView(LoginRequiredMixin, View):
    """设置地址标题"""

    def put(self, request, address_id):
        """设置地址标题"""
        # 接收参数：地址标题
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')

        try:
            # 查询地址
            address = Address.objects.get(id=address_id)

            # 设置新的地址标题
            address.title = title
            address.save()
        except Exception as e:

            return JsonResponse({'code': 6666, 'errmsg': '设置地址标题失败'})

        # 4.响应删除地址结果
        return JsonResponse({'code': 0, 'errmsg': '设置地址标题成功'})




