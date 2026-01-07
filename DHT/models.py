from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# --- ASSETS ---

class Refrigerator(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    min_temp = models.FloatField(default=2.0)
    max_temp = models.FloatField(default=8.0)
    
    def __str__(self):
        return f"{self.name} ({self.location})"

class Sensor(models.Model):
    serial_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100, blank=True)
    refrigerator = models.ForeignKey(Refrigerator, on_delete=models.SET_NULL, null=True, blank=True, related_name='sensors')
    is_active = models.BooleanField(default=True)
    api_key = models.CharField(max_length=100, blank=True) # Simple API protection

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

# --- CORE DATA ---

class Dht11(models.Model):
    temp = models.FloatField(null=True)
    hum = models.FloatField(null=True)
    dt = models.DateTimeField(auto_now_add=True,null=True)
    # Link to Sensor (Optional for backward compatibility with old data)
    sensor = models.ForeignKey(Sensor, on_delete=models.SET_NULL, null=True, blank=True, related_name='readings')

    def __str__(self):
        return f"Reading {self.id} - {self.temp}°C"

# --- ALERTING & INCIDENTS ---

class Incident(models.Model):
    dht_reading = models.ForeignKey(Dht11, on_delete=models.CASCADE, related_name='incidents')
    description = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    
    # Notification & Escalation
    escalation_level = models.IntegerField(default=0) # 0=None, 1=Email, 2=Telegram, 3=Call, 4=Full
    last_notification_at = models.DateTimeField(null=True, blank=True)
    
    # Acknowledgment
    acknowledged_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='acknowledged_incidents')
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Incident #{self.id} - {self.timestamp}"

class IncidentComment(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.incident}"


# --- TICKETING SYSTEM ---

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('CLOSED', 'Closed'),
    ]
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    incident = models.OneToOneField(Incident, on_delete=models.CASCADE, related_name='ticket', null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tickets')

    def __str__(self):
        return f"Ticket #{self.id} - {self.title}"


# --- AUDIT & TRACEABILITY ---

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('DATA_RX', 'Data Received'),
        ('ALERT_SENT', 'Alert Sent'),
        ('TICKET_UPDATE', 'Ticket Updated'),
        ('CONFIG_CHANGE', 'Configuration Change'),
    ]
    
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # Null for system actions
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True) # JSON or text details
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.action} - {self.user}"

