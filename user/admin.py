from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *
# Register your models here.


@admin.register(User)
class UsersAdmin(ImportExportModelAdmin):
    list_display = ('username', 'first_name', 'last_name','email','phone_number',
                    'is_business', 'is_personal', 'is_admin')
    search_fields = ['username', 'first_name', 'last_name']
    list_editable = ['is_business', 'is_personal', 'is_admin',]
    list_filter = ('is_business', 'is_personal', 'is_admin',)


@admin.register(UserProfile)
class UserProfileAdmin(ImportExportModelAdmin):
    list_display = ('user','work', 'date_of_birth', 'gender',)
    list_filter = ('gender',)
    search_fields = ['user',]

@admin.register(BusinessCategory)
class BusinessCategoryAdmin(ImportExportModelAdmin):
    list_display = ('name', 'desc')
    list_filter = ('name',)

@admin.register(BusinessAvailability)
class BusinessAvailability(ImportExportModelAdmin):
    list_display = ()

@admin.register(BusinessProfile)
class BusinessProfileAdmin(ImportExportModelAdmin):
    list_display = ('profile', 'role', 'business_category',)
    list_filter = ('business_category',)


@admin.register(ReportedUser)
class ReportedUserAdmin(ImportExportModelAdmin):
    list_display = ('user', 'is_banned', 'is_disabled')
    list_editable = ['is_banned', 'is_disabled',]

@admin.register(Address)
class AddressAdmin(ImportExportModelAdmin):
    list_display = ('country', 'city', 'location')


@admin.register(Verification)
class VerificationSerializer(ImportExportModelAdmin):
    list_display = ('profile', 'legal_name', 'work')
