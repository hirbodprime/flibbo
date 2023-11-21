from rest_framework import serializers
from wallet.models import UsersNfts
from marketplace.models import NftProductModel
class UsersNftsSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    caption = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    user_bought = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    pro_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    def get_username(self, obj):
        return f'{obj.nft_product.user.username}'




    def get_video(self, obj):
        # Get the current request object
        request = self.context.get('request')

        # Check if the object has a 'photo' field
        if obj.nft_product.video:
            # Get the full URL for the photo by prepending the domain
            return request.build_absolute_uri(obj.nft_product.video.url)
        else:
            return None

    def get_caption(self, obj):
        print(obj.nft_product.description)
        return obj.nft_product.description

    def get_created_at(self, obj):
        return obj.purchase_date

    def get_price(self, obj):
        print(obj.nft_product.price)
        return str(obj.nft_product.price)
    def get_title(self, obj):
        print(obj.nft_product.title)
        return obj.nft_product.title
    def get_pro_id(self, obj):
        print(obj.nft_product.title)
        return obj.nft_product.pro_id
    def get_user_bought(self, obj):
        return True
    class Meta:
        model = UsersNfts
        fields = ['id','title', 'price', 'caption', 'video', 'user_bought','created_at','pro_id','username']
