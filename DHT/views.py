from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import Dht11, Incident, IncidentComment, Ticket, AuditLog, Sensor
from django.utils import timezone
import csv
import datetime
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import json

# --- FRONTEND VIEWS ---

def home(request):
    if request.user.is_authenticated:
        return redirect('table')
    return render(request, 'login.html')

@login_required
def table(request):
    return render(request, 'dashboard.html')

@login_required
def charts_hub(request):
    return render(request, 'charts.html')

@login_required
def graphiqueTemp(request):
    return redirect('charts_hub')

@login_required
def graphiqueHum(request):
    return redirect('charts_hub')

# --- TICKET MANAGEMENT (NEW) ---

@login_required
def ticket_list(request):
    # Managers see all, others see their assignments or unassigned
    tickets = Ticket.objects.all().order_by('-updated_at')
    return render(request, 'ticket_list.html', {'tickets': tickets})

@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'take':
            ticket.assigned_to = request.user
            ticket.status = 'ASSIGNED'
            ticket.save()
            AuditLog.objects.create(action='TICKET_UPDATE', user=request.user, details=f"Assigned ticket #{ticket.id} to self")
            
        elif action == 'close':
            ticket.status = 'CLOSED'
            ticket.save()
            # Also resolve linked incident
            if ticket.incident:
                ticket.incident.resolved = True
                ticket.incident.save()
            AuditLog.objects.create(action='TICKET_UPDATE', user=request.user, details=f"Closed ticket #{ticket.id}")
            
        elif action == 'comment':
            # Logic for generic comments if we had a TicketComment model, 
            # for now we assume IncidentComment is used or we add it later.
            pass

        return redirect('ticket_detail', ticket_id=ticket.id)
        
    return render(request, 'ticket_detail.html', {'ticket': ticket})

# --- AUDIT LOGS (NEW) ---

@login_required
def audit_log_view(request):
    # Admin only
    if not request.user.is_superuser:
         return redirect('table')
         
    logs = AuditLog.objects.all().order_by('-timestamp')[:100]
    return render(request, 'audit_log.html', {'logs': logs})

# --- REPORTS (NEW) ---

@login_required
def reports_view(request):
    return render(request, 'reports.html')

@login_required
def export_report_csv(request):
    # Basic export logic
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Sensor', 'Temp', 'Hum'])
    
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - datetime.timedelta(days=days)
    
    qs = Dht11.objects.filter(dt__gte=start_date).select_related('sensor')
    for d in qs:
        s_name = d.sensor.name if d.sensor else "Unknown"
        writer.writerow([d.dt, s_name, d.temp, d.hum])
        
    AuditLog.objects.create(action='DATA_RX', user=request.user, details=f"Exported CSV report for last {days} days")
    return response


# --- LEGACY INCIDENTS (Keep for compatibility) ---

@login_required
def incident_list(request):
    incidents = Incident.objects.all().order_by('-timestamp')
    return render(request, 'incident_list.html', {'incidents': incidents})

@login_required
def incident_detail(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    if request.method == 'POST' and 'acknowledge' in request.POST:
        incident.acknowledged_by = request.user
        incident.acknowledged_at = timezone.now()
        incident.save()
        return redirect('incident_detail', incident_id=incident.id)
    return render(request, 'incident_detail.html', {'incident': incident})


# --- AUTHENTICATION ---

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            AuditLog.objects.create(action='LOGIN', user=user, details="New user registered and logged in")
            return redirect('table')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_logout(request):
    if request.user.is_authenticated:
        AuditLog.objects.create(action='LOGOUT', user=request.user, details="User logged out")
    logout(request)
    return redirect('home')

@login_required
def custom_login_redirect(request):
    AuditLog.objects.create(action='LOGIN', user=request.user, details="User logged in")
    return redirect('table')


# --- API / DATA ENDPOINTS (UPDATED) ---

@csrf_exempt
def api_post_dht(request):
    if request.method == "POST":
        try:
            # 1. Parse Data
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)

            temp = data.get("temp")
            hum = data.get("hum")
            serial = data.get("serial") # New field
            api_key = data.get("key")   # New field

            if temp is None or hum is None:
                return JsonResponse({"error": "Missing temp or hum"}, status=400)

            # 2. Security Check & Sensor Identification
            sensor_obj = None
            if serial:
                try:
                    sensor_obj = Sensor.objects.get(serial_number=serial)
                    if sensor_obj.api_key and sensor_obj.api_key != api_key:
                        AuditLog.objects.create(action='DATA_RX', details=f"Unauthorized access attempt for sensor {serial}")
                        return JsonResponse({"error": "Invalid API Key"}, status=403)
                except Sensor.DoesNotExist:
                    # Optional: Auto-create sensor or reject? 
                    # For strict mode: reject. For ease: keep it None.
                    pass
            
            # 3. Save Data
            reading = Dht11.objects.create(
                temp=float(temp),
                hum=float(hum),
                dt=timezone.now(),
                sensor=sensor_obj
            )
            
            # Log only occasionally to save space, or log all?
            # AuditLog.objects.create(action='DATA_RX', details=f"Data received from {serial or 'Unknown'}")

            return JsonResponse({"status": "success", "id": reading.id})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "POST only"}, status=405)


def api_sensors_latest(request):
    latest = Dht11.objects.last()
    if latest:
        data = {
            "temp": latest.temp, 
            "hum": latest.hum, 
            "dt": latest.dt.isoformat(),
            "sensor": latest.sensor.name if latest.sensor else None
        }
    else:
        data = {"error": "No data available"}
    return JsonResponse(data)

def api_sensors_all(request):
    # Optimized: Values list
    data = list(Dht11.objects.all().values('id', 'temp', 'hum', 'dt', 'sensor__name'))
    return JsonResponse(data, safe=False)

# Chart Data Helpers (Unchanged logic, just ensure imports work)
def chart_data(request):
    qs = Dht11.objects.all().order_by('dt')
    data = {
        'temps': [d.dt.isoformat() for d in qs],
        'temp': [d.temp for d in qs],
        'hum': [d.hum for d in qs],
    }
    return JsonResponse(data)

def chart_data_mois(request):
    start = timezone.now() - datetime.timedelta(days=30)
    qs = Dht11.objects.filter(dt__gte=start).order_by('dt')
    return _chart_response(qs)

def chart_data_semaine(request):
    start = timezone.now() - datetime.timedelta(days=7)
    qs = Dht11.objects.filter(dt__gte=start).order_by('dt')
    return _chart_response(qs)

def chart_data_jour(request):
    start = timezone.now() - datetime.timedelta(hours=24)
    qs = Dht11.objects.filter(dt__gte=start).order_by('dt')
    return _chart_response(qs)

def _chart_response(qs):
    data = {
        'temps': [d.dt.isoformat() for d in qs],
        'temp': [d.temp for d in qs],
        'hum': [d.hum for d in qs],
    }
    return JsonResponse(data)

def download_csv(request):
    return export_report_csv(request)

def json_data_view(request):
    # Only returning simplified JSON for now
    return api_sensors_latest(request)


##