from django.urls import path

from product.views.drink_views         import DrinkView
from product.views.drink_list_views    import DrinkListView
from product.views.manufacture_views   import ManufactureView
from product.views.category_list_views import CategoryListView
from product.views.pre_info_list_views import PreInfoListView
from product.views.product_image_views import ProductImageView



urlpatterns = [
    path('/drink', DrinkView.as_view()),
    path('/drink_list', DrinkListView.as_view()),
    path('/drink/<int:product_id>', DrinkView.as_view()),

    path('/image', ProductImageView.as_view()),
    path('/image/<int:product_image_id>', ProductImageView.as_view()),

    path('/manufacture', ManufactureView.as_view()),
    path('/manufacture/<int:manufacture_id>', ManufactureView.as_view()),

    path('/category_list', CategoryListView.as_view()),

    path('/pre_info_list', PreInfoListView.as_view()),
]