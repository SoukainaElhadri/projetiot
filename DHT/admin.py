from django.contrib import admin
from . import models
admin.site.register(models.Dht11)

admin.site.register(models.Incident)
admin.site.register(models.IncidentComment)
