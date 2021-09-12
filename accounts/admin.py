from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Account, Transaction

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'minecraft_uuid', 'email', 'is_staff',]
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('minecraft_uuid',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('minecraft_uuid',)}),
    )

class AccountAdmin(admin.ModelAdmin):
    model = Account
    list_display = ['owner', 'account_name', 'account_type', 'primary', 'balance']

class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    list_display = ['date', 'sender', 'recipient', 'transaction_type', 'amount', 'succeeded']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction, TransactionAdmin)