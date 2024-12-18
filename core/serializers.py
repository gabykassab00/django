from rest_framework.serializers import ModelSerializer
from .models import Users

class Userserializer(ModelSerializer):
    class Meta:
        model = Users
        fields = ['id','email','password']
        extra_kwargs= {
            'password':{'write_only':True}
        }