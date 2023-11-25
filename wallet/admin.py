from django.contrib import admin
from .models import UsersNfts, WalletModel

class UsersNftsAdmin(admin.ModelAdmin):
    list_display = ('user', 'nft_product', 'purchase_date', 'bought_or_not')
    list_filter = ('user', 'nft_product', 'purchase_date', 'bought_or_not')
    search_fields = ('user__username', 'nft_product__title')
    date_hierarchy = 'purchase_date'

admin.site.register(WalletModel)
admin.site.register(UsersNfts, UsersNftsAdmin)
