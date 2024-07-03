from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from uuid import uuid4 

USER = get_user_model()

class Category(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=500,blank=True)
    top_product = models.ForeignKey('Product',on_delete=models.SET_NULL,blank=True,null=True,related_name='+')
    
    
    def __str__(self):
        return f'{self.id}. {self.title}'
    
    
class Discount(models.Model):
    discount = models.FloatField()
    description = models.CharField(max_length=255)
    
    def __str__(self):
        return f'{str(self.discount)} | {self.description}'


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category,on_delete=models.PROTECT,related_name='products')
    unit_price = models.DecimalField(max_digits=6,decimal_places=2)
    discount = models.ManyToManyField(Discount,blank=True,related_name='products')
    slug = models.SlugField()
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.name}'
    
    
class Customer(models.Model):
    user = models.OneToOneField(USER,on_delete=models.PROTECT)
    phone_number = models.CharField(max_length=255)
    birth_date = models.DateField(null=True,blank=True)
    
    class Meta:
        permissions = [
            ('send_private_email','you can send private email to user by the button.')
        ]    
    
    @property
    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'
    
    @property
    def first_name(self):
        return self.user.first_name
    
    @property 
    def last_name(self):
        return self.user.last_name
    
    @property
    def email(self):
        return self.user.email
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    
    
class OrderManager(models.Manager):
    def get_unpaid(self):
        return self.get_queryset().filter(status=Order.ORDER_STATUS_UNPAID)
    
    
class UnpaidOrderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.ORDER_STATUS_UNPAID)
    
    
class Order(models.Model):
    ORDER_STATUS_PAID = 'p'
    ORDER_STATUS_UNPAID = 'u'
    ORDER_STATUS_CANCELED = 'c'
    ORDER_STATUS = [
        (ORDER_STATUS_PAID, 'Paid'),
        (ORDER_STATUS_UNPAID, 'Unpaid'),
        (ORDER_STATUS_CANCELED, 'Canceled'),
    ]
    customer = models.ForeignKey(Customer,on_delete=models.PROTECT,related_name='orders')
    status = models.CharField(max_length=1,choices=ORDER_STATUS,default=ORDER_STATUS_UNPAID)
    
    datetime_created = models.DateTimeField(auto_now_add=True)
    
    
    
    def __str__(self):
        return f'order id = {self.id}'
    
    
class CommentManager(models.Manager):
    def get_approved(self):
        return self.get_queryset().filter(status=Comment.COMMENT_STATUS_APPROVED)
    
    
class ApprovedCommentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Comment.COMMENT_STATUS_APPROVED)
    
    
class Comment(models.Model):
    COMMENT_STATUS_WAITING = 'w'
    COMMENT_STATUS_APPROVED = 'a'
    COMMENT_STATUS_NOT_APPROVED = 'na' 
    COMMENT_STATUS = [
        (COMMENT_STATUS_WAITING, 'Waiting'),
        (COMMENT_STATUS_APPROVED, 'Approved'),
        (COMMENT_STATUS_NOT_APPROVED, 'Not Approved'),
    ]
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='comments')
    name = models.CharField(max_length=255)
    body = models.TextField()
    datetime_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2,choices=COMMENT_STATUS,default=COMMENT_STATUS_WAITING)
    
        
class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.PROTECT,related_name='items')
    product = models.ForeignKey(Product,on_delete=models.PROTECT,related_name='order_items')
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6,decimal_places=2)
    
    class Meta:
        unique_together = [['order','product']]
        
        
class Cart(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='cart_items')
    quantity = models.PositiveSmallIntegerField()
    
    class Meta:
        unique_together = [['cart','product']]
        
    
    
    
    

    