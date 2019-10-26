import base64
from django_redis import get_redis_connection
import pickle

def make_redis_cookie(request,user,response):
    carts = request.COOKIES.get('carts')
    carts_dict = pickle.loads(base64.b64decode(carts))
    # if carts is None:
        # {
        #   sku_id1:{'count':count,'selected':selected}
        #   sku_id2:{'count':count,'selected':selected}
        # }
        # carts_dict = pickle.loads(base64.b64decode(carts))
        # carts_info = []
        # for sku_id,count_dic in carts_dict.items():
        #     for count,selected in count_dic.items:
        #         carts_info.append({
        #
        #         })
    # else:
    #     carts_dict = {}
    #
    if user.is_authenticated:
        redis_con = get_redis_connection('carts')
        new_list = redis_con.hgetall('user_%s'%user.id)

        for sku_id in carts_dict:
            if bytes(sku_id) not in new_list:
                redis_con.hset('user_%s' % user.id, sku_id, carts_dict[sku_id]['count'])
                if carts_dict[sku_id]['selected']:
                    redis_con.sadd('selected_%s' % user.id, sku_id)

            else:
                new_list[sku_id] += carts_dict[sku_id]['count']
                redis_con.hset('user_%s' % user.id, sku_id, new_list[sku_id])
                if carts_dict[sku_id]['selected']:
                    redis_con.sadd('selected_%s' % user.id, sku_id)
        response.delete_cookie('carts')
        return response
