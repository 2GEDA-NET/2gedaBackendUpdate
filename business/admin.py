from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin


# Register your models here.
@admin.register(BusinessDirectory)
class BusinessDirectoryAdmin(ImportExportModelAdmin):
    list_display = ('name', 'address', 'phone_number', 'about')

@admin.register(Address)
class AddressAdmin(ImportExportModelAdmin):
    list_display = ('street', 'city', 'state', 'country')

@admin.register(PhoneNumber)
class PhoneNumberAdmin(ImportExportModelAdmin):
    list_display = ('phone_number1', 'phone_number2', 'phone_number3', 'phone_number4')
