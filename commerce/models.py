from django.db import models
from datetime import datetime
from user.models import *
from django.db import models
from user.models import *
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property



# Create your models here.

class ProductCategory(models.Model):
    name = models.CharField(max_length = 250)
    image = models.ImageField(upload_to='product_images')
    description = models.TextField()
    
    def __str__(self):
        return self.name
    

class Store(models.Model):
    userId = models.ForeignKey(User, on_delete = models.CASCADE)
    name = models.CharField( max_length=100)
    create_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class SaleLocation(models.Model):
    name = models.CharField(max_length = 250, blank = True, null = True)


class SaleHistory(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    selling_price = models.CharField(max_length=100)
    sale_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale of {self.product.title} on {self.sale_date}"

class Product(models.Model):
    title = models.CharField(max_length=500)
    description = models.TextField()
    business = models.ForeignKey(BusinessAccount, on_delete=models.CASCADE)
    category = models.ForeignKey(ProductCategory, on_delete = models.CASCADE)
    price = models.CharField( max_length=100)
    sale_location = models.ForeignKey(SaleLocation, on_delete = models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)
    is_trending = models.BooleanField(default=False, verbose_name='Trending')
    is_sold = models.BooleanField(default=False, verbose_name='Sold')
    # New fields for promotions
    is_promoted = models.BooleanField(default=False, verbose_name='Promoted')
    promotion_plan = models.ForeignKey('PromotionPlan', on_delete=models.SET_NULL, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.is_sold and not self.salehistory_set.exists():
            SaleHistory.objects.create(product=self, selling_price=self.price)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name



class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)  # Rating from 1 to 5, you can customize this
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.product.name} Review'

# class ProductDetail(models.Model):
#     productId = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_details')
#     organic = models.IntegerField()
#     expiration = models.IntegerField()
#     review = models.CharField(max_length = 200)
#     gram = models.IntegerField()


class PromotionPlan(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class ProductImg(models.Model):
    productId = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_imgs')
    image = models.ImageField(upload_to='product_images')
    # url = models.URLField(max_length=200, blank=True, null = True)

class Cart(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField()

class CartItem(models.Model):
    cartId = models.ForeignKey(Cart, on_delete = models.CASCADE)
    productId = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    create_at = models.DateTimeField(auto_now_add=True)

def upload_location(instance, filename):
    ext = filename.split(".")[-1]
    return "%s/%s.%s" % ("img", datetime.now(), ext)

class FileUpload(models.Model):
    cartId =  models.ImageField(upload_to=upload_location, height_field=None, width_field=None, max_length=None)


class Order(models.Model):
    PENDING = 'P'
    COMPLETED = 'C'

    STATUS_CHOICES = ((PENDING, _('pending')), (COMPLETED, _('completed')))

    buyer = models.ForeignKey(
        User, related_name='orders', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=PENDING)
    shipping_address = models.ForeignKey(
        "DeliveryAddress", related_name='shipping_orders', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        "DeliveryAddress", related_name='billing_orders', on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at', )

    def __str__(self):
        return self.buyer.get_full_name()

    @cached_property
    def total_cost(self):
        """
        Total cost of all the items in an order
        """
        return round(sum([order_item.cost for order_item in self.order_items.all()]), 2)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="order_items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="product_orders", on_delete=models.CASCADE)
    quantity = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at', )

    def __str__(self):
        return self.order.buyer.get_full_name()

    @cached_property
    def cost(self):
        """
        Total cost of the ordered item
        """
        return round(self.quantity * self.product.price, 2)


class DeliveryAddress(models.Model):
    # Address options
    BILLING = 'B'
    SHIPPING = 'S'

    ADDRESS_CHOICES = ((BILLING, _('billing')), (SHIPPING, _('shipping')))

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='addresses',
        on_delete=models.CASCADE
    )
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)
    address = models.ForeignKey(Address, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at', )

    def __str__(self):
        return str(self.user.get_full_name())

DURATION_CHOICES = (
    ('24 hours', '24 hours'),
    ('48 hours', '48 hours'),
    ('72 hours', '72 hours'),
    ('1 week', '1 week'),
    ('2 week', '2 week'),
    ('1 month', '1 month'),
    ('3 months', '3 months'),
    ('1 year', '1 year'),
)

class Advert(models.Model):
    title = models.CharField(max_length = 250)
    category = models.CharField(max_length = 250, choices = DURATION_CHOICES)
    duration = models.IntegerField()
    custom_duration_start = models.DateTimeField()
    custom_duration_end = models.DateTimeField()
    image = models.ImageField(upload_to = 'advert-image/')
    note = models.TextField()

    def __str__(self):
        return self.title
