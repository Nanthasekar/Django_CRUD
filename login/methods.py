from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth.models import User
from django.contrib.auth import login as django_login

def login(request, **kwargs):
        username = request.GET.get('username', '')
        password = request.GET.get('password', '')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                django_login(request, user)
                return True
            else:
                return True
        else:
            return False