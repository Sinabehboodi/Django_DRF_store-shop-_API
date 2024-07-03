from django.contrib import admin, messages
from django.db.models import Count
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode

from . import models


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    fields = ['product', 'quantity', 'unit_price']
    extra = 1


class InventoryFilter(admin.SimpleListFilter):
    LESS_THAN_3 = '<3'
    BETWEEN_3_AND_10 = '3<=10'
    MORE_THAN_10 = '>10'
    title = 'Critical Inventory Status'
    parameter_name = 'inventory'
    
    def lookups(self, request, model_admin):
        return [
            (InventoryFilter.LESS_THAN_3, 'High'),
            (InventoryFilter.BETWEEN_3_AND_10, 'Medium'),
            (InventoryFilter.MORE_THAN_10, 'Ok'),
        ]
        
    def queryset(self, request, queryset):
        if self.value() == InventoryFilter.LESS_THAN_3:
            return queryset.filter(inventory__lt=3)
        if self.value() == InventoryFilter.BETWEEN_3_AND_10:
            return queryset.filter(inventory__range=(3,10))
        if self.value() == InventoryFilter.MORE_THAN_10:
            return queryset.filter(inventory__gt=10)

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'inventory','inventory_status','category','product_category', 'unit_price', 'num_of_comments', 'product_category']
    list_per_page = 10
    list_editable = ['unit_price']
    list_select_related = ['category']
    list_filter = ['datetime_created', InventoryFilter, 'category']
    actions = ['clear_inventory']
    search_fields = ['name',]
    exclude = ['discounts',]
    readonly_fields = ['category']
    prepopulated_fields = {
        'slug': ['name',]
    }
    
    @admin.action(description='clear inventory')
    def clear_inventory(self,request,queryset):
        update_clear = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{update_clear} of products inventories cleaned to zero',
            messages.WARNING,
        )
    
    def inventory_status(self,product:models.Product):
        if product.inventory < 10 :
            return 'Low'
        if product.inventory > 50 :
            return 'High'
        return 'Medium'
    
    @admin.display(ordering='category_id')
    def product_category(self,product:models.Product):
        return product.category.title
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('comments').annotate(comments_count=Count('comments'))
    
    @admin.display(description='# comments', ordering='comments_count')
    def num_of_comments(self, product:models.Product):
        url = (
            reverse('admin:store_comment_changelist')
            +'?'
            +urlencode({
                'product__id':product.id,
            })
        )
        
        return format_html('<a href="{}">{}</a>',url,product.comments_count)
    
    @admin.display(ordering='category__title')
    def product_category(self, product:models.Product):
        return product.category.title 
            
    
@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status','num_of_items', 'datetime_created']
    list_editable = ['status']
    list_per_page = 10
    ordering = ['datetime_created']
    inlines = [OrderItemInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items').annotate(items_count=Count('items'))
    
    @admin.display(ordering='items_count')
    def num_of_items(self,order:models.Order):
        return order.items_count
    
    
@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'status']
    list_editable = ['status']
    list_per_page = 10
    list_display_links = ['id', 'product']
    autocomplete_fields = ['product',]
    
    
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email']
    list_per_page = 10
    ordering = ['user__last_name', 'user__first_name', ]
    search_fields = ['first_name__istartswith', 'last_name__istartwith']
    
    
    def first_name(self,customer:models.Customer):
        return customer.first_name
    
    def last_name(self,customer:models.Customer):
        return customer.last_name
    
    def email(self,customer:models.Customer):
        return customer.email
    
@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'unit_price']
    autocomplete_fields = ['product',]
    
    
class CartItemInline(admin.TabularInline):
    model = models.CartItem
    fields = ['id','product','quantity']
    extra = 1
    
    
@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id','created_at']
    inlines = [CartItemInline]
