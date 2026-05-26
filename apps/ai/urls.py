from django.urls import path

from . import views

app_name = "ai"

urlpatterns = [
    path("ai/api/stream/", views.chat_stream_view, name="chat_stream"),
    path("ai/api/sessions/", views.chat_sessions_view, name="chat_sessions"),
    path("ai/api/sessions/create/", views.chat_session_create_view, name="chat_session_create"),
    path("ai/api/sessions/<int:pk>/", views.chat_session_detail_view, name="chat_session_detail"),
    path("ai/api/sessions/<int:pk>/delete/", views.chat_session_delete_view, name="chat_session_delete"),
]
