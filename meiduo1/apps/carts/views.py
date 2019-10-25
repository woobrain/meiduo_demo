import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django_redis import get_redis_connection
# Create your views here.
from django.views import View
import pickle
from apps.goods.models import SKU
import base64


class CartsAddView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            pass
        else:
            carts_data = request.COOKIES.get('carts')
            if carts_data is None:
                context = {
                    "cart_skus": [{
                        "count": "",
                        "selected": "",
                        "default_image_url": "",
                        "name": "",
                        "price": "",
                        "amount": ""
                    }]
                }
                return render(request, 'cart.html', context)
            else:
                data_n = pickle.loads(base64.b64decode(carts_data))
                sku_ids = data_n.keys()
                skus = SKU.objects.filter(id__in=sku_ids)
                cart_skus = []
                for sku in skus:
                    cart_skus.append({
                        'id': sku.id,
                        'count': data_n.get(sku.id).get('count'),
                        'selected': str(data_n.get(sku.id).get('select')),
                        'default_image_url': sku.default_image.url,
                        'name': sku.name,
                        'price': str(sku.price),
                        'amount': str(data_n.get(sku.id).get('count') * sku.price)
                    })

                context = {
                    'cart_skus': cart_skus
                }
                return render(request,'cart.html',context)

    def post(self, request):

        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        if not all([sku_id, count]):
            return JsonResponse({"count": 5555, "errmsg": "参数不全"})
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({"count": 5555, "errmsg": "商品不存在"})
        try:
            count = int(count)
        except:
            return JsonResponse({"count": 5555, "errmsg": "参数类型错误"})
        select = True
        user = request.user
        if user.is_authenticated:
            redis_con = get_redis_connection('carts')
            a_list = redis_con.hkeys('user_%s' % user.id)
            b = str(sku_id).encode()
            if b not in redis_con.hkeys('user_%s' % user.id):
                redis_con.hset('user_%s' % user.id, sku_id, count)
                redis_con.sadd('selected_%s' % user.id, select)
                return JsonResponse({"code": 0, "errmsg": "ok"})
            else:
                count_new = int(redis_con.hget('user_%s' % user.id, sku_id).decode())
                count += count_new
                redis_con.hset('user_%s' % user.id, sku_id, count)
                return JsonResponse({"code": 0, "errmsg": "ok"})

        else:
            carts_data = request.COOKIES.get('carts')
            if carts_data is None:
                cookies_data = {
                    sku_id: {"count": count, "select": select}
                }
            else:
                cookies_data = pickle.loads(base64.b64decode(carts_data))
                if sku_id in cookies_data:
                    count_new = cookies_data[sku_id]['count']

                    count += count_new

                    cookies_data[sku_id] = {"count": count, "select": select}

                else:
                    cookies_data[sku_id] = {"count": count, "select": select}

            s_cookies = pickle.dumps(cookies_data)
            s_base64 = base64.b64encode(s_cookies)
            response = JsonResponse({"code": 0, "errmsg": "ok"})
            response.set_cookie('carts', s_base64, 7 * 24 * 3600)
            return response
