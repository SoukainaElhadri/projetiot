import os
import django
from django.utils import timezone
from datetime import timedelta
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet.settings')
django.setup()

from DHT.models import Incident, Dht11
from django.core.management import call_command

def verify_escalation():
    print("Verifying Escalation Logic...")
    
    # 1. Create fresh incident
    Incident.objects.all().delete()
    Dht11.objects.all().delete()
    dht = Dht11.objects.create(temp=10, hum=50) # Bad temp
    # Incident auto-created by signal
    incident = Incident.objects.get(dht_reading=dht)
    print(f"Created Incident #{incident.id}. Level: {incident.escalation_level}")

    # 2. Run Escalation (Should go to Level 1 - Email)
    print("\n--- Run 1 (Immediate) ---")
    call_command('run_escalation')
    incident.refresh_from_db()
    print(f"Level after Run 1: {incident.escalation_level} (Expected: 1)")
    if incident.escalation_level != 1:
        print("FAIL: Did not escalate to Level 1")
    
    # 3. Time Travel: 25 mins later
    print("\n--- Time Travel: +25 mins ---")
    incident.timestamp = timezone.now() - timedelta(minutes=25)
    incident.save()
    
    call_command('run_escalation')
    incident.refresh_from_db()
    print(f"Level after Run 2: {incident.escalation_level} (Expected: 2)")
    if incident.escalation_level != 2:
        print("FAIL: Did not escalate to Level 2")

    # 4. Time Travel: 45 mins later (Total)
    print("\n--- Time Travel: +45 mins ---")
    incident.timestamp = timezone.now() - timedelta(minutes=45)
    incident.save()

    call_command('run_escalation')
    incident.refresh_from_db()
    print(f"Level after Run 3: {incident.escalation_level} (Expected: 3)")
    if incident.escalation_level != 3:
        print("FAIL: Did not escalate to Level 3")

    # 5. Time Travel: 60 mins later (Total)
    print("\n--- Time Travel: +60 mins ---")
    incident.timestamp = timezone.now() - timedelta(minutes=60)
    incident.save()

    call_command('run_escalation')
    incident.refresh_from_db()
    print(f"Level after Run 4: {incident.escalation_level} (Expected: 4)")
    if incident.escalation_level != 4:
        print("FAIL: Did not escalate to Level 4")

if __name__ == "__main__":
    verify_escalation()
