from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.core.paginator import Paginator
# Create your views here.
from django.views import View

from apps.goods.models import GoodsCategory, SKU


class ListView(View):
    def get(self, request, category_id,page_num):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return render(request,'404.html')

        data = SKU.objects.filter(category_id=category_id)

        paginator = Paginator(object_list=data,
                              per_page=5,
                              )
        page_skus = paginator.page(page_num)

        total_page = paginator.num_pages

        context = {
            # 'categories': categories,  # 频道分类
            # 'breadcrumb': breadcrumb,  # 面包屑导航
            # 'sort': sort,  # 排序字段
            'category': category,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
        }

        return render(request, 'list.html', context)


