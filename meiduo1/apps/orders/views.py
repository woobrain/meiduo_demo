import json

from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.views import View
from django_redis import  get_redis_connection

from apps.goods.models import SKU
from apps.myaddr.models import Address
from apps.orders.models import OrderInfo, OrderGoods


class OrderComView(LoginRequiredMixin,View):
    def post(self,request):
        data = json.loads(request.body.decode())
        address_id = data.get('address_id')
        pay_method = data.get('pay_method')
        if not all([address_id,pay_method]):
            return JsonResponse({"code":5555,"errmsg":"参数不全"})
        user = request.user
        if user.is_authenticated:
            try:
                addr = Address.objects.get(id=address_id)
            except:
                return JsonResponse({"code":5555,"errmsg":"不存在该地址"})
            if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'],OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
                return JsonResponse({"code":5555,"errmsg":"请选择支付方式"})
            order_id = timezone.localtime().strftime("%Y%m%d%H%M%s") + '%09d'%user.id
            if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
                status_id = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
            else:
                status_id = OrderInfo.ORDER_STATUS_ENUM['UNPAID']
            # total_count = 0
            # total_amount = Decimal('0')
            # freight = Decimal('10.00')
            with transaction.atomic():
                savepoint = transaction.savepoint()
                try:
                    order = OrderInfo.objects.create(
                        order_id=order_id,
                        user=user,
                        pay_method=pay_method,
                        address=addr,
                        status=status_id,
                        total_count=0,
                        total_amount=Decimal('0'),
                        freight=Decimal('10.00'),
                    )
                    redis_con = get_redis_connection('carts')
                    skus = redis_con.smembers('selected_%s'%user.id)
                    info_list = redis_con.hgetall('user_%s'%user.id)
                    for sku_id in skus:
                        sku = SKU.objects.get(id=sku_id)
                        count = int(info_list[sku_id])
                        if sku.stock < count:
                            transaction.savepoint_rollback(savepoint)
                            return JsonResponse({"code":5555,"errmsg":"库存不足"})
                        OrderGoods.objects.create(
                            order=order,
                            sku_id=sku_id,
                            count=count,
                            price=sku.price
                        )
                        sku.stock -= count
                        sku.sales += count
                        sku.save()
                        order.total_count += count
                        order.total_amount += count * sku.price
                    order.total_amount += order.freight
                    order.save()
                except:
                    transaction.savepoint_rollback(savepoint)
                    return JsonResponse({"code": 5555, "errmsg": "下单失败"})
                else:
                    transaction.savepoint_commit(savepoint)

                redis_con.hdel('user_%s'%user.id,*skus)
                redis_con.srem('selected_%s'%user.id,*skus)
                return JsonResponse({"code":0,"errmsg":"ok"})