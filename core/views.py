from djangoRest import settings
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer
import random
from django.core.mail import send_mail
from . models import Profile
from django.conf import settings
from django.utils import timezone

# 1. Define a Serializer for Registration


# 2. Updated Register View
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")

        if not username or not password or not email:
            return Response({"error": "All fields required"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "User exists"}, status=400)

        user = User.objects.create_user(username=username, password=password)

        otp = str(random.randint(100000, 999999))

        Profile.objects.create(
            user=user,
            email=email,
            otp=otp
        )

        
        send_mail(
            "Your OTP Code",
            f"Your OTP is {otp}",
            settings.EMAIL_HOST_USER,   # ✅ use your email
            [email],
            fail_silently=False,
        )
        return Response({"message": "User created. Check email for OTP"})
# 3. Updated Login View
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            })

        return Response(
            {"detail": "No active account found with the given credentials"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get (self, request):
        user = request.user 
        return Response({
            "user": request.user.username
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()  # 🔥 blacklist token

            return Response({"message": "Logged out successfully"})

        except Exception:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )

class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user

        username = request.data.get("username")
        password = request.data.get("password")

        if username:
            user.username = username

        if password:
            user.set_password(password)  # important (hashing)

        user.save()

        return Response({
            "message": "Profile updated successfully",
            "username": user.username
        })
class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        password = request.data.get("password")

        user = authenticate(username=request.user.username, password=password)

        if user is None:
            return Response({"error": "Wrong password"}, status=400)

        request.user.delete()

        return Response({"message": "Account deleted"})
    
    
class VerifyOTPView(APIView):

    def post(self, request):
        username = request.data.get("username")
        otp = request.data.get("otp")

        try:
            user = User.objects.get(username=username)
            profile = user.profile

            if profile.otp == otp:
                profile.is_verified = True
                profile.otp = None
                profile.save()

                return Response({"message": "Email verified successfully"})

            return Response({"error": "Invalid OTP"}, status=400)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        

class ForgotPasswordView(APIView):
    
    def post(self, request):
        email = request.data.get('email')
        
        try:
            profile = Profile.objects.get(email=email)
            otp = str ( random. randint(100000, 999999) )
            
            profile.otp = otp
            profile . save()
            
            send_mail(
                "Password Reset OTP",
                f"Your OTP is {otp}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return Response({"message": "OTP sent to email"})

        except Profile.DoesNotExist:
            return Response({"error": "Email not found"}, status=404)


class ResetPasswordView(APIView):
    
    def post(self, request):
        
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        
        
        try:
            profile = Profile.objects.get(email= email)
            
            if profile.otp != otp:
                return Response({"error": "Invalid OTP"}, status=400)
            
            if timezone.now() > profile.otp_created_at + timedelta(minutes=5):
                return Response({"error": "OTP expired"}, status=400)

            user = profile.user
            user.set_password(new_password)
            user.save()
            profile.otp = None
            profile.save()

            return Response({"message": "Password reset successful"})

        except Profile.DoesNotExist:
            return Response({"error": "Email not found"}, status=404)
                