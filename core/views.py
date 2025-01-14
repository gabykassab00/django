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
from ML.main import main
from dotenv import load_dotenv
import openai
from rest_framework.exceptions import APIException
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Team

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
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        global PASSES_DATA  
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"error": "No file uploaded."})

        media_folder = os.path.join("media")
        os.makedirs(media_folder, exist_ok=True)
        save_file_path = os.path.join(media_folder, file_obj.name)

        try:
            with open(save_file_path, "wb+") as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)

            print(f"File saved at: {save_file_path}")

            PASSES_DATA = main(save_file_path)

            return Response({
                "message": f"File '{file_obj.name}' uploaded and processed successfully."
            }, status=200)

        except Exception as e:
            print(f"Error: {e}")
            return Response({"error": str(e)})


class GetStatsView(APIView):
    def get(self, request):
        global PASSES_DATA
        try:
            if PASSES_DATA is None:
                return Response({"error": "No stats available. Please run the upload API first."})

            PASSES_DATA["passers_totals"]["team1"] = {
                str(k): v for k, v in PASSES_DATA["passers_totals"]["team1"].items()
            }
            PASSES_DATA["passers_totals"]["team2"] = {
                str(k): v for k, v in PASSES_DATA["passers_totals"]["team2"].items()
            }

            PASSES_DATA["team_stats"]["team1"] = {
                str(k): {
                    "average_speed": float(v.get("average_speed", 0.0)),
                    "total_distance": float(v.get("total_distance", 0.0)),
                }
                for k, v in PASSES_DATA["team_stats"]["team1"].items()
            }
            PASSES_DATA["team_stats"]["team2"] = {
                str(k): {
                    "average_speed": float(v.get("average_speed", 0.0)),
                    "total_distance": float(v.get("total_distance", 0.0)),
                }
                for k, v in PASSES_DATA["team_stats"]["team2"].items()
            }

            ball_control_stats = PASSES_DATA.get("team_ball_control", {})
            PASSES_DATA["team_ball_control"] = {
                "team1": float(ball_control_stats.get("team1", 0.0)),
                "team2": float(ball_control_stats.get("team2", 0.0)),
            }

            team_summary = PASSES_DATA.get("team_summary", {})



            PASSES_DATA["team_summary"]["team1"]["average_speed"] = float(
                team_summary.get("team1", {}).get("average_team_speed", 0.0)
            )
            PASSES_DATA["team_summary"]["team1"]["total_distance"] = float(
                team_summary.get("team1", {}).get("total_team_distance", 0.0)
            )
            PASSES_DATA["team_summary"]["team2"]["average_speed"] = float(
                team_summary.get("team2", {}).get("average_team_speed", 0.0)
            )
            PASSES_DATA["team_summary"]["team2"]["total_distance"] = float(
                team_summary.get("team2", {}).get("total_team_distance", 0.0)
            )



            return Response(PASSES_DATA)

        except Exception as e:
            return Response({"error": str(e)})


logger = logging.getLogger(__name__)

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

@method_decorator(csrf_exempt,name='dispatch')

class AIVIEW(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            logger.info(f"Received data: {data}")

            stats = data.get("stats")
            action = data.get("action", "analyze")  

            if not stats or not isinstance(stats, list):
                logger.error("Stats data must be a list.")
                return JsonResponse({"error": "Stats data must be a list"})

            logger.info(f"Parsed stats: {stats}")
            logger.info(f"Requested action: {action}")

            if action == "analyze":
                user_message = f"I want your full analysis, like a pundit, with details on these stats: {stats}"
            elif action == "training":
                user_message = (
                    f"Using these stats: {stats}, create a short and concise training program with key drills and exercises to improve speed, endurance, ball control, and passing accuracy."
                )
            
            else:
                logger.error("Invalid action provided.")
                return JsonResponse({"error": "Invalid action"})

            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message},
                ],
            )
            logger.info(f"OpenAI Response: {response}")

            answer = response.choices[0].message.content

            return JsonResponse({"answer": answer})

        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from the request body.")
            return JsonResponse({"error": "Invalid JSON data"})

        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            return JsonResponse({"error": str(e)})


class Addteamdataview(LoginRequiredMixin,View):
    def post(self,request, *args, **kwargs):
        try:
            data = request.POST
            user = request.user
            
            
            Team.objects.create(
                user=user,
                date=data.get('date'),
                game=data.get('game'),
                ball_control=float(data.get('ball_control')),
                distance_covered=float(data.get('distance_covered')),
                average_speed=float(data.get('average_speed')),
                total_passes=int(data.get('total_passes')),
            )
            
            return JsonResponse({"message":"team data added succesfully"})
        except Exception as e :
            return JsonResponse({"error":str(e)})