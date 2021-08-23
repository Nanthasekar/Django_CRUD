from django.contrib.auth.models import User
from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import BasicAuthentication



class ExampleResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'example'
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'resource_uri']
        filtering = {
            'username': ALL,
        }
        