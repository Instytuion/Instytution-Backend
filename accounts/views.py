from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from .serializers import (
    UserSerializer,
    OTPSerializer,
    SignInSerializer,
    GoogleSignInSerializer,
)
from utils.utils import generate_otp , send_otp_email
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from .permissions import IsAdminAndAuthenticated
from rest_framework.generics import GenericAPIView


class UserSignUpView(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        try:
            if serializer.is_valid():
                email = serializer.validated_data['email']
                otp = generate_otp()

                # Store OTP in Redis cache with a 2-minute timeout
                cache.set(f"otp_{email}", otp, timeout=120)
                print('generated_otp:',otp)


                username = email.split('@')[0]
                try:
                    send_otp_email(email, username, otp)
                    return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
                except Exception as e:
                    cache.delete(f"otp_{email}")
                    return Response(
                        {"error": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print('error:',e)
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class UserOTPVerifyView(APIView):

    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        try:
            if serializer.is_valid():

                email = serializer.validated_data['email']
                password = serializer.validated_data['password']

                user = CustomUser.objects.create_user(email=email, password=password, role='user')

                if user:
                    cache.delete(f"otp_{email}")
                
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                # Serialize user data
                user_serializer = UserSerializer(user)

                return Response({
                    "message": "User created successfully.",
                    "user": user_serializer.data,
                    "refresh": str(refresh),
                    "access": access_token
                }, status=status.HTTP_201_CREATED)
                
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print('error:', e)
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
                



class SignInUserView(APIView):

    def post(self, request):
        serializer = SignInSerializer(data=request.data)
        
        try:
            if serializer.is_valid():
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']

                # Find the user by email
                user = CustomUser.objects.filter(email=email).first()

                if user and not user.is_active:
                    return Response({
                        "error": "You are blocked by admin. Please contact the admin."
                    }, status=status.HTTP_403_FORBIDDEN)
                
                if user and check_password(password, user.password):
                    # Generate tokens
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)

                    # Serialize user data
                    user_serializer = UserSerializer(user)

                    return Response({
                        "message": "Login successful.",
                        "user": user_serializer.data,
                        "refresh": str(refresh),
                        "access": access_token
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)
        
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print('error:', e)
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ResentOTPView(APIView):
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        try:
            if serializer.is_valid():
                email = serializer.validated_data['email']
                cached_otp = cache.get(f"otp_{email}")

                if cached_otp:
                    remaining_time = cache.ttl(f"otp_{email}")
                    return Response({
                        "message": "OTP already sent.",
                        "remaining_time": remaining_time,
                        "detail": "Please wait before requesting a new OTP."
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
                
                resent_otp = generate_otp()
                email = serializer.validated_data['email']
                cache.set(f"otp_{email}", resent_otp, timeout=120)
                print('generated_otp:',resent_otp)



                username = email.split('@')[0]
                try:
                    send_otp_email(email, username, resent_otp)
                    return Response({"message": "OTP resent successfully."}, status=status.HTTP_200_OK)
                except Exception as e:
                    cache.delete(f"otp_{email}")
                    return Response(
                        {"error": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print('error:',e)
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SubAdminCreateView(APIView):
    def post(self , request):

        permission_classes = [IsAdminAndAuthenticated]
        serializer = UserSerializer(data=request.data) 

        try:
            if serializer.is_valid():
                email = serializer.validated_data.pop('email')
                password = serializer.validated_data.pop('password')

                extra_feilds = serializer.validated_data

                user = CustomUser.objects.create_user(email=email, password=password, **extra_feilds)
                
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                user_serializer = UserSerializer(user)

                return Response({
                    "message": "User created successfully.",
                    "user": user_serializer.data,
                    "refresh": str(refresh),
                    "access": access_token
                }, status=status.HTTP_201_CREATED)
                
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print('error:', e)
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


class GoogleOauthSignInview(GenericAPIView):
    """
    Google OAuth sign-in view.
    """
    serializer_class=GoogleSignInSerializer

    def post(self, request):
        """
        Handle Google OAuth sign-in.
        Returns Response object containing the access token.
        """
        print(request.data)
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=((serializer.validated_data)['access_token'])
        return Response(data, status=status.HTTP_200_OK) 


