from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name=""),
    path('register', views.register, name="register"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('userlogout', views.userlogout, name="userlogout"),
    path('updategames', views.updategames, name="updategames"),
    path('updaterecords', views.updateRecords, name="updaterecords"),
    path('standings', views.standings, name="standings"),
    path("accounts/", include("django.contrib.auth.urls")),
    path('picks', views.picks, name="picks"),

]