from  django.shortcuts import render
from django.http import HttpResponse
def test(request):
    return HttpResponse("Hello world")





# Create your views here.
def latest_json():
    return None


from django.shortcuts import render, get_object_or_404, redirect
from .models import Dht11, Incident, IncidentComment  # Assurez-vous d'importer le modèle Dht11
from django.utils import timezone
import csv
from django.http import HttpResponse
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth import logout

from django.http import HttpResponse, JsonResponse

import json


# Page d'accueil
def home(request):
    return render(request, 'home.html')


# Dernière valeur dans value.html
def table(request):
    derniere_ligne = Dht11.objects.last()
    if not derniere_ligne:
        return HttpResponse("Aucune donnée disponible.")

    delta_temps = timezone.now() - derniere_ligne.dt
    minutes = delta_temps.seconds // 60
    temps_ecoule = f"il y a {minutes} min"
    if minutes > 60:
        temps_ecoule = f"il y a {minutes // 60}h{minutes % 60}min"

    valeurs = {
        'date': temps_ecoule,
        'id': derniere_ligne.id,
        'temp': derniere_ligne.temp,
        'hum': derniere_ligne.hum
    }
    return render(request, 'value.html', {'valeurs': valeurs})


def incident_list(request):
    incidents = Incident.objects.all().order_by('-timestamp')
    critical_threshold = timezone.now() - datetime.timedelta(hours=10)
    return render(request, 'incident_list.html', {
        'incidents': incidents,
        'critical_threshold': critical_threshold
    })


@login_required
def incident_detail(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    
    if request.method == 'POST':
        if 'acknowledge' in request.POST:
            incident.acknowledged_by = request.user
            incident.acknowledged_at = timezone.now()
            # incident.resolved = True  <-- Removed: Only safe temp resolves it
            incident.save()
            return redirect('incident_detail', incident_id=incident.id)
        
        elif 'comment' in request.POST:
            text = request.POST.get('text')
            if text:
                IncidentComment.objects.create(incident=incident, user=request.user, text=text)
            return redirect('incident_detail', incident_id=incident.id)

    return render(request, 'incident_detail.html', {'incident': incident})


# Téléchargement CSV
def download_csv(request):
    data = Dht11.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dht.csv"'

    writer = csv.writer(response)
    writer.writerow(['id', 'temp', 'hum', 'dt'])
    for row in data:
        writer.writerow([row.id, row.temp, row.hum, row.dt])
        
    return response

# Mini Dashboard Views (Restored for Navbar compatibility)
def dashboard(request):
    return render(request, 'dashboard.html')


# Pages graphiques
def graphiqueTemp(request):
    return render(request, 'ChartTemp.html')


def graphiqueHum(request):
    return render(request, 'ChartHum.html')

def charts_hub(request):
    return render(request, 'charts_hub.html')


# Données JSON - toutes
def chart_data(request):
    qs = Dht11.objects.all()
    data = {
        'temps': [d.dt.isoformat() for d in qs],
        'temp': [d.temp for d in qs],
        'hum': [d.hum for d in qs],
    }
    return JsonResponse(data)


def chart_data_jour(request):
    now = timezone.now()
    start = now - datetime.timedelta(hours=24)
    qs = Dht11.objects.filter(dt__range=(start, now))
    data = {
        'temps': [d.dt.isoformat() for d in qs],
        'temp': [d.temp for d in qs],
        'hum': [d.hum for d in qs],
    }
    return JsonResponse(data)


def chart_data_semaine(request):
    start = timezone.now() - datetime.timedelta(days=7)
    qs = Dht11.objects.filter(dt__gte=start)
    data = {
        'temps': [d.dt.isoformat() for d in qs],
        'temp': [d.temp for d in qs],
        'hum': [d.hum for d in qs],
    }
    return JsonResponse(data)


def chart_data_mois(request):
    start = timezone.now() - datetime.timedelta(days=30)
    qs = Dht11.objects.filter(dt__gte=start)
    data = {
        'temps': [d.dt.isoformat() for d in qs],
        'temp': [d.temp for d in qs],
        'hum': [d.hum for d in qs],
    }
    return JsonResponse(data)


def chart_data_date_temp(request):
    date_str = request.GET.get('date')
    try:
        # Convertir la chaîne en objet date
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return JsonResponse({'temps': [], 'temp': [], 'hum': []})

    # Créer un datetime pour le début (minuit) et la fin (minuit suivant) de la date sélectionnée
    start_datetime = datetime.datetime.combine(date_obj, datetime.time.min)
    start_datetime = timezone.make_aware(start_datetime)
    end_datetime = start_datetime + datetime.timedelta(days=1)

    # Filtrer les données entre start_datetime et end_datetime
    queryset = Dht11.objects.filter(dt__gte=start_datetime, dt__lt=end_datetime).order_by('dt')

    # Préparer les données avec les temps en format ISO
    data = {
        'temps': [obj.dt.isoformat() for obj in queryset],
        'temp': [obj.temp for obj in queryset],
        'hum': [obj.hum for obj in queryset],
    }
    return JsonResponse(data)


def chart_data_date_hum(request):
    date_str = request.GET.get('date')
    try:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return JsonResponse({'temps': [], 'temp': [], 'hum': []})

    start_datetime = datetime.datetime.combine(date_obj, datetime.time.min)
    start_datetime = timezone.make_aware(start_datetime)
    end_datetime = start_datetime + datetime.timedelta(days=1)

    queryset = Dht11.objects.filter(dt__gte=start_datetime, dt__lt=end_datetime).order_by('dt')

    data = {
        'temps': [obj.dt.isoformat() for obj in queryset],
        'temp': [obj.temp for obj in queryset],
        'hum': [obj.hum for obj in queryset],
    }
    return JsonResponse(data)


# Inscription utilisateur
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


# Déconnexion
def user_logout(request):
    logout(request)
    return redirect('home')

# Redirect after login based on Role
@login_required
def custom_login_redirect(request):
    user = request.user
    if user.is_superuser or user.groups.filter(name='Admin').exists():
        return redirect('/admin/')
    elif user.groups.filter(name='Manager').exists():
        return redirect('incident_list')
    else:
        return redirect('incident_list')


# ////////////////////////// Json
def json_data_view(request):
    # Get latest sensor data
    sensor_data = Dht11.objects.order_by('-dt')[:50]

    # Format as JSON
    data = {
        "status": "success",
        "dt": timezone.now().isoformat(),
        "count": sensor_data.count(),
        "sensors": [
            {
                "id": s.id,
                "temp": s.temp,
                "hum": s.hum,
                "dt": s.dt.isoformat()
            }
            for s in sensor_data
        ]
    }

    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(data)

    # For HTML view
    return render(request, 'json_data.html', {
        'sensor_data': json.dumps(data, indent=2, ensure_ascii=False)
    })


# API endpoints
def api_sensors_all(request):
    data = Dht11.objects.all().values()
    return JsonResponse(list(data), safe=False)


def api_sensors_latest(request):
    latest = Dht11.objects.last()
    if latest:
        data = {
            "temp": latest.temp,
            "hum": latest.hum,
            "dt": latest.dt.isoformat()
        }
    else:
        data = {"error": "No data available"}
    return JsonResponse(data)


# @csrf_exempt
#def api_post_dht(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            temp = data.get("temp")
            hum = data.get("hum")

            # Sauvegarde en base de données
            Dht11.objects.create(
                temp=temp,
                hum=hum,
                dt=timezone.now()
            )

            print("✅ DATA REÇUE :", data)

            return JsonResponse({
                "status": "success",
                "temp": temp,
                "hum": hum
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "POST only"}, status=405)
##