import os
import django
from django.test import RequestFactory
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet.settings')
django.setup()

from DHT.views import incident_list
from DHT.models import Incident, Dht11

def verify_url():
    print("Verifying Incident URL...")
    
    # Ensure there is some data
    if Incident.objects.count() == 0:
        d = Dht11.objects.create(temp=1, hum=50) # Should trigger incident
        print("Created test incident.")

    factory = RequestFactory()
    request = factory.get('/incidents/')
    response = incident_list(request)

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("PASS: URL is accessible.")
        content = response.content.decode('utf-8')
        if "Incidents List" in content:
            print("PASS: Content contains 'Incidents List'.")
        else:
            print("FAIL: Content missing expected title.")
    else:
        print("FAIL: URL returned non-200 status.")

if __name__ == "__main__":
    verify_url()
