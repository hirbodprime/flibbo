from django.contrib import admin
from .models import (
    ReferralCodeModel, 
    PointWalletModel, 
    GoldUsersListModel, 
    NormalUsersListModel, 
    WithDrawalRequestModel
)

# Admin class for ReferralCodeModel
class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'ref_code')

# Admin class for PointWalletModel
class PointWalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')

# Admin class for GoldUsersListModel
class GoldUsersListAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('level_1', 'level_2', 'level_3',)

# Admin class for NormalUsersListModel
class NormalUsersListAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('users',)

# Admin class for WithDrawalRequestModel
class WithDrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email')

# Register your models here
admin.site.register(ReferralCodeModel, ReferralCodeAdmin)
admin.site.register(PointWalletModel, PointWalletAdmin)
admin.site.register(GoldUsersListModel, GoldUsersListAdmin)
admin.site.register(NormalUsersListModel, NormalUsersListAdmin)
admin.site.register(WithDrawalRequestModel, WithDrawalRequestAdmin)
