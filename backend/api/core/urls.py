"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin
from django.http import HttpResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    field_runs,
    upload_run,
    fields_view,
    field_points,
    list_spectra,
    field_heatmap,
    fields_geojson,
    upload_spectrum,
    upload_prediction,
    StartPiScriptView,
    PiCommandRetrieveView,
    PiCommandAcknowledgeView
)

def home(request):
    return HttpResponse("Hello from Django on AWS Lambda!")

urlpatterns = [
    path('', home, name='home'),  # Add this to serve a basic response at "/"
    path('admin/', admin.site.urls),
    path('upload-prediction/', upload_prediction),
    path("spectra/", list_spectra, name="list-spectra"),
    path("upload-spectrum/", upload_spectrum, name="upload-spectrum"),
    path("fields/", fields_view),
    path("fields/geojson/", fields_geojson),
    path("fields/<uuid:field_id>/runs/", field_runs),
    path("fields/<uuid:field_id>/heatmap/", field_heatmap),
    path("fields/<uuid:field_id>/points/", field_points),
    path("upload-run/", upload_run, name="upload-run"),
    path("start-pi-script/", StartPiScriptView.as_view(), name="start-pi-script"),
    path("pi-commands/<str:device_id>/", PiCommandRetrieveView.as_view(), name="pi-command-get"),
    path("pi-commands/<str:device_id>/ack/", PiCommandAcknowledgeView.as_view(), name="pi-command-ack"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]