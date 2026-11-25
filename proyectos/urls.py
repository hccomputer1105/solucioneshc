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
    path("card/<slug:slug>/", views.ver_tarjeta_publica, name="ver_tarjeta_publica"),
    path("admin-tarjeta/<int:user_id>/", views.admin_gestionar_tarjeta, name="admin_gestionar_tarjeta"),
    path("mi-tarjeta/", views.cliente_editar_tarjeta, name="cliente_editar_tarjeta"),
    path("validar-pago/<int:pago_id>/<str:accion>/", views.admin_validar_pago, name="admin_validar_pago"),
    path("reportar-pago/", views.cliente_reportar_pago, name="cliente_reportar_pago"),
    path("api/publicidad/", views.api_publicidad, name="api_publicidad"),
    path("admin-publicidad/<int:user_id>/", views.admin_gestionar_publicidad, name="admin_gestionar_publicidad"),
    path("validar-pago-pub/<int:pago_id>/<str:accion>/", views.admin_validar_pago_pub, name="admin_validar_pago_pub"),
    path("mi-publicidad/", views.cliente_editar_publicidad, name="cliente_editar_publicidad"),
    path("reportar-pago-pub/", views.cliente_reportar_pago_pub, name="cliente_reportar_pago_pub"),
    path("eliminar-app-demo/<int:pk>/", views.eliminar_app_demo, name="eliminar_app_demo"),
    path("api/apps/", views.api_apps_publicas, name="api_apps_publicas"),
]