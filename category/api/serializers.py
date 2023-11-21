
from rest_framework import serializers
from category.models import (
    CategoryModel , 
    MenuCategoryModel, 
    UserFavoriteCategories
)
class BaseCategorySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    image = serializers.ImageField(read_only=True)

    class Meta:
        abstract = True
        fields = ['hidden','id', 'name', 'slug', 'description', 'created_at', 'updated_at']

class CategorySerializer(BaseCategorySerializer):
    selected_by_user = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    hidden = serializers.SerializerMethodField()
    def get_hidden(self,obj):
        if obj.slug == "all-for-you":
            return True
        else:
            return False
    def get_image(self, obj):
        # Get the current request object
        request = self.context.get('request')

        # Check if the object has a 'photo' field
        if obj.image:
            # Get the full URL for the photo by prepending the domain
            site_domain = "app.flxdevpanel.com"  # Replace this with your actual website domain
            return f"https://{site_domain}{obj.image.url}"
        else:
            return None
    def get_selected_by_user(self, obj):
        request_user = self.context['request'].user

        # Check if the user has any favorite categories
        try:
            favorites_obj = UserFavoriteCategories.objects.get(user=request_user)
        except UserFavoriteCategories.DoesNotExist:
            return False

        # Return True if obj is in the user's favorites, otherwise return False
        return obj in favorites_obj.favorite_categories.all()

    class Meta:
        model = CategoryModel
        fields = ['hidden','selected_by_user','id', 'name', 'slug', 'description', 'image', 'created_at', 'updated_at']


class MenuCategorySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = MenuCategoryModel
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'updated_at', 'image']

