from django.db.models.signals import post_save
from django.dispatch import receiver 
from django.conf import settings 

from store import models


@receiver(post_save,sender=settings.AUTH_USER_MODEL)
def create_customer_profile_for_newly_created_user(sender,created,instance,**kwargs):
    if created :
        models.Customer.objects.create(user=instance)
