from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *
# Register your models here.


@admin.register(Store)
class StoreAdmin(ImportExportModelAdmin):
    list_display = ('userId', 'name', 'create_at')


@admin.register(ProductCategory)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ('name', 'description')


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ('title', 'storeId', 'category', 'price', 'kilogram', 'stock',
                    'condition', 'is_exclusive', 'is_best_selling', 'is_promo', 'is_meat',)
    list_filter = ('is_exclusive', 'is_best_selling', 'is_promo', 'is_meat',
                   'create_at', 'storeId', 'category',)  # Add filters for the desired fields
    # Enable in-place editing for the fields
    list_editable = ('is_exclusive', 'is_best_selling', 'is_promo', 'is_meat')


@admin.register(ProductImg)
class ProductImgAdmin(ImportExportModelAdmin):
    list_display = ('productId', 'image',)


@admin.register(ProductDetail)
class ProductDetailAdmin(ImportExportModelAdmin):
    list_display = ('productId', 'organic', 'expiration', 'review', 'gram')


@admin.register(Cart)
class CartAdmin(ImportExportModelAdmin):
    list_display = ('userId', 'quantity',)


@admin.register(CartItem)
class CartItemAdmin(ImportExportModelAdmin):
    list_display = ('cartId', 'productId', 'quantity', 'create_at',)


@admin.register(FileUpload)
class FileUploadAdmin(ImportExportModelAdmin):
    list_display = ('cartId',)
