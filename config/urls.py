from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("index.html", RedirectView.as_view(url="/", permanent=False)),
    path("", include("catalog.urls")),
    # Serve admin-uploaded media directly from Django. Fine for this site's traffic
    # level; move to S3/whatever if that ever changes.
    path("media/<path:path>", serve, {"document_root": settings.MEDIA_ROOT}),
]
