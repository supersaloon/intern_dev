from django.urls import path

from product.views.drink_views      import DrinkView
from product.views.drink_list_views import DrinkListView


urlpatterns = [
    path('/drink', DrinkView.as_view()),
    path('/drink_list', DrinkListView.as_view()),
    # path('/drink/<int:product_id>', DrinkView.as_view())
]