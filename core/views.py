from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions
from .serializers import Userserializer
from .models import Users
from .authentication import create_access_token,create_refresh_token,decode_access_token,Jwtauthentication
from rest_framework.authentication import get_authorization_header
class Registerapiview(APIView):
    def post(self,request):
        data = request.data 
        
        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('passwords do not match')
        
        serializer = Userserializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    

class Loginapiview(APIView):
    def post(self,request):
        email  =request.data['email']
        password = request.data['password']
        
        
        user = Users.objects.filter(email=email).first()
        
        if user is None:
            raise exceptions.AuthenticationFailed('invalid credentials')
        
        
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('invalid credentials')
        
        
        
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        
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
        
        return Response(refresh_token)