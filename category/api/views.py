from category.models import CategoryModel, MenuCategoryModel,UserFavoriteCategories
from .serializers import CategorySerializer
from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class FavoriteCategoryAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch the user's favorite categories
        user = request.user
        user_favorites, created = UserFavoriteCategories.objects.get_or_create(user=user)
        categories = CategoryModel.objects.all()
        context = {
            'request': request
        }

        # Serialize and return the items
        serializer = CategorySerializer(categories, many=True,context=context)
        response_data = {
            'data': serializer.data,
            'success': True,
        }
        return Response(response_data)

    def post(self, request):
        ids = request.data.get('ids', '')
        id_list = ids.split(',')  # Split the string into a list of IDs
        user = request.user
        favorite_categories = CategoryModel.objects.filter(id__in=id_list)

        # Get or create the UserFavoriteCategories instance for the user
        user_favorites, created = UserFavoriteCategories.objects.get_or_create(user=user)

        # Set the favorite_categories on the user_favorites instance
        user_favorites.favorite_categories.set(favorite_categories)
        user_favorites.save()
        context = {
            'request': request
        }
        # Serialize and return the newly added items
        serializer = CategorySerializer(favorite_categories, many=True,context=context)
        response_data = {
            'data': serializer.data,
            'success': True,
        }
        return Response(response_data)
class CategoryListView(generics.ListAPIView):
    queryset = CategoryModel.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # Get the serialized data using the serializer class
        serializer = self.get_serializer(self.get_queryset(), many=True)
        
        # Create a custom response dictionary with your desired key
        custom_response = {
            'data': serializer.data,
            'success':True, 
        }
        
        return Response(custom_response)
        
class CategoryDetailView(generics.RetrieveAPIView):
    queryset = CategoryModel.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class AddFavoriteCategory(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, ids):
        id_list = ids.split(',')  # Split the string into a list of IDs
        user = request.user
        favorite_categories = CategoryModel.objects.filter(id__in=id_list)
        
        # Get or create the UserFavoriteCategories instance for the user
        user_favorites, created = UserFavoriteCategories.objects.get_or_create(user=user)

        # Set the favorite_categories on the user_favorites instance
        user_favorites.favorite_categories.set(favorite_categories)
        user_favorites.save()
        
        # Serialize and return the items
        serializer = CategorySerializer(favorite_categories, many=True)
        response_data = {
            'data':serializer.data,
            'success':True,
        }
        return Response(response_data)
        


