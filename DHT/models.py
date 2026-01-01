from django.db import models

# Create your models here.

from django.db import models
class Dht11(models.Model):
    temp = models.FloatField(null=True)
    hum = models.FloatField(null=True)
    dt = models.DateTimeField(auto_now_add=True,null=True)

class Incident(models.Model):
    dht_reading = models.ForeignKey(Dht11, on_delete=models.CASCADE, related_name='incidents')
    description = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    
    # Notification & Escalation
    escalation_level = models.IntegerField(default=0) # 0=None, 1=Email, 2=Telegram, 3=Call, 4=Full
    last_notification_at = models.DateTimeField(null=True, blank=True)
    
    # Acknowledgment
    acknowledged_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='acknowledged_incidents')
    acknowledged_at = models.DateTimeField(null=True, blank=True)

class IncidentComment(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.incident}"

    def __str__(self):
        return f"Incident at {self.timestamp}: {self.description}"

from django.db.models.signals import post_save
from django.dispatch import receiver
from DHT.notifications import send_email_alert, send_telegram_alert, make_phone_call
from django.utils import timezone

@receiver(post_save, sender=Dht11)
def check_temperature_incident(sender, instance, created, **kwargs):
    if created and instance.temp is not None:
        if instance.temp < 2 or instance.temp > 8:
            # Check if there is already an active incident
            if not Incident.objects.filter(resolved=False).exists():
                incident = Incident.objects.create(
                    dht_reading=instance,
                    description=f"Temperature out of range: {instance.temp} (Allowed: 2-8)"
                )
                
                # Send ALL alerts immediately (No waiting for worker)
                send_email_alert(incident)
                send_telegram_alert(incident)
                try:
                    make_phone_call(incident)
                except Exception as e:
                    print(f"Call failed: {e}")
                
                incident.escalation_level = 3 # Mark as fully notified
                incident.last_notification_at = timezone.now()
                incident.save()
        else:
            # Auto-resolve existing incidents
            Incident.objects.filter(resolved=False).update(resolved=True)

