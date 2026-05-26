from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", RedirectView.as_view(pattern_name="dashboard:home", permanent=False)),
    path("", include("apps.core.urls")),
    path("", include("apps.dashboard.urls")),
    path("", include("apps.assets.urls")),
    path("", include("apps.ai.urls")),
    path("api/v1/", include("apps.assets.api_urls")),
]
