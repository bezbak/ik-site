from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("cottages/", views.property_list, {"property_type": "cottage"}, name="cottages"),
    path("cottages.html", views.property_list, {"property_type": "cottage"}, name="cottages_html"),
    path("apartments/", views.property_list, {"property_type": "apartment"}, name="apartments"),
    path("apartments.html", views.property_list, {"property_type": "apartment"}, name="apartments_html"),
    path("planirovka/<slug:slug>/", views.property_detail, name="property_detail"),
]
