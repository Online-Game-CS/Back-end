from django.conf.urls import url
from . import api

urlpatterns = [
    url('init', api.initialize),
    url('move', api.move),
    url('say', api.say),
    url('welcome', api.welcome),
    url('getrooms', api.get_rooms),
    url('start', api.start),
    url('completechallenge', api.complete_challenge)
]