from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets,status
from rest_framework.views import APIView
import os


from django.utils.crypto import get_random_string
from django.utils import timezone

from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication


from rest_framework.permissions import IsAuthenticated, AllowAny,IsAdminUser

from django.contrib.auth.models import User
from ..serializers import  ProfileCompletionSerializer, ProfileSerializer
import random
import requests
from django.http import JsonResponse
from django.views import View
from rest_framework.decorators import action
from django.core.cache import cache

from ..models import Profile, TemporaryMobileVerification
from twilio.rest import Client 




class MobileLoginView(viewsets.ViewSet):
    
    permission_classes = [AllowAny]

    # disabling DRF’s default authentication to allow mobile based token to be used
    authentication_classes = []
    
    @action(detail=False, methods=['post'], url_path='request-otp')
    def request_otp(self, request):
        mobile_number = request.data.get('mobile_number')

        if not self.can_request_otp(mobile_number):
            return Response({'error': 'Too many requests, Try again later'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        otp_code = get_random_string(length=6, allowed_chars='0123456789')

        verification, created = TemporaryMobileVerification.objects.update_or_create(
            mobile_number=mobile_number,
            defaults={
                'otp_code': otp_code,
                'is_verified': False,
                'otp_sent_at': timezone.now() # NECESSARY
            }
        )

        print(f'sending otp {otp_code} to mobile {mobile_number}')
        # message_body = f"Your verification code is: {otp_code}"

        try:
            response = self.send_whatsapp_message(mobile_number, otp_code)
            # response = send_otp_via_fast2sms(mobile_number, otp_code)
            print("status",response.status_code)
            if response.status_code == 200:  #get('return', False):
                return Response({'message': 'OTP sent successfully via Fast2SMS '}, status=status.HTTP_200_OK)
            else:
                print('failed to send')
                return Response({'error': 'Failed to send OTP via Fast2SMS'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        
        except Exception as e:
            print('error to send')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def send_otp_via_twilio(self, phone_number, otp_code):
        try:
            # Twilio credentials from environment variables
            print('sending')
            account_sid =""
            auth_token = ""
            twilio_phone_number = ""

            client = Client(account_sid, auth_token)

            message = client.messages.create(
                body=f"Your OTP code is {otp_code}",
                from_=twilio_phone_number,
                to=phone_number
            )
            print(message)
            return {"status": "success", "sid": message.sid}
        except Exception as e:
            print("Error", e)
            return {"status": "error", "message": str(e)}
        
    def send_whatsapp_message(self, phone_number, otp_code):
        # Failed due to Facebook aprroval delay
        url = "https://graph.facebook.com/v20.0/392655450602043/messages"
        WHATSAPP_SECRET_KEY = os.getenv('WHATSAPP_SECRET_KEY')
        headers = {
            # 60 days permanent for Husni
            "Authorization": f"Bearer {WHATSAPP_SECRET_KEY}",

            "Content-Type": "application/json"
        }
        data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        # "text": {
        #     "body": "Test message",
        # }
        "template": {
            "name": "mishwari_login",  # Replace with your actual template name
            "language": {"code": "ar"},  # Replace with the appropriate language code
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": otp_code  # The OTP code variable
                        }
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [
                    {
                        "type": "text",
                        "text": otp_code
                    }
                    ]
                }
            ]
        }
    }
        response = requests.post(url, json=data, headers=headers)
        print(response.json())
        return response
    

    @action(detail=False, methods=['patch'], url_path='verify-otp')
    def verify_otp(self, request):
        mobile_number = request.data.get('mobile_number')
        otp_code = request.data.get('otp_code')
        
        try:
            verification = TemporaryMobileVerification.objects.get(mobile_number=mobile_number)
            print('Verification', verification.otp_is_valid())
        except TemporaryMobileVerification.DoesNotExist:
            return Response({'error': 'Mobile number not found'}, status=status.HTTP_404_NOT_FOUND)
        

        if verification.otp_code == otp_code and verification.otp_is_valid(): # otp validity 10 min from models
            print('received otp ',otp_code)
            verification.is_verified = True
            verification.save()

            try:
                user = User.objects.get(profile__mobile_number=mobile_number)
                tokens = self.get_tokens_for_user(user)
                return Response({
                    "message": "Login successful.",
                    "user_status": "complete",
                    "tokens": tokens
                }, status=status.HTTP_200_OK)
            
            except User.DoesNotExist:
                tokens = self.get_temporary_token_for_mobile(mobile_number)
                return Response({
                    "message": "Mobile number verified, proceed to complete registration.",
                    "user_status": "partial",
                    "tokens": tokens
                }, status=status.HTTP_200_OK)
            
        return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
    

    @action(detail = False, methods = ['GET'], url_path='profile')
    def profile_detail(self,request):
        user = User.objects.get(user=request.user)
    
    @action(detail=False, methods=['post'], url_path='complete-profile')
    def complete_profile(self, request):
        # token_mobile_number = request.user.token.get('mobile_number') # did not work since token has to be linked with user id 

        # self.authentication_classes = []

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "No token provided"}, status=status.HTTP_401_UNAUTHORIZED)
        
        token_str = auth_header.split(' ')[1]

        try: 
            token = UntypedToken(token_str)
            token_mobile_number = token.get('mobile_number', None) # case 1: if mobile based token
            user_id = token.get('user_id', None) # case 2: if user based token

            # if not token_mobile_number:
            #     return Response({"error": "Invalid token. No mobile number found"}, status=status.HTTP_401_UNAUTHORIZED)

            # if only mobile verified without
            if token_mobile_number:


                if 'mobile_number' in request.data:
                    return Response({"error" : "Mobile number can not be changed during profile completing after verification."}, status=status.HTTP_400_BAD_REQUEST)
                
                serializer = ProfileCompletionSerializer(data=request.data, context={'mobile_number': token_mobile_number}) # NOTE trigger create since no instance provided 
                if serializer.is_valid():
                    profile = serializer.save()
                    user = profile.user
                    tokens = self.get_tokens_for_user(user)
                    # print('serializer', serializer.data)
                    return Response({
                        "message": "Profile created successfully.",
                        "tokens": tokens}, status=status.HTTP_201_CREATED
                        )
                
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # if exist user and profile
            elif user_id:
                print('user_based update')
                try:
                    user = User.objects.get(id=user_id) # raise user exception if user is not available
                    profile = user.profile # raise profile exception if profile is not available
                    serializer = ProfileCompletionSerializer(profile, data=request.data, partial=True) # NOTE trigger update method since "profile" instance provided
                    if serializer.is_valid():
                        serializer.save()
                        return Response({"message": "Profile updated successfully."}, status=status.HTTP_200_OK)
                    
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                except User.DoesNotExist:
                    return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
                
                except Profile.DoesNotExist:
                    return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
                
            else:
                return Response({"error": "Invalid token. No valid identification found"}, status=status.HTTP_401_UNAUTHORIZED)
                
        except  (InvalidToken, TokenError) as e:

            return Response({"error": f"Invalid or expired token: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)
        


    

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        

    
    def get_temporary_token_for_mobile(self, mobile_number):
        refresh = RefreshToken()
        refresh['mobile_number'] = mobile_number # number becomes part of the token's data
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
    
    def can_request_otp(self, mobile_number):
        request_count = cache.get(f'otp_request_count_{mobile_number}', 0)
        if request_count >= 3:
            return False
        
        cache.set(f'otp_request_count_{mobile_number}', request_count + 1, timeout = 30) # Waiting time
        return True
    

class ProfileView(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # This line gets the user ID from the JWT token and returns the corresponding user
        return Profile.objects.filter(user=self.request.user.id)
    
    def get_permissions(self):
        if self.request.method in ['GET']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    

class whatsapp_webhook(APIView):
    def post(self, request):
        data = request.data
        
        # Check if the webhook is related to message delivery
        if 'statuses' in data:
            for status_data in data['statuses']:
                message_status = status_data.get('status')
                recipient_phone = status_data.get('recipient_id')

                # Log message status
                print(f"Message to {recipient_phone} has status: {message_status}")

                # You can implement further logic here, such as marking OTP as delivered, etc.

        return Response({"message": "Webhook received"}, status=status.HTTP_200_OK)

    def get(self, request):
        """
        This GET method is usually called by Facebook/WhatsApp when validating the webhook.
        """
        hub_mode = request.GET.get('hub.mode')
        hub_challenge = request.GET.get('hub.challenge')
        hub_verify_token = request.GET.get('hub.verify_token')

        if hub_mode == 'subscribe' and hub_verify_token == 'YOUR_VERIFY_TOKEN':
            return Response(hub_challenge, status=status.HTTP_200_OK)

        return Response({"error": "Invalid verification token"}, status=status.HTTP_400_BAD_REQUEST)