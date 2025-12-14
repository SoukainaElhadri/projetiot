from django.urls import path
from . import views
from .api import Dlist, Dhtviews
from . import api
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path("api",api.Dlist,name='json'),
    # path("api/post",api.Dlist,name='json')
    path("api/", Dlist, name="api_list"),  # GET
    path("api/post/", Dhtviews.as_view(), name="api_post"),  # POST
    # path("api/post/", views.api_post_dht, name="api_post_dht"),

    path('download_csv/', views.download_csv, name='download_csv'),
    path('index/',views.table,name='table'),
    path('myChartTemp/',views.graphiqueTemp,name='myChartTemp'),
    path('myChartHum/', views.graphiqueHum, name='myChartHum'),
    path('chart-data/', views.chart_data, name='chart-data'),

    path('chart-data-jour/',views.chart_data_jour,name='chart-data-jour'),
    path('chart-data-semaine/',views.chart_data_semaine,name='chart-data-semaine'),
    path('chart-data-mois/',views.chart_data_mois,name='chart-data-mois'),
    path('chart-data-date-temp/', views.chart_data_date_temp, name='chart-data-date-temp'),
    path('chart-data-date-hum/', views.chart_data_date_hum, name='chart-data-date-hum'),
    path('', views.home, name='home'),

    path('json-data/', views.json_data_view, name='json_data'),
    path('api/sensors/all/', views.api_sensors_all, name='api_all'),
    path('api/sensors/latest/', views.api_sensors_latest, name='api_latest'),


]