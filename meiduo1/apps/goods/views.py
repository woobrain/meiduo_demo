from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator
# Create your views here.
from django.views import View

from apps.goods.models import GoodsCategory, SKU
from apps.user1.utils import get_categories


class ListView(View):
    def get(self, request, category_id,page_num):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return render(request,'404.html')
        sort = request.GET.get('sort','default')
        categories = get_categories()
        breadcrumb={
            "cat1":'',
            "cat2":'',
            "cat3":'',

        }
        # a = category.subs
        if category.parent is None:
            breadcrumb['cat1']=category
        elif category.subs.count() == 0:
            breadcrumb['cat3']=category
            breadcrumb['cat2']=category.parent
            breadcrumb['cat1']=category.parent.parent
        else:
            breadcrumb['cat2']=category
            breadcrumb['cat1']=category.parent

        if sort == 'price':
            sort_field = 'price'
        elif sort == 'hot':
            sort_field = '-sales'
        else:
            sort = 'default'
            sort_field = 'create_time'
        skus = SKU.objects.filter(category=category, is_launched=True).order_by(sort_field)

        # data = SKU.objects.filter(category_id=category_id)

        paginator = Paginator(object_list=skus,
                              per_page=5,
                              )
        page_skus = paginator.page(page_num)

        total_page = paginator.num_pages

        context = {
            'categories': categories,  # 频道分类
            'breadcrumb': breadcrumb,  # 面包屑导航
            'sort': sort,  # 排序字段
            'category': category,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
        }

        return render(request, 'list.html', context)


class HotView(View):
    def get(self,request,category_id):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({"code":5555,"errmsg":"ok"})
        hots = SKU.objects.filter(category=category,is_launched=True).order_by('-sales')[:2]

        hot_list=[]
        for sku in hots:
            hot_list.append({
                'id':sku.id,
                'default_image_url':sku.default_image.url,
                'name':sku.name,
                'price':sku.price

            })
        a=hot_list

        return JsonResponse({"code":0,"errmsg":"ok","hot_skus":hot_list})