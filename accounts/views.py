from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from .serializers import (
    UserSerializer,
    OTPSerializer,
    SignInSerializer,
    GoogleSignInSerializer,
    VerifyEmailUpdateOTpSerializer,
)
from utils.utils import generate_otp , send_otp_email
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from .permissions import IsAdminAndAuthenticated,IsCourseAdmin
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView

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
                register_mode='email'

                user = CustomUser.objects.create_user(email=email, password=password, register_mode=register_mode, role='user')

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
            if not serializer.is_valid():
                error_message = serializer.errors.get('email', ['An error occurred'])[0]
                return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)  
            
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Find the user by email
            user = CustomUser.objects.filter(email=email).first()

            if not user:
                return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)
        
            if not user.is_active:
                return Response({"error": "You are blocked by admin. Please contact the admin."}, status=status.HTTP_403_FORBIDDEN)
        
            if not check_password(password, user.password):
                return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

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



class CustomreAbstractCrateView(APIView):

    permission_classes = []

    def post(self , request):

        
        serializer = UserSerializer(data=request.data) 

        try:
            if serializer.is_valid():
                email = serializer.validated_data.pop('email')
                password = serializer.validated_data.pop('password')

                extra_feilds = serializer.validated_data
                register_mode = 'email'

                user = CustomUser.objects.create_user(
                    email=email,
                    password=password,
                    register_mode=register_mode,
                    **extra_feilds
                )
                

                user_serializer = UserSerializer(user)

                return Response({
                    "message": "User created successfully.",
                    "user": user_serializer.data
                }, status=status.HTTP_201_CREATED)
                
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print('error:', e)
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class SubAdminCreateView(CustomreAbstractCrateView):
    """
    This View handle the Creation of Subadmin 
    """

    permission_classes = [IsAdminAndAuthenticated]
class InstructorCreateView(CustomreAbstractCrateView):
    """
    This View handle the Creation of Instructor 
    """
    permission_classes = [IsCourseAdmin]




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

class UserProfileRetrieveUpdateView(RetrieveUpdateAPIView):
    
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Override to return the current user.
        """
        return self.request.user
    

    
class UserProfileVerifyUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        print(request.data)
        otp_serializer = VerifyEmailUpdateOTpSerializer(data=request.data)

        if not otp_serializer.is_valid():
            return Response(otp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = otp_serializer.validated_data
        user = request.user

        # Prepare update data conditionally
        update_data = {
            'email': validated_data.get('email', user.email),
            'first_name': validated_data.get('first_name', user.first_name),
            'last_name': validated_data.get('last_name', user.last_name),
        }

        # Remove any None values from update_data
        update_data = {k: v for k, v in update_data.items() if v is not None}

        if update_data:
            user_serializer = UserSerializer(user, data=update_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
                return Response({
                    "message": "Profile updated successfully",
                    "user": user_serializer.data
                }, status=status.HTTP_200_OK)
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "No valid data to update."}, status=status.HTTP_400_BAD_REQUEST)

                