from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import render

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.api_views import ProtectedTestView


def home(request):
    return render(request, "home.html")


urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("recruiter/", include("recruiter.urls")),
    path("candidate/", include("candidate.urls")),
    path("account/", include("accounts.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/protected/", ProtectedTestView.as_view(), name="protected-api"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.BASE_DIR / "static",
    )
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
