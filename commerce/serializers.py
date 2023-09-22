from rest_framework import serializers
from .models import *
from rest_framework import serializers
from .models import *
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied



# Product Category Serializer
class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'

# Store Serializer
class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'

# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        models = ProductReview
        fields = '__all__'

# CartItem Serializer
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class SaleHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleHistory
        fields = '__all__'

class ProductImgSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImg
        fields = ['id', 'image',]


class ProductSerializer(serializers.ModelSerializer):
    store = serializers.CharField(source='storeId.name', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'store', 'category', 'price','kilogram', 'stock', 'condition', 'create_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        product_imgs = instance.product_imgs.all()  # Assuming you've set related_name='product_imgs'
        if product_imgs:
            representation['productImgs'] = ProductImgSerializer(product_imgs, many=True).data
        return representation



class ProductModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'sku', 'category', 'description', 'price', 'created', 'featured',)

# class ProductImgSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductImg
#         fields = ['id', 'title', 'productId', 'url']

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'userId', 'name', 'create_at']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id','userId', 'quantity']

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['cartId', 'productId', 'quantity', 'create_at']
        
class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['imgFile']

class JoinSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='productId')
    class Meta:
        model = CartItem
        fields = ['cartId', 'productId', 'quantity','product_details', 'create_at']



class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer class for serializing order items
    """
    price = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'product', 'quantity',
                  'price', 'cost', 'created_at', 'updated_at', )
        read_only_fields = ('order', )

    def validate(self, validated_data):
        order_quantity = validated_data['quantity']
        product_quantity = validated_data['product'].quantity

        order_id = self.context['view'].kwargs.get('order_id')
        product = validated_data['product']
        current_item = OrderItem.objects.filter(
            order__id=order_id, product=product)

        if(order_quantity > product_quantity):
            error = {'quantity': _('Ordered quantity is more than the stock.')}
            raise serializers.ValidationError(error)

        if not self.instance and current_item.count() > 0:
            error = {'product': _('Product already exists in your order.')}
            raise serializers.ValidationError(error)

        if self.context['request'].user == product.seller:
            error = _('Adding your own product to your order is not allowed')
            raise PermissionDenied(error)

        return validated_data

    def get_price(self, obj):
        return obj.product.price

    def get_cost(self, obj):
        return obj.cost


class OrderReadSerializer(serializers.ModelSerializer):
    """
    Serializer class for reading orders
    """
    buyer = serializers.CharField(source='buyer.get_full_name', read_only=True)
    order_items = OrderItemSerializer(read_only=True, many=True)
    total_cost = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'buyer', 'shipping_address', 'billing_address', 'payment',
                  'order_items', 'total_cost', 'status', 'created_at', 'updated_at')

    def get_total_cost(self, obj):
        return obj.total_cost


class OrderWriteSerializer(serializers.ModelSerializer):
    """
    Serializer class for creating orders and order items

    Shipping address, billing address and payment are not included here
    They will be created/updated on checkout
    """
    buyer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'buyer', 'status', 'order_items',
                  'created_at', 'updated_at',)
        read_only_fields = ('status', )

    def create(self, validated_data):
        orders_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)

        for order_data in orders_data:
            OrderItem.objects.create(order=order, **order_data)

        return order

    def update(self, instance, validated_data):
        orders_data = validated_data.pop('order_items', None)
        orders = list((instance.order_items).all())

        if orders_data:
            for order_data in orders_data:
                order = orders.pop(0)
                order.product = order_data.get('product', order.product)
                order.quantity = order_data.get('quantity', order.quantity)
                order.save()

        return instance


class MarkProductSoldSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


class PromotionSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    promotion_plan_id = serializers.IntegerField()