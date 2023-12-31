from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

# Register your models here.
@admin.register(EventCategory)
class EventCategory(ImportExportModelAdmin):
    list_display = ('name', 'image')

@admin.register(Event)
class EventAdmin(ImportExportModelAdmin):
    list_display = ('user', 'get_attendees_count', 'title', 'desc', 'platform', 'category', 'location', 'ticket')
    list_filter = ('is_popular', 'is_promoted')

    def get_attendees_count(self, obj):
        return obj.attendees.count()
    
    get_attendees_count.short_description = 'Number of Attendees'


@admin.register(Bank)
class BankAdmin(ImportExportModelAdmin):
    list_display = ('name', 'bank_code')

@admin.register(Ticket)
class TicketAdmin(ImportExportModelAdmin):
    list_display = ('category', 'price', 'quantity',)
    list_filter = ('category', 'is_sold')

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
