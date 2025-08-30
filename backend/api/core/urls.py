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
from django.contrib import admin
from django.urls import path
from .views import upload_spectrum, list_spectra, upload_prediction, fields_view, field_heatmap, field_points, fields_geojson
from django.http import HttpResponse

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
    path("fields/<uuid:field_id>/heatmap/", field_heatmap),
    path("fields/<uuid:field_id>/points/", field_points),
]