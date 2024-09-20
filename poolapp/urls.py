from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name=""),
    path('register', views.register, name="register"),
    path('userlogin', views.userlogin, name="userlogin"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('userlogout', views.userlogout, name="userlogout"),
    path('updategames', views.updategames, name="updategames"),
    path('updaterecords', views.updateRecords, name="updaterecords"),
    path('standings', views.standings, name="standings"),

]