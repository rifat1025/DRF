from . import views
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logins/', views.LoginView.as_view(), name='logins'),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path('logout/', views.LogoutView.as_view(), name= 'logout'),
    path('update/', views.UpdateProfileView.as_view(), name='update_profile'),
    path('delete/', views.DeleteAccountView.as_view(), name= 'delete_account'),
    path('verify/', views.VerifyOTPView.as_view(), name='verify_otp'),
    path('forgot-password/',views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
]