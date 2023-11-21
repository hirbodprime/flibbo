from django.contrib import admin
from .models import CategoryModel, MenuCategoryModel, SubCategoryModel, UserFavoriteCategories

class UserFavoriteCategoriesAdmin(admin.ModelAdmin):
    list_display = ('user',)

    # Customize the display of favorite categories and subcategories
    filter_horizontal = ('favorite_categories', 'favorite_subcategories')

# Register the admin class with the model
admin.site.register(UserFavoriteCategories, UserFavoriteCategoriesAdmin)

# Admin class for CategoryModel
class CategoryModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at','id')
    list_filter = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}
# Admin class for CategoryModel
class SubCategoryModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}

# Admin class for MenuCategoryModel
class MenuCategoryModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}

# Register the admin classes
admin.site.register(CategoryModel, CategoryModelAdmin)
admin.site.register(SubCategoryModel, SubCategoryModelAdmin)
admin.site.register(MenuCategoryModel, MenuCategoryModelAdmin)
