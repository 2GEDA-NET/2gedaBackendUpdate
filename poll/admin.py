from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *


# Register your models here.

@admin.register(Option)
class OptionAdmin(ImportExportModelAdmin):
    list_display = ('content',)

@admin.register(Poll)
class PollAdmin(ImportExportModelAdmin):
    list_display = ('id','user', 'question', 'duration', 'type','is_editable')

@admin.register(Payment)
class PaymentAdmin(ImportExportModelAdmin):
    list_display = ('user', 'amount', 'transaction_reference', 'status', 'timestamp')

@admin.register(PollMedia)
class PollMediaPayment(ImportExportModelAdmin):
    list_display = ('image',)

@admin.register(PollView)
class PollViewAdmin(ImportExportModelAdmin):
    list_display = ('user', 'poll', 'timestamp')




@admin.register(Voting)
class VoteAdmin(ImportExportModelAdmin):
    list_display = ('user','have_Voted','cost')