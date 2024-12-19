import jwt,datetime


def create_access_token(id):
     return jwt.encode({
         'user_id':id,
         'exp':datetime.datetime.utcnow()+datetime.timedelta(seconds=300),
         'iat':datetime.datetime.utcnow()
     },'access_secret',algorithm='HS256')
     
def create_refresh_token(id):
    return jwt.encode({
        'user_id':id,
        'exp':datetime.datetime.utcnow()+datetime.timedelta(days=7),
        'iat':datetime.datetime.utcnow()
    },'refresh_token',algorithm='HS256')
     