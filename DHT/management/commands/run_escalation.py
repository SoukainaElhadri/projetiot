from django.core.management.base import BaseCommand
from django.utils import timezone
from DHT.models import Incident
from DHT.notifications import send_email_alert, send_telegram_alert, make_phone_call, notify_supervisors
from datetime import timedelta

class Command(BaseCommand):
    help = 'Checks for unacknowledged incidents and escalates them'

    def handle(self, *args, **options):
        now = timezone.now()
        unresolved_incidents = Incident.objects.filter(resolved=False, acknowledged_by__isnull=True)
        
        for incident in unresolved_incidents:
            time_since_creation = (now - incident.timestamp).total_seconds() / 60
            
            # Level 0 -> 1: Immediate Email
            if incident.escalation_level == 0:
                if send_email_alert(incident):
                    incident.escalation_level = 1
                    incident.last_notification_at = now
                    incident.save()
                    self.stdout.write(self.style.SUCCESS(f'Escalated incident {incident.id} to Level 1 (Email)'))

            # Level 1 -> 2: Telegram after 1 min (for testing)
            elif incident.escalation_level == 1 and time_since_creation >= 1:
                if send_telegram_alert(incident):
                    incident.escalation_level = 2
                    incident.last_notification_at = now
                    incident.save()
                    self.stdout.write(self.style.SUCCESS(f'Escalated incident {incident.id} to Level 2 (Telegram)'))

            # Level 2 -> 3: Call after 2 mins (1 min after Telegram)
            elif incident.escalation_level == 2 and time_since_creation >= 2:
                if make_phone_call(incident):
                    incident.escalation_level = 3
                    incident.last_notification_at = now
                    incident.save()
                    self.stdout.write(self.style.SUCCESS(f'Escalated incident {incident.id} to Level 3 (Call)'))

            # Level 3 -> 4: Notify Supervisors (after call if still no response)
            elif incident.escalation_level == 3 and time_since_creation >= 3: # Give 1 min after call
                 if notify_supervisors(incident):
                    incident.escalation_level = 4
                    incident.last_notification_at = now
                    incident.save()
                    self.stdout.write(self.style.SUCCESS(f'Escalated incident {incident.id} to Level 4 (Supervisor)'))
