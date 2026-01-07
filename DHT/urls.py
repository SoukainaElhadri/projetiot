from django.urls import path
from . import views
from .api import Dlist, Dhtviews
from . import api
from django.contrib.auth import views as auth_views

urlpatterns = [
    # --- DASHBOARD & CHARTS ---
    path('',views.table,name='table'),
    path('charts/', views.charts_hub, name='charts_hub'),
    path('myChartTemp/',views.graphiqueTemp,name='myChartTemp'), # Legacy Redirect
    path('myChartHum/', views.graphiqueHum, name='myChartHum'), # Legacy Redirect

    # --- TICKETS (NEW) ---
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),

    # --- AUDIT LOGS (NEW) ---
    path('audit/', views.audit_log_view, name='audit_log_view'),

    # --- REPORTS (NEW) ---
    path('reports/', views.reports_view, name='reports_view'),
    path('reports/export/csv/', views.export_report_csv, name='export_report_csv'),
    path('download_csv/', views.download_csv, name='download_csv'), # Legacy alias

    # --- INCIDENTS ---
    path('incidents/', views.incident_list, name='incident_list'),
    path('incidents/<int:incident_id>/', views.incident_detail, name='incident_detail'),

    # --- API ---
    path("api/", Dlist, name="api_list"),  # GET
    path("api/post/", Dhtviews.as_view(), name="api_post_legacy"),  # POST (Old)
    path("api/post-dht/", views.api_post_dht, name="api_post_dht"), # New secure endpoint
    path('json-data/', views.json_data_view, name='json_data'),
    path('api/sensors/all/', views.api_sensors_all, name='api_all'),
    path('api/sensors/latest/', views.api_sensors_latest, name='api_latest'),

    # --- CHART DATA ---
    path('chart-data/', views.chart_data, name='chart-data'),
    path('chart-data-jour/',views.chart_data_jour,name='chart-data-jour'),
    path('chart-data-semaine/',views.chart_data_semaine,name='chart-data-semaine'),
    path('chart-data-mois/',views.chart_data_mois,name='chart-data-mois'),

    # --- AUTHENTICATION ---
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    # path('register/', views.register, name='register'),
    path('redirect/', views.custom_login_redirect, name='custom_login_redirect'),
    path('logout/', views.user_logout, name='logout'),
]