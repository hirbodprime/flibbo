from rest_framework import serializers
from marketplace.models import NftProductModel
from decimal import Decimal

class NftProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = NftProductModel
        fields = '__all__'


class NftProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NftProductModel
        fields = ['title', 'price', 'description', 'bought_or_not']
    def create(self, validated_data):
        # Automatically set the 'user' field to the currently logged-in user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class NftProductlistSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    user_bought = serializers.SerializerMethodField()
    caption = serializers.SerializerMethodField()

    def get_user_bought(self, obj):
        print(obj)
        # Get the current request user
        request_user = self.context['request'].user

        # Check if the request user has bought this subscription level
        if request_user.is_authenticated:
            return NftProductModel.objects.filter(user=request_user, title=obj).exists()

        return False
    
    def get_username(self, obj):
        # Return the username from the associated user object
        return obj.user.username
    def get_caption(self, obj):
        # Return the username from the associated user object
        return obj.description
    def get_price(self, obj):
        # Return the username from the associated user object
        return str(obj.price)

    def get_image(self, obj):
        # Get the current request object
        request = self.context.get('request')

        # Check if the object has a 'photo' field
        if obj.image:
            site_domain = "app.flxdevpanel.com"  # Replace this with your actual website domain
            return f"https://{site_domain}{obj.image.url}"

        else:
            return None
    def get_video(self, obj):
        # Get the current request object
        request = self.context.get('request')

        # Check if the object has a 'photo' field
        if obj.video:
            # Get the full URL for the photo by prepending the domain
            site_domain = "app.flxdevpanel.com"  # Replace this with your actual website domain
            return f"https://{site_domain}{obj.video.url}"
        else:
            return None
    class Meta:
        model = NftProductModel
        fields = ['pro_id','id','title', 'price', 'created_at','caption','image','video','user_bought','username']
    def create(self, validated_data):
        # Automatically set the 'user' field to the currently logged-in user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    



class NftProductGeterializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    user_bought = serializers.SerializerMethodField()
    caption = serializers.SerializerMethodField()

    def get_user_bought(self, obj):
        print(obj)
        # Get the current request user
        request_user = self.context['request'].user

        # Check if the request user has bought this subscription level
        if request_user.is_authenticated:
            return NftProductModel.objects.filter(user=request_user, title=obj).exists()

        return False
    
    def get_username(self, obj):
        # Return the username from the associated user object
        return obj.user.username
    def get_caption(self, obj):
        # Return the username from the associated user object
        return obj.description
    def get_price(self, obj):
        # Return the username from the associated user object
        return str(obj.price)

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
    def get_video(self, obj):
        # Get the current request object
        request = self.context.get('request')

        # Check if the object has a 'photo' field
        if obj.video:
            # Get the full URL for the photo by prepending the domain
            site_domain = "app.flxdevpanel.com"  # Replace this with your actual website domain
            return f"https://{site_domain}{obj.video.url}"
        else:
            return None
    class Meta:
        model = NftProductModel
        fields = ['pro_id','id','title', 'price', 'created_at','caption','image','video','user_bought','username']
    def create(self, validated_data):
        # Automatically set the 'user' field to the currently logged-in user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



class NftProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NftProductModel
        fields = ['title', 'price', 'description', 'image', 'bought_or_not']
    def create(self, validated_data):
        # Automatically set the 'user' field to the currently logged-in user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



class NftProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = NftProductModel
        fields = ['title', 'price', 'description', 'image', 'bought_or_not']
    def create(self, validated_data):
        # Automatically set the 'user' field to the currently logged-in user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)