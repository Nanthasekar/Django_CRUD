from tastypie.validation import Validation
import json

from crud.models import Blog

class BlogValidation(Validation):
    def create_valid(self, request):
        body = json.loads(request.body)
        title = body.get("title", "")
        error = []
        if not title:
            return "title should not empty"
        return self.check_title(title)

    def update_valid(self, request):
        body = json.loads(request.body)
        idd = body.get("blog_id", "")
        if not idd:
            return "blog id should be mention"
        return self.check_user(request, idd)
    
    def delete_valid(self, request):
        body = json.loads(request.body)
        idd = body.get("blog_id", "")
        if not idd:
            return "blog id should be mention"
        return self.check_user(request, idd)

    def check_title(self, title):
        try:
            blog_obj = Blog.objects.get(title=title)
            if blog_obj:
               return "title already present" 
        except Exception as e:
            pass
        return ""

    def check_user(self, request, idd):
        try:
            blog_obj = Blog.objects.get(pk=int(idd))
            user_name = blog_obj.username
            if request.user.username != user_name:
                return "don't have permission to perform this action"
            return ""
        except Blog.DoesNotExist:
            return "blog not found"
        except Exception as e:
            return str(e)
            

       