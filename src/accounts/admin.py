from django.contrib import admin

from src.accounts.models import User, Address

admin.site.register(User)
admin.site.register(Address)