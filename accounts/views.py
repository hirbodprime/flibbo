from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import DeleteAccountForm
from django.contrib import messages


@login_required
def delete_account(request):
    if request.method == 'POST':
        form = DeleteAccountForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            confirm_delete = form.cleaned_data['confirm_delete']

            # Authenticate user
            user = authenticate(username=username, password=password)
            if user is not None and confirm_delete:
                # Delete the user
                user.delete()
                # Add success message
                messages.success(request, 'Your account has been successfully deleted.')
                form = DeleteAccountForm()  # Reset the form
            else:
                # Add an error message
                form.add_error(None, "Invalid credentials or confirmation not checked.")
    else:
        form = DeleteAccountForm()

    return render(request, 'delete_account.html', {'form': form})