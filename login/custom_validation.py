from tastypie.validation import Validation
import json

class AwesomeValidation(Validation):
    def is_valid(self, request):
        body = json.loads(request.body)
        username = body.get("username")
        password = body.get("password")
        if not username:
            return {"username empty": "username should not be empty"}
        if username == 'admin':
            return {'admin user': "username should not be admin user"}
        return {}