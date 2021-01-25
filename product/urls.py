from django.urls import path

from product.views.drink_views         import DrinkView
from product.views.drink_list_views    import DrinkListView
from product.views.category_list_views import CategoryListView



urlpatterns = [
    path('/drink', DrinkView.as_view()),
    path('/drink_list', DrinkListView.as_view()),
    path('/drink/<int:product_id>', DrinkView.as_view()),

    path('/category_list', CategoryListView.as_view()),
]