
from django.core.mail import send_mail
from django.conf import settings
import rest_framework
from .models import Dht11
from .serializers import DHT11serialize

from rest_framework.decorators import api_view
from rest_framework import generics, status
from rest_framework.response import Response


# ============================
# GET → Lister toutes les données
# ============================
@api_view(['GET'])
def Dlist(request):
    """
    Retourne toutes les données du capteur DHT11 (GET)
    URL : /api/
    """
    all_data = Dht11.objects.all().order_by('-dt')
    serializer = DHT11serialize(all_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ============================
# POST → Réception ESP8266
# ============================
class Dhtviews(generics.CreateAPIView):
    """
    Réception des données envoyées par ESP8266 (POST)
    URL : /api/post/
    """
    queryset = Dht11.objects.all()
    serializer_class = DHT11serialize
