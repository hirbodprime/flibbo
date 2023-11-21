from django.urls import path

from .views import (
    CategoryListView,
    CategoryDetailView,
    AddFavoriteCategory,
    FavoriteCategoryAPI,
    # MenuCategoryDetailView,
    
)

urlpatterns = [

    # path('menu-categories/', MenuCategoryListView.as_view(), name='menu_category_list'),
    # path('menu-categories/<int:pk>/', MenuCategoryDetailView.as_view(), name='menu_category_detail'),
    path('user-favorite-categories/', FavoriteCategoryAPI.as_view(), name='user-favorite-categories'),
    path('list/', CategoryListView.as_view(), name='category-list'),
    path('get/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('add-favorite-categories/<str:ids>/', AddFavoriteCategory.as_view(), name='add-favorite-categories'),

]

