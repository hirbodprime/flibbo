from django.db import models
from posts.utils.upload_image import PostUploadHandler 
from django.contrib.auth import get_user_model
User = get_user_model()

upload_nft_product_handler = PostUploadHandler('nft_produtct', 'nft', 'nfts')

def upload_nft_product(instance, filename):
    return upload_nft_product_handler.get_filename(instance, filename)


class NftProductModel(models.Model):
    pro_id = models.IntegerField(blank=True,null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    slug = models.SlugField(unique=True, max_length=200, allow_unicode=True, blank=True, null=True)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to=upload_nft_product, blank=True, null=True)
    video = models.FileField(upload_to='nft_videos', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bought_or_not = models.BooleanField(default=False)
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = 'NFT Product'
        verbose_name_plural = 'NFT Products'



class PurchaseTestModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    purchase_name = models.CharField(null=True, blank=True,max_length=100)
    order_number = models.BigIntegerField(null=True,blank=True)




class OrderNumber(models.Model):
    order_number = models.BigIntegerField(null=True,blank=True)
