from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS, Resource
from tastypie.authentication import BasicAuthentication
from tastypie.utils.urls import trailing_slash
from tastypie.http import HttpForbidden, HttpUnauthorized
from tastypie.serializers import Serializer

from django.conf.urls import url
from django.contrib.auth.models import User
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder

from .blog_validation import BlogValidation
from crud.models import Blog

import json


blog_valid = BlogValidation()

class CRUDResource(Resource):
    class Meta:
        resource_name = 'blog'

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/create%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('create'), name="api_create"),
            
            url(r"^(?P<resource_name>%s)/update%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('update'), name="api_update"),

            url(r"^(?P<resource_name>%s)/read%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('read'), name="api_read"),

            url(r"^(?P<resource_name>%s)/delete%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('delete'), name="api_delete"),

        ]


 
    #api: http://127.0.0.1:8000/api/v1/blog/create/
    #params: format=>json, data= {'title':'title name', 'message':'message name'}
    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.error_response(request, { 'status': False, 'message': 'Unauthorized' }, HttpUnauthorized)
        self.method_check(request, allowed=['post'])

        is_valid = blog_valid.create_valid(request)
        if is_valid:
        	return self.error_response(request, {'status': False, 'error':is_valid})
        try:
        	body = json.loads(request.body)
        	title = body.get('title')
        	message = body.get('message', '')
        	username = request.user.username

        	blog = Blog()
        	blog.title = title
        	blog.message = message
        	blog.username = request.user.username
        	blog.created_by = User.objects.get(id=int(request.user.id))
        	blog.save()

        	blog_list = {}
        	blog_list['id'] = blog.id
        	blog_list['title'] = blog.title
        	blog_list['message'] = blog.message
        	blog_list['username'] = blog.username
        	blog_list['created_by_id'] = blog.created_by_id
        	blog_list['created_by'] = blog.created_by
        	return self.create_response(request, {'status': True , 'data':blog_list})
        except Exception as e:
            return self.error_response(request, { 'status': False, 'error':str(e)})

    #api: http://127.0.0.1:8000/api/v1/blog/update/
    #params: format=>json, data= {'blog_id': 'id', message':'message name'}
    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.error_response(request, { 'status': False, 'message': 'Unauthorized' }, HttpUnauthorized)
        self.method_check(request, allowed=['put'])

        is_valid = blog_valid.update_valid(request)
        if is_valid:
        	return self.error_response(request, {'status': False, 'error':is_valid})

        try:
            body = json.loads(request.body)
            blog_id = body.get('blog_id', 0)
            message = body.get('message', '')

            username = request.user.username
            blog = Blog.objects.get(pk=int(blog_id))
            if username != blog.username:
                return self.error_response(request, {'status': False, 'error': "You don't have permission to updated the records"})

            if blog:
                blog.message = message
                blog.save()

                blog_list = {}
                blog_list['id'] = blog.id
                blog_list['title'] = blog.title
                blog_list['message'] = blog.message
                blog_list['username'] = blog.username
                return self.create_response(request, {'status': True , 'data':blog_list})
            return self.error_response(request, { 'status': False, 'error':"Blog not existed"})
        except Blog.DoesNotExist:
        	return self.error_response(request, { 'status': False, 'error':"Blog not existed"})
        except Exception as e:
            return self.error_response(request, { 'status': False, 'error':str(e)})

    #api: http://127.0.0.1:8000/api/v1/blog/read/
    #params(optional): format=>json, data= {'user_id':'id'}
    def read(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.error_response(request, { 'status': False, 'message': 'Unauthorized' }, HttpUnauthorized)
        self.method_check(request, allowed=['get'])

        try:
            body = json.loads(request.body)
            blog_id = body.get('user_id', 0)

            if blog_id:
                blog_lists = Blog.objects.filter(created_by_id=int(blog_id))
            else:
                blog_lists = Blog.objects.all()
         
            if blog_lists:
                blogs = []
                for blog in  blog_lists:
                    blog_temp = {}
                    blog_temp['id'] = blog.id
                    blog_temp['title'] = blog.title
                    blog_temp['message'] = blog.message
                    blog_temp['username'] = blog.username
                    blog_temp['created_by'] = blog.created_by
                    blog_temp['created_by_id'] = blog.created_by_id
                    blogs.append(blog_temp)
                return self.create_response(request, {'status': True , 'data':blogs})
            return self.error_response(request, { 'status': False, 'error':"Blog is empty"})
        except Blog.DoesNotExist:
            return self.error_response(request, { 'status': False, 'error':"Blog not existed"})
        except Exception as e:
            return self.error_response(request, { 'status': False, 'error':str(e)})

    #api: http://127.0.0.1:8000/api/v1/blog/delete/
    #params: format=>json, data= {'blog_id':'id'}
    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.error_response(request, { 'status': False, 'message': 'Unauthorized' }, HttpUnauthorized)
        self.method_check(request, allowed=['delete'])

        is_valid = blog_valid.delete_valid(request)
        if is_valid:
        	return self.error_response(request, {'status': False, 'error':is_valid})

        try:
            body = json.loads(request.body)
            blog_id = body.get('blog_id', 0)
            Blog.objects.get(pk=int(blog_id)).delete()
            return self.create_response(request, { 'status': True, 'message':"blog has delete"})
        except Blog.DoesNotExist:
            return self.error_response(request, { 'status': False, 'error':"Blog not existed"})
        except Exception as e:
            return self.error_response(request, { 'status': False, 'error':str(e)})
