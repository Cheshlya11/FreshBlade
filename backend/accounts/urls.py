from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit_view, name="profile_edit"),
    path("masters/create/", views.master_create_view, name="master_create"),
    path(
        "masters/<int:master_id>/schedule/",
        views.master_schedule_create_view,
        name="master_schedule_create",
    ),
]
