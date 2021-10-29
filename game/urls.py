from django.urls import path
from game.views import gyr,index,play

urlpatterns = {
    path("gyr/", gyr, name="gyr"),
    path("", index, name="index"),
    path("play/", play, name="play"),
}
