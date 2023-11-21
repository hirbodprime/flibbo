from django.contrib import admin
from .models import NftProductModel,PurchaseTestModel,OrderNumber

class NftProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'user', 'created_at', 'updated_at')  # Fields to display in the list view
    list_filter = ('user', 'created_at', 'updated_at')  # Filter options
    search_fields = ('title', 'description')  # Search fields
    date_hierarchy = 'created_at'  # Date hierarchy navigation
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(NftProductModel, NftProductAdmin)


admin.site.register(PurchaseTestModel)
admin.site.register(OrderNumber)

