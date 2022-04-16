from django.urls import path
from . import views
from .views import VerificationView

urlpatterns= [

    path('login/',views.login,name='login'),
    path('register/',views.register,name='register'),
    path('logout/',views.logout,name='logout'),
    path('activate/<uidb64>/<token>',VerificationView.as_view(),name='activate')


]