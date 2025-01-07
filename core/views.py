from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions
from .serializers import Userserializer
from .models import Users,Usertoken,Reset
from .authentication import create_access_token,create_refresh_token,decode_access_token,Jwtauthentication,decode_refresh_token
from rest_framework.authentication import get_authorization_header
import datetime,random,string
from django.core.mail import send_mail
from google.oauth2 import id_token
from google.auth.transport.requests import Request as googlereq
from rest_framework.parsers import MultiPartParser,FormParser
import os



class Registerapiview(APIView):
    def post(self,request):
        data = request.data 
        
        # print(f"Received data: {data}")
        
        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('passwords do not match')
        
        serializer = Userserializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    

class Loginapiview(APIView):
    def post(self,request):
        print(f"Request data: {request.data}")
        

        email  =request.data['email']
        password = request.data['password']
        
        
        user = Users.objects.filter(email=email).first()
        
        if user is None:
            raise exceptions.AuthenticationFailed('invalid credentials')
        
        
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('invalid credentials')
        
        
        
        
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        
        
        Usertoken.objects.create(
            user_id=user.id,
            token=refresh_token,
            expired_at=datetime.datetime.utcnow() + datetime.timedelta(days=7)
        )
        
        
        response = Response()        
        
        response.set_cookie(key='refresh_token',value=refresh_token,httponly=True)
        response.data ={
            "token":access_token
        }
        return response
    
    
class Userapiview(APIView):
    authentication_classes = [Jwtauthentication]
    def get(self,request):
        return Response(Userserializer(request.user).data)
    

class Refreshapiview(APIView):
    def post(self,request):
        refresh_token = request.COOKIES.get('refresh_token')
        
        id = decode_refresh_token(refresh_token)
        
        if not Usertoken.objects.filter(
            user_id=id,
            token=refresh_token,
            expired_at__gt=datetime.datetime.now(tz=datetime.timezone.utc)
        ).exists():
            raise exceptions.AuthenticationFailed('unauthenticated')
        
        access_token = create_access_token(id)
        
        
        return Response({
            'token':access_token
        })
        
class Logoutapiview(APIView):
    def post (self,request):
        
        refresh_token = request.COOKIES.get('refresh_token')
        Usertoken.objects.filter(token=refresh_token).delete()        
        
        
        response = Response()
        response.delete_cookie(key='refresh_token')
        response.data = {
            'message':'sucess'
        }
        return response
    
    
class Forgotapiview(APIView):
    def post(self,request):
        email = request.data['email']
        token = ''.join(random.choice(string.ascii_lowercase+string.digits) for _ in range(10))
        
        Reset.objects.create(
            email=request.data['email'],
            token=token
        )
        
        url = 'http://localhost:3000/forgot/' + token
        
        send_mail(
            subject='Reset your password',
            message='click <a href= "%s">here</a> to reset your password' % url,
            from_email='from@example.com',
            recipient_list=[email]
        )
        
        return Response ({
            'message':'success'
        })
        
class Resetapiview(APIView):
    def post(self,request):
        data = request.data 
        
        if data['password'] !=data['password_confirm']:
            raise exceptions.APIException('password do not match')
        
        
        reset_password = Reset.objects.filter(token=data['token']).first()
        
        
        if not reset_password:
            raise exceptions.APIException('invalid link')
        
        user = Users.objects.filter(email=reset_password.email).first()
        
        if not user:
            raise exceptions.APIException('user not found !')
        
        user.set_password(data['password'])
        user.save()
        
        return Response({
            'message':'success'
        })
        
class Googleauthapiview(APIView):
    def post(self,request):
        token = request.data.get('token')
        if not token:
            return Response({'error':'token is required'},status=400)
        
        try :
            google_user = id_token.verify_token(token,googlereq())
        except ValueError:
            return Response({'error':'invalid google token'})
                
        user = Users.objects.filter(email=google_user['email']).first()
        
        if not user :
            user=Users.objects.create(
                email=google_user['email']
            )
            user.set_password(token)
            user.save()
            
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
            
        Usertoken.objects.update_or_create(
                user_id=user.id,
                defaults={
                'token':refresh_token,
                'expired_at':datetime.datetime.utcnow()+ datetime.timedelta(days=7),
                }
        )
            
        response = Response()
        response.set_cookie(key='refresh_token',value=refresh_token,httponly=True)
        response.data ={
                'token':access_token,
                'message':'user logged in sucessfully',
                'user_email':user.email
            }
        return response
    
    
class Fileuploadview(APIView):
    parser_classes = (MultiPartParser,FormParser)
    
    def post(self,request,*args,**kwargs):
        file_obj = request.FILES['file']
        
        
        upload_path = os.path.join('media','uploads')
        os.makedirs(upload_path,exist_ok=True)
        
        save_file_path =os.path.join(upload_path,file_obj.name)
        with open(save_file_path,'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)
            
        