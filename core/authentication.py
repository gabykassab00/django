import jwt,datetime
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication,get_authorization_header
from core.models import Users
from .serializers import Userserializer
class Jwtauthentication(BaseAuthentication):
    def authenticate(self,request):
                auth = get_authorization_header(request).split()
        
                if auth and len(auth) == 2 :
                        token = auth[1].decode('utf-8')
                        id = decode_access_token(token)
                        
                        user = Users.objects.get(pk=id)
                        
                        return (user,None) 
                        
                    
                    
                raise exceptions.AuthenticationFailed('unathenticated')

def create_access_token(id):
     return jwt.encode({
         'user_id':id,
         'exp':datetime.datetime.utcnow()+datetime.timedelta(seconds=3000000),
         'iat':datetime.datetime.utcnow()
     },'access_secret',algorithm='HS256')
     
def decode_access_token(token):
    try:
        payload = jwt.decode(token,'access_secret',algorithms='HS256')
        return payload['user_id']
    except  :
        raise exceptions.AuthenticationFailed('unauthenticated')
     
def create_refresh_token(id):
    return jwt.encode({
        'user_id':id,
        'exp':datetime.datetime.utcnow()+datetime.timedelta(days=7),
        'iat':datetime.datetime.utcnow()
    },'refresh_token',algorithm='HS256')
    
    
    
def decode_refresh_token(token):
    try:
        payload = jwt.decode(token,'refresh_secret',algorithms='HS256')
        return payload['user_id']
    except :
        raise exceptions.AuthenticationFailed('unauthenticated')
    
     
     
