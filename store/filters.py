from django_filters.rest_framework import FilterSet

from . import models 


class ProductFilter(FilterSet):
    class Meta:
        model = models.Product 
        fields = {
            'inventory':['exact']
        }

