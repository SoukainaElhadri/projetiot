import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet.settings')
django.setup()

from DHT.notifications import make_phone_call
from DHT.models import Incident, Dht11

# Create a dummy incident for testing
try:
    # Use existing or create mock
    dht = Dht11.objects.last()
    if not dht:
        dht = Dht11.objects.create(temp=40, hum=50)
        
    incident = Incident(dht_reading=dht, description="Test Call Debug")
    # Don't save it to DB to avoid polluting, just pass object if possible, 
    # but some logic might rely on ID? 
    # make_phone_call uses incident.description mainly.
    
    print("Attempting to make a call...")
    success = make_phone_call(incident)
    
    if success:
        print("✅ Function returned True (Call should have been sent)")
    else:
        print("❌ Function returned False (Call failed)")

except Exception as e:
    print(f"❌ Script Error: {e}")
