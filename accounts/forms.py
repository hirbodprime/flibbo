from django import forms

class DeleteAccountForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_delete = forms.BooleanField(required=True)
