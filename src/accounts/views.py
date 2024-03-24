from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import View, UpdateView
from django.contrib.auth import logout
from src.accounts.models import Address


@method_decorator(login_required, name='dispatch')
class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('account_login')


@method_decorator(login_required, name='dispatch')
class CrossAuthView(View):

    def get(self, request):
        if request.user.is_superuser or request.user.is_staff:
            return redirect("admins:dashboard")
        else:
            return redirect('client:dashboard')

