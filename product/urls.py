from django.urls import path

from product.views.drink_views                 import DrinkView
from product.views.drink_list_views            import DrinkListView
from product.views.manufacture_views           import ManufactureView
from product.views.manufacture_list_views      import ManufactureListView
from product.views.category_list_views         import CategoryListView
from product.views.pre_info_list_views         import PreInfoListView
from product.views.product_image_views         import ProductImageView
from product.views.label_views                 import LabelView
from product.views.drink_base_info_views       import DrinkBaseInfoView
from product.views.test_views                  import TestView
from product.views.drink_industrial_info_views import DrinkIndustrialInfoView


urlpatterns = [
    path('/drink', DrinkView.as_view()),
    path('/drink_list', DrinkListView.as_view()),
    path('/drink/<int:product_id>', DrinkView.as_view()),

    path('/drink/base_info', DrinkBaseInfoView.as_view()),
    path('/drink/base_info/<int:product_id>', DrinkBaseInfoView.as_view()),

    path('/drink/industrial_info', DrinkIndustrialInfoView.as_view()),
    path('/drink/industrial_info/<int:product_id>', DrinkIndustrialInfoView.as_view()),

    path('/product_image', ProductImageView.as_view()),
    path('/product_image/<int:product_image_id>', ProductImageView.as_view()),

    path('/label', LabelView.as_view()),
    path('/label/<int:label_id>', LabelView.as_view()),

    path('/manufacture', ManufactureView.as_view()),
    path('/manufacture_list', ManufactureListView.as_view()),
    path('/manufacture/<int:manufacture_id>', ManufactureView.as_view()),

    path('/category_list', CategoryListView.as_view()),

    path('/pre_info_list', PreInfoListView.as_view()),

    path('/test/<int:id>', TestView.as_view()),
]