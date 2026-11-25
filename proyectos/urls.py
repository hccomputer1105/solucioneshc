from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("editar/<int:pk>/", views.editar_proyecto, name="editar_proyecto"),
    path("eliminar/<int:pk>/", views.eliminar_proyecto, name="eliminar_proyecto"),
    path("tarjeta/", views.tarjeta_view, name="tarjeta"),
    path("api/proyectos/", views.api_proyectos, name="api_proyectos"),
]