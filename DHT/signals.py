from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Dht11, Incident, Ticket, AuditLog
from .notifications import send_email_alert, send_telegram_alert, make_phone_call

# --- INCIDENT & ALERT LOGIC ---

@receiver(post_save, sender=Dht11)
def check_temperature_incident(sender, instance, created, **kwargs):
    if created and instance.temp is not None:
        # Determine limits: Use Refrigerator limits if linked, else Default 2-8
        min_temp = 2.0
        max_temp = 8.0
        
        if instance.sensor and instance.sensor.refrigerator:
             min_temp = instance.sensor.refrigerator.min_temp
             max_temp = instance.sensor.refrigerator.max_temp
             
        if instance.temp < min_temp or instance.temp > max_temp:
            # Check if there is already an active UNRESOLVED incident for this sensor
            # If sensor is None, we might check generic. Ideally restrict to sensor.
            
            existing_incident = Incident.objects.filter(resolved=False)
            if instance.sensor:
                existing_incident = existing_incident.filter(dht_reading__sensor=instance.sensor)
            
            if not existing_incident.exists():
                incident = Incident.objects.create(
                    dht_reading=instance,
                    description=f"Température {instance.temp}°C en dehors de la plage autorisée({min_temp}-{max_temp})"
                )
                
                # --- AUTOMATION: Create Ticket ---
                Ticket.objects.create(
                    title=f"Alert: {incident.description}",
                    description=f"Automated ticket for Incident #{incident.id}.\nSensor: {instance.sensor}\nTemp: {instance.temp}",
                    incident=incident,
                    priority='HIGH',
                    status='OPEN'
                )

                # --- NOTIFICATIONS (Simplified for immediacy) ---
                send_email_alert(incident)
                send_telegram_alert(incident)
                # make_phone_call(incident) # Optional
                
                incident.escalation_level = 1 
                incident.last_notification_at = timezone.now()
                incident.save()
                
                # --- AUDIT LOG ---
                AuditLog.objects.create(
                    action='ALERT_SENT',
                    details=f"Incident #{incident.id} triggered. Ticket created."
                )

        else:
            # AUTO-RESOLVE if back to normal
            filter_args = {'resolved': False}
            if instance.sensor:
                 filter_args['dht_reading__sensor'] = instance.sensor
            
            open_incidents = Incident.objects.filter(**filter_args)
            if open_incidents.exists():
                count = open_incidents.update(resolved=True)
                AuditLog.objects.create(
                    action='SYSTEM',
                    details=f"Auto-resolved {count} incidents as temp returned to normal."
                )

# --- AUDIT LOGGING ---

@receiver(post_save, sender=Ticket)
def log_ticket_change(sender, instance, created, **kwargs):
    action = 'TICKET_CREATED' if created else 'TICKET_UPDATE'
    AuditLog.objects.create(
        action=action,
        user=instance.assigned_to, # Might be None if automated
        details=f"Ticket #{instance.id} ({instance.title}) is now {instance.status}."
    )
