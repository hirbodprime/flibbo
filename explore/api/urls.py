from django.urls import path
from .views import ExploreViewApi,ExploreCategoriesViewApi


urlpatterns = [
    path('main/', ExploreViewApi.as_view(), name='explore-list'),
    path('category/<slug:category_name>/', ExploreCategoriesViewApi.as_view(), name='explore-category-list'),

]
