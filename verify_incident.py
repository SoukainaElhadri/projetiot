import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet.settings')
django.setup()

from DHT.models import Dht11, Incident

def run_verification():
    print("Starting verification...")
    
    # Clean up previous test data if needed (optional)
    # Dht11.objects.all().delete()
    # Incident.objects.all().delete()

    # Test Case 1: Normal temperature (should NOT create incident)
    print("Testing Normal Temperature (5°C)...")
    Incident.objects.all().delete() # Start clean
    d1 = Dht11.objects.create(temp=5, hum=50)
    incidents_count = Incident.objects.filter(dht_reading=d1).count()
    if incidents_count == 0:
        print("PASS: No incident created for 5°C.")
    else:
        print(f"FAIL: Incident created for 5°C! Count: {incidents_count}")

    # Test Case 2: Low temperature (should create incident)
    print("Testing Low Temperature (1°C)...")
    Incident.objects.all().delete() # Start clean
    d2 = Dht11.objects.create(temp=1, hum=50)
    incidents_count = Incident.objects.filter(dht_reading=d2).count()
    if incidents_count == 1:
        print("PASS: Incident created for 1°C.")
        print(f"Incident: {Incident.objects.get(dht_reading=d2)}")
    else:
        print(f"FAIL: Incident NOT created for 1°C! Count: {incidents_count}")

    # Test Case 3: High temperature (should create incident)
    print("Testing High Temperature (9°C)...")
    Incident.objects.all().delete() # Start clean
    d3 = Dht11.objects.create(temp=9, hum=50)
    incidents_count = Incident.objects.filter(dht_reading=d3).count()
    if incidents_count == 1:
        print("PASS: Incident created for 9°C.")
        print(f"Incident: {Incident.objects.get(dht_reading=d3)}")
    else:
        print(f"FAIL: Incident NOT created for 9°C! Count: {incidents_count}")

    # Test Case 4: Auto-resolve
    print("Testing Auto-Resolve (5°C)...")
    # Setup: Create an incident first
    Incident.objects.all().delete()
    Dht11.objects.create(temp=1, hum=50)
    
    d4 = Dht11.objects.create(temp=5, hum=50) # Should resolve existing incidents
    incidents_count = Incident.objects.filter(resolved=True).count()
    if incidents_count > 0:
         print(f"PASS: {incidents_count} incidents resolved.")
    else:
         print("FAIL: Incidents NOT resolved.")

    # Test Case 5: Duplicate prevention
    print("Testing Duplicate Prevention...")
    # Clean state
    Dht11.objects.all().delete()
    Incident.objects.all().delete()
    
    # 1. Create first incident
    d_bad1 = Dht11.objects.create(temp=1, hum=50) # Incident created
    count_after_first = Incident.objects.count()
    print(f"Count after first bad reading: {count_after_first}")

    # 2. Create second incident (same bad condition)
    d_bad2 = Dht11.objects.create(temp=0, hum=50) # Should NOT create new incident
    count_after_second = Incident.objects.count()
    print(f"Count after second bad reading: {count_after_second}")

    if count_after_first == 1 and count_after_second == 1:
        print("PASS: No duplicate incident created.")
    else:
        print(f"FAIL: Duplicates created! {count_after_first} -> {count_after_second}")

if __name__ == "__main__":
    run_verification()
