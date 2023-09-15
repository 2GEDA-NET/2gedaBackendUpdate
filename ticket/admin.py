from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

# Register your models here.


@admin.register(PayOutInfo)
class PayOutInfoAdmin(ImportExportModelAdmin):
    list_display = ('user', 'bank_name', 'account_name',
                    'account_number', 'account_type')
    list_filter = ('user', 'bank_name', 'account_name')


@admin.register(Withdraw)
class WithdrawAdmin(ImportExportModelAdmin):
    list_display = ('details', 'amount', 'is_successful',
                    'is_pending', 'is_failed')
    list_filter = ('is_successful', 'is_failed', 'is_pending')
    list_editable = ('is_successful', 'is_failed', 'is_pending')
