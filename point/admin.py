from django.contrib import admin
from .models import (
    ReferralCodeModel, 
    PointWalletModel, 
    GoldUsersListModel, 
    NormalUsersListModel, 
    WithDrawalRequestModel,
    AmountModel,
    RefMoneyModel,
    UserWalletModel
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django import forms

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

class AmountModelForm(forms.ModelForm):
    class Meta:
        model = AmountModel
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk and AmountModel.objects.exists():
            raise ValidationError(_('Only one instance of AmountModel is allowed.'))
        return cleaned_data

@admin.register(AmountModel)
class AmountModelAdmin(admin.ModelAdmin):
    form = AmountModelForm

admin.site.register(UserWalletModel)
admin.site.register(RefMoneyModel)
admin.site.register(ReferralCodeModel, ReferralCodeAdmin)
admin.site.register(PointWalletModel, PointWalletAdmin)
admin.site.register(GoldUsersListModel, GoldUsersListAdmin)
admin.site.register(NormalUsersListModel, NormalUsersListAdmin)
admin.site.register(WithDrawalRequestModel, WithDrawalRequestAdmin)
