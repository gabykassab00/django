from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions
class Registerapiview(APIView):
    def post(self,request):
        data = request.data 
        
        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('passwords do not match')
        
        
        
        return Response(request.data)
    
