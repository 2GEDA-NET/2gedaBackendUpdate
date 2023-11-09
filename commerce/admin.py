from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *
# Register your models here.



@admin.register(ProductCategory)
class ProductCategoryAdmin(ImportExportModelAdmin):
    list_display = ('name', 'image', 'description')

@admin.register(Store)
class StoreAdmin(ImportExportModelAdmin):
    list_display = ('userId', 'name', 'create_at')


@admin.register(SaleLocation)
class SaleLocationAdmin(ImportExportModelAdmin):
    list_display = ('name',)

@admin.register(ProductReview)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ('user', 'product', 'rating', 'review_text', 'created_at',)


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    list_display = ('buyer', 'status', 'shipping_address', 'billing_address', 'created_at', 'updated_at')

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ('title', 'business', 'category', 'price', 'is_trending', 'is_promoted','promotion_plan',)
    list_filter = ('is_trending', 'create_at', 'business', 'category',)  # Add filters for the desired fields
    # Enable in-place editing for the fields
    list_editable = ('is_trending',)


@admin.register(ProductImg)
class ProductImgAdmin(ImportExportModelAdmin):
    list_display = ('productId', 'image',)

@admin.register(PromotionPlan)
class PromotionPlanAdmin(ImportExportModelAdmin):
    list_display = ('name', 'amount',)


@admin.register(Cart)
class CartAdmin(ImportExportModelAdmin):
    list_display = ('userId', 'quantity',)


@admin.register(CartItem)
class CartItemAdmin(ImportExportModelAdmin):
    list_display = ('cartId', 'productId', 'quantity', 'create_at',)


@admin.register(FileUpload)
class FileUploadAdmin(ImportExportModelAdmin):
    list_display = ('cartId',)
