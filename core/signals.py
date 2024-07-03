from django.dispatch import receiver 
from store.signals import order_ceated 



@receiver(order_ceated)
def after_order_created(sender,**kwargs):
    print(f'New order is created {kwargs['order'].id}')

