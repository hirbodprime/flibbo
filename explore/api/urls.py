from django.urls import path
from .views import ExploreViewApi,ExploreCategoriesViewApi,SortByLikesAndViewsApi,SortByRecencyApi


urlpatterns = [
    path('main/', ExploreViewApi.as_view(), name='explore-list'),
    path('category/<slug:category_name>/', ExploreCategoriesViewApi.as_view(), name='explore-category-list'),
    path('sort/popular/', SortByLikesAndViewsApi.as_view(), name='explore-list-likes-views'),
    path('sort/recent/', SortByRecencyApi.as_view(), name='explore-list-recent'),
]
