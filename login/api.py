from tastypie.resources import Resource, ModelResource
from tastypie.utils.urls import trailing_slash
from tastypie.authentication import BasicAuthentication
from tastypie.http import HttpForbidden, HttpUnauthorized
from tastypie.serializers import Serializer

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder

from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login, logout as django_logout
from django.contrib.auth.models import User
from django.conf.urls import url
from .custom_validation import AwesomeValidation
import json


valid_obj = AwesomeValidation()

class MyModelResource(Resource):
    class Meta:
        resource_name = 'users'

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/login%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login'), name="api_login"),

            url(r"^(?P<resource_name>%s)/create_user%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('create_user'), name="api_create_user"),

            url(r"^(?P<resource_name>%s)/user_list%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('user_list'), name="api_user_list"),


            url(r"^(?P<resource_name>%s)/logout%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('logout'), name="api_logout"),

        ]

    #api: http://127.0.0.1:8000/api/v1/users/create_user/
    #params: format=>json, data= {'username':'user', 'password':'password'}
    def create_user(self, request, *args, **kwargs):
        self.method_check(request, allowed=['post'])

        valid_res = valid_obj.is_valid(request)
        if valid_res:
            return self.error_response(request, { 'status': False, 'error':valid_res})
        try:
            body = json.loads(request.body)
            username = body.get("username")
            password = body.get("password")
            user = authenticate(username=username, password=password)
            if not user:
            	user = User.objects.create_user(username=username, password=password)
            	return self.create_response(request, 
            		                        {'status': True, 
            		                        'message':'new user has created'}
            		                        )
            else:
            	return self.error_response(request, 
            		                      {'status': False,
            		                      'message':'user already present'}
            		                      )
        except Exception as e:
            return self.error_response(request, 
            	                       {'status': False, 
            	                      'message':str(e)}
            	                      )

    #api: http://127.0.0.1:8000/api/v1/users/login/
    #params: format=>json, data= {'username':'user', 'password':'password'}
    def login(self, request, *args, **kwargs):
        self.method_check(request, allowed=['post'])
        try:
            body = json.loads(request.body)
            username = body.get("username")
            password = body.get("password")
            user = authenticate(username=username, password=password)
            if user:
                django_login(request, user)
                return self.create_response(request, 
                	                       {'status': True, 
                	                       'message': 'login successfully'})      
            else:
                return self.error_response(request, 
                	                       {'status': True, 
                	                       'message': 'invalid user'}, 
                	                       HttpUnauthorized)
        except Exception as e:
            return self.error_response(request,
            	                       {'success':False, 
            	                       "message":str(e)}, 
            	                       HttpForbidden)

    #api: http://127.0.0.1:8000/api/v1/users/user_list/
    def user_list(self, request, *args, **kwargs):
        self.method_check(request, allowed=['get'])
        try:
            if not request.user.is_authenticated:
                return self.error_response(request, 
                	                       { 'status': False, 
                	                        'message': 'Unauthorized' }, 
                	                       HttpUnauthorized)
            queryset = User.objects.all()
            if queryset:
                data_list = serializers.serialize('json', queryset)
                return HttpResponse(data_list, content_type="text/json-comment-filtered")
            else:
        	    return self.error_response(request, 
        	    	                       {'status':False, 
        	    	                       "message":"No Record Found"},
        	    	                       HttpForbidden)
        except Exception as e:
        	return self.error_response(request,
        		                       {'status':False, 
        		                       "message":"No Record Found"}, 
        		                       HttpForbidden)

    #api: http://127.0.0.1:8000/api/v1/users/logout/
    def logout(self, request, *args, **kwargs):
    	self.method_check(request, allowed=['get'])
    	if request.user.is_authenticated:
    		print('hi')
    		django_logout(request)
    	return self.create_response(request, 
    		            {'status': True,
    		            'message': 'logout successfully'})

