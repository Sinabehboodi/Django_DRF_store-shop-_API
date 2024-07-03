from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()

router.register('products',views.ProductViewSet,basename='product')
router.register('categories',views.CategoryViewSet,basename='category')
router.register('carts',views.CartViewSet,basename='carts')
router.register('customers',views.CustomerViewSet,basename='customer')
router.register('orders',views.OrderViewSet,basename='order')

products_router = routers.NestedDefaultRouter(router,'products',lookup='product')
cart_items_router = routers.NestedDefaultRouter(router,'carts',lookup='cart')

products_router.register('comments',views.CommentViewSet,basename='product_comments')
cart_items_router.register('items',views.CartItemViewSet,basename='cart_items')



urlpatterns = router.urls + products_router.urls + cart_items_router.urls



