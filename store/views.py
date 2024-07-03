from rest_framework.response import Response 
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.decorators import action
from django_filters.rest_framework import OrderingFilter, DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from . import models 
from . import serializers
from . import permissions
from . import signals



class ProductViewSet(ModelViewSet):
    serializer_class = serializers.ProductSerializer
    queryset = models.Product.objects.select_related('category').all()
    filter_backends = [DjangoFilterBackend,OrderingFilter,SearchFilter]
    ordering_fields = ['name','price','inventory']
    search_fields = ['title','category__title']
    pagination_class = PageNumberPagination
    
    permission_classes = [permissions.CustomDjangoModelPermissions]
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    
    def destroy(self,request,pk):
        product = get_object_or_404(models.Product.objects.select_related('category'),pk=pk)
        
        if product.order_items.count() > 0:
            return Response({'error':'Ther is some order items including the products . please remove them first.'})
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class CategoryViewSet(ModelViewSet):
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.prefetch_related('products').all()
    
    permission_classes = [permissions.IsAdminOrReadOnly]
    
    def destroy(self,request,pk):
        category = get_object_or_404(models.Category.objects.prefetch_related('products',pk=pk))
        
        if category.products.count() > 0:
            return Response({'error':'There is some products relating this category.please remove them first.'})
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class CommentViewSet(ModelViewSet):
    serializer_class = serializers.CommentSerializer
    queryset = models.Comment.objects.all()
    
    
    def get_queryset(self):
        product_pk = self.kwargs['product_pk']
        
        return models.Comment.objects.filter(product_id = product_pk).all()
    
    def get_serializer_context(self):
        return {'product_pk':self.kwargs['product_pk']}
    

class CartViewSet(CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,GenericViewSet):
    serializer_class = serializers.CartSerializer
    queryset = models.Cart.objects.prefetch_related('items__product').all()
    
    lookup_value_regex = '[0_9a_fa_F]{8}\_?[0_9a_fa_F]{4}\_?[0_9a_fa_F]{4}\_?[0_9a_fa_F]{4}\_?[0_9a_fa_F]{12}'
    
    

class CartItemViewSet(ModelViewSet):
    serializer_class = serializers.CartItemSerializer
    http_method_names = ['get','post','patch','delete']
    
    def get_queryset(self):
        cart_pk = self.kwargs['cart_pk']
        
        return models.CartItem.objects.select_related('product').filter(cart_id=cart_pk).all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return serializers.UpdateCartItemSerializer
        
        return serializers.CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_pk':self.kwargs['cart_pk']}
    
    

class CustomerViewSet(ModelViewSet):
    serializer_class = serializers.CustomerSerializer
    queryset = models.Customer.objects.all()
    
    permission_classes = [IsAdminUser,IsAuthenticated]
    
    
    @action(detail=False,methods=['GET','PUT']) 
    def me(self,request):
        user_id = request.user.id
        customer = models.Customer.objects.get(user_id=user_id)
        if request.method == 'GET':
            serializer = serializers.CustomerSerializer(customer) 
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = serializers.CustomerSerializer(customer,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
  
  
    @action(detail=True,permission_classes=[permissions.SendPrivateEmailToCustomerPermission])
    def send_private_email(self,request,pk):
        return Response(f'sending email to customer {pk=}')
    
    
    
class OrderViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get','post','patch','delete','option','head']
    
    def get_permissions(self):
        if self.request.method in ['PATCH','DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    
    def get_queryset(self):
        
        queryset = models.Order.objects.prefetch_related(
            Prefetch(
                    'items',
                     queryset=models.OrderItem.objects.select_related('product')
                    )
            ).select_related('customer__user').all()
        
        if self.request.user.is_staff:
            return queryset 
        
        return queryset.filter(customer__user_id=self.request.user.id)
        
        
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.OrderCreateSerializer
        
        if self.request.method == 'PATCH':
            return serializers.OrderUpdateSerializer
        
        if self.request.user.is_staff:
            return serializers.OrderForAdminSerializer
        
        return serializers.OrderSerializer    
    
    
    def get_serializer_context(self):
        return {'user_id': self.request.user.id}
    
    
    def create(self,request,*args,**kwargs):
        create_order_serializer = serializers.OrderCreateSerializer(
            data=request.data,
            context = {'user_id': self.request.user.id}
            )
        create_order_serializer.is_valid(raise_exception=True)
        created_order = create_order_serializer.save()
        
        signals.order_ceated.send_robust(self.__class__,order=created_order)
        
        serializer = serializers.OrderSerializer(created_order)
        
        return Response(serializer.data)
    
        
    
