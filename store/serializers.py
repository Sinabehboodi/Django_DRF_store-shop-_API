from rest_framework import serializers
from django.utils.text import slugify 
from django.db import transaction 
from decimal import Decimal


from . import models



DOLLORS_TO_RIALS = 500000


class CategorySerializer(serializers.Serializer):
    class Meta:
        model = models.Category
        fields = ['id','title','description','num_of_products']
        
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)
    num_of_products = serializers.IntegerField(source='products.count',read_only=True)
    


class ProductSerializer(serializers.Serializer):
    class Meta:
        model = models.Product
        fields = ['id', 'name', 'unit_price', 'inventory', 'category', 'price_to_rial', 'price_after_tax', 'slug', 'description']
        
    id = serializers.IntegerField()
    inventory = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    slug = serializers.SlugField()
    description = serializers.CharField(max_length=500)
    '''Could not resolve URL for hyperlinked relationship using view name "category_detail". You may have failed to include the related model in your API, or incorrectly configured the `lookup_field` attribute on this field.'''
    # category = serializers.HyperlinkedRelatedField(
    #     queryset = models.Category.objects.all(),
    #     view_name = 'category_detail'
    # )
    price_to_rial = serializers.SerializerMethodField()
    price_after_tax = serializers.SerializerMethodField()
    
    def get_price_to_rial(self,product:models.Product):
        return int(product.unit_price * DOLLORS_TO_RIALS)
    
    def get_price_after_tax(self,product:models.Product):
        return round(product.unit_price * Decimal(1.09), 2)
    
    def validate(self, data):
        if len(data['name']) < 6 :
            raise serializers.ValidationError('product name length should be at least 6 !')
        return data 
    
    def create(self,validated_data):
        product = models.Product(**validated_data)
        product.slug = slugify(product.name)
        product.save()
        return product
    
 
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = ['id', 'name', 'product', 'body']
        
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    product = serializers.CharField(max_length=255)
    body = serializers.CharField(max_length=500)
    
    
    def create(self, validated_data):
        product_id = self.context['product_pk']
        
        return models.Comment.objects.cerate(product_id = product_id,**validated_data)
    
    
class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['id','name','unit_price']
        
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    unit_price = serializers.IntegerField()
    
    
class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ['id','product','quantity']
        
    id = serializers.IntegerField()
    product = serializers.CharField(max_length=255)
    quantity = serializers.IntegerField()
    
    def create(self, validated_data):
        cart_id = self.context['cart_pk']
        product = validated_data.get('product')
        quantity = validated_data.get('quantity')
        
        try:
            cart_item = models.CartItem.objects.get(cart_id=cart_id,product_id=product.id)
            
            cart_item += quantity
            cart_item.save()
            
        except models.CartItem.DoesNotExist:
            cart_item = models.CartItem.objects.create(cart_id=cart_id,**validated_data)
            
        self.instance = cart_item
         
        return cart_item
    
    
class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ['quantity']
        
    quantity = serializers.IntegerField()
    
    
    
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ['id','product','quantity','product','item_total']
        
    id = serializers.IntegerField()
    product = serializers.CharField(max_length=255)
    quantity = serializers.IntegerField()
    product = CartProductSerializer()
    item_total = serializers.SerializerMethodField()
    
    def get_item_total(self,cart_item:models.CartItem):
        return cart_item.quantity * cart_item.product.unit_price
        
    

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = ['id','created_at','items']  
        read_only_fields = ['id','items']
        
    id = serializers.UUIDField(read_only=True)  
    created_at = serializers.DateTimeField()
    items = CartItemSerializer(many=True,read_only=True)
    total_price = serializers.SerializerMethodField()
    
    def get_total_price(self,cart:models.Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])
    
    
    
class OrderCustomersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = ['id','first_name','last_name','email']
        
        
    id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=255,source='user.first_name')
    last_name = serializers.CharField(max_length=255,source='user.last_name')
    email = serializers.EmailField(source='user.email')
    
    
    
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = ['id','user','birth_date',]
        read_only_fields = ['user']
        
        
    id = serializers.IntegerField()
    user = serializers.CharField(max_length=255)
    birth_date = serializers.DateField()
    
    
    
class OrderItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['id','name','unit_price']
        
        
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    unit_price = serializers.IntegerField()
    
    
    
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderItem
        fields = ['id','product','quantity','unit_price']
        
    
    id = serializers.IntegerField()
    product = OrderItemProductSerializer()
    quantity = serializers.IntegerField()
    unit_price = serializers.IntegerField()
    
    

class OrderForAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ['id','customer_id','status','datetime_created','items','customer']
    
    
    id = serializers.IntegerField()
    customer_id = serializers.CharField(max_length=255)
    status = serializers.CharField(max_length=1)
    datetime_created = serializers.DateTimeField()
    items = OrderItemSerializer()   
    customer = OrderCustomersSerializer() 



class OrderCreateSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    
    def validate_cart_id(self,cart_id):
        try:
            if models.Cart.objects.prefetch_related('items').get(id=cart_id).items.count() == 0:
                raise serializers.ValidationError('Your cart is empty . please add some products to it first.')
        except models.Cart.DoesNotExist:
            raise serializers.ValidationError('Ther is no cart with this cart id !')
        
        return cart_id
    
    def save(self,**kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user_id = self.context['user_id']
            customer = models.Customer.objects.get(user_id=user_id)
            
            order = models.Order()
            order.customer = customer
            order.save()
            
            cart_items = models.CartItem.objects.select_related('product').filter(cart_id=cart_id)
            
            order_items = [
                models.OrderItem(
                    order=order,
                    product=cart_item.product,
                    unit_price=cart_item.product.unit_price,
                    quantity=cart_item.quantity,
                ) for cart_item in cart_items
            ]
        
            models.OrderItem.objects.bulk_create(order_items)
            models.Cart.objects.get(pk=cart_id).delete()
            
            return order 
        

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order 
        fields = ['status']
        
    status = serializers.CharField(max_length=1)
    
    
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ['id','customer_id','status','datetime_created','items']
    
    
    id = serializers.IntegerField()
    customer_id = serializers.CharField(max_length=255)
    status = serializers.CharField(max_length=1)
    datetime_created = serializers.DateTimeField()
    items = OrderItemSerializer()
   
   
   
 