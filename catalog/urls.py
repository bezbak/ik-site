from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("properties/", views.properties, name="properties"),
    path("properties.html", views.properties, name="properties_html"),
    path("cottages/", views.cottages, name="cottages"),
    path("cottages.html", views.cottages, name="cottages_html"),
    path("apartments/", views.apartments, name="apartments"),
    path("apartments.html", views.apartments, name="apartments_html"),
    path("planirovka/<slug:slug>/", views.property_detail, name="property_detail"),
    path("contact-us.html", views.contact_us, name="contact_us"),
    path("about-us.html", views.about_us, name="about_us"),
    path("api/leads/", views.lead_create, name="lead_create"),
]
