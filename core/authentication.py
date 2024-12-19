import jwt,datetime
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

class Jwtauthentication(BaseAuthentication):
    def authenticate(self,request):
                auth = get_authorization_header(request).split()
        
                if auth and len(auth) == 2 :
                        token = auth[1].decode('utf-8')
                        id = decode_access_token(token)
                        
                        user = Users.objects.get(pk=id)
                        
                        if user:
                            serializer = Userserializer(user)
                            return Response(serializer.data)
                        
                    
                    
                raise exceptions.AuthenticationFailed('unathenticated')

def create_access_token(id):
     return jwt.encode({
         'user_id':id,
         'exp':datetime.datetime.utcnow()+datetime.timedelta(seconds=300),
         'iat':datetime.datetime.utcnow()
     },'access_secret',algorithm='HS256')
     
def decode_access_token(token):
    try:
        payload = jwt.decode(token,'access_secret',algorithms='HS256')
        return payload['user_id']
    except Exception as e :
        print(e)
        raise exceptions.AuthenticationFailed('unauthenticated')
     
def create_refresh_token(id):
    return jwt.encode({
        'user_id':id,
        'exp':datetime.datetime.utcnow()+datetime.timedelta(days=7),
        'iat':datetime.datetime.utcnow()
    },'refresh_token',algorithm='HS256')
     
     
