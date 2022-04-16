from django.urls import path
from . import views

#http://127.0.0.1:8000/movies
#http://127.0.0.1:8000/2



urlpatterns= [

    path('',views.index,name='movies'),
    path('<int:movie_id>',views.detail,name='detail'),
    path('search', views.search, name='search')

]