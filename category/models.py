from django.db import models
from category.utils.upload_image import ImageUploadHandler
from django.contrib.auth import get_user_model

User = get_user_model()


category_upload_handler = ImageUploadHandler("categories", "category")
def category_upload(instance, filename):
    return category_upload_handler(instance, filename)


menu_category_upload_handler = ImageUploadHandler("menu_categories", "menu_category")
def menu_category_upload(instance, filename):
    return menu_category_upload_handler(instance, filename) 


sub_category_upload_handler = ImageUploadHandler("sub_categories", "sub_category")
def sub_category_upload(instance, filename):
    return sub_category_upload_handler(instance, filename)


class BaseCategoryModel(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=500, allow_unicode=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hidden = models.BooleanField(default=False)
    class Meta:
        abstract = True
        
    def __str__(self):
        return self.name


class CategoryModel(BaseCategoryModel):
    image = models.ImageField(upload_to=category_upload, blank=True, null=True)
    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return self.name


class SubCategoryModel(BaseCategoryModel):
    parent = models.ForeignKey(CategoryModel, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=sub_category_upload, blank=True, null=True)
    class Meta:
        verbose_name_plural = "Sub Categories"
    def __str__(self):
        return f'{self.name}, {self.parent.name}'


class UserFavoriteCategories(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_categories = models.ManyToManyField(CategoryModel, blank=True)
    favorite_subcategories = models.ManyToManyField(SubCategoryModel, blank=True)


class MenuCategoryModel(BaseCategoryModel):
    image = models.ImageField(upload_to=menu_category_upload, blank=True, null=True)
    class Meta:
        verbose_name_plural = "Menu Categories"
    def __str__(self):
        return self.name