from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.text import slugify
from .models import (
    Proyecto,
    TarjetaDigital,
    ReportePagoTarjeta,
    PublicidadBanner,
    ReportePagoPublicidad,
    AppDemoRender,
    EvaluacionFactibilidad,
)


# 1. PÁGINA PRINCIPAL Y TARJETA DE DEMOSTRACIÓN
def home_view(request):
    return render(request, "index.html")


def tarjeta_view(request):
    return render(request, "tarjeta.html")


# 2. APIS PÚBLICAS PARA LA WEB / WORDPRESS
def api_proyectos(request):
    proyectos = Proyecto.objects.filter(visible_en_web=True)
    data = [
        {
            "id": p.id,
            "titulo": p.titulo,
            "cliente": p.cliente,
            "descripcion": p.descripcion,
            "problema_detectado": p.problema_detectado,
            "resultado_obtenido": p.resultado_obtenido,
            "estado": p.estado,
            "progreso": p.progreso,
            "tecnologias": p.tecnologias,
        }
        for p in proyectos
    ]
    response = JsonResponse(data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    return response


def api_publicidad(request):
    anuncios = [b for b in PublicidadBanner.objects.all() if b.esta_activa]
    data = [
        {
            "id": b.id,
            "ubicacion": b.ubicacion,
            "titulo": b.titulo,
            "texto": b.texto,
            "texto_boton": b.texto_boton,
            "enlace_destino": b.enlace_destino,
            "imagen_url": request.build_absolute_uri(b.imagen.url) if b.imagen else "",
            "usar_html": b.usar_html_personalizado,
            "html": b.codigo_html_personalizado if b.usar_html_personalizado else "",
        }
        for b in anuncios
    ]
    response = JsonResponse(data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    return response


def api_apps_publicas(request):
    apps = AppDemoRender.objects.filter(visible_en_web=True)
    data = [
        {
            "nombre": a.nombre,
            "categoria": a.categoria,
            "descripcion": a.descripcion,
        }
        for a in apps
    ]
    response = JsonResponse(data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    return response


# 3. AUTENTICACIÓN (LOGIN / LOGOUT)
def login_view(request):
    error = None
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user:
            login(request, user)
            return redirect("dashboard")
        error = "Usuario o contraseña incorrectos"
    return render(request, "login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("login")


# 4. DASHBOARD PRINCIPAL (ADMIN VS CLIENTE)
@login_required(login_url="/login/")
def dashboard_view(request):
    # Portal del Cliente
    if not request.user.is_staff:
        mis_proyectos = Proyecto.objects.filter(cliente_usuario=request.user)
        tarjeta = TarjetaDigital.objects.filter(usuario=request.user).first()
        publicidad = PublicidadBanner.objects.filter(usuario=request.user).first()
        return render(request, "cliente_portal.html", {
            "proyectos": mis_proyectos,
            "tarjeta": tarjeta,
            "publicidad": publicidad,
        })

    # Panel del Administrador
    mensaje = None
    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "crear_cliente":
            nuevo_user = request.POST.get("nuevo_username", "").strip()
            nueva_pass = request.POST.get("nuevo_password", "").strip()
            email_cliente = request.POST.get("nuevo_email", "").strip()
            if nuevo_user and nueva_pass:
                if not User.objects.filter(username=nuevo_user).exists():
                    User.objects.create_user(
                        username=nuevo_user,
                        password=nueva_pass,
                        email=email_cliente,
                        is_staff=False,
                    )
                    mensaje = f"Acceso creado para el cliente '{nuevo_user}'."
                else:
                    mensaje = f"El usuario '{nuevo_user}' ya existe."

        elif accion == "crear_app_demo":
         AppDemoRender.objects.create(
             nombre=request.POST.get("app_nombre", "").strip(),
             url=request.POST.get("app_url", "").strip(),
             descripcion=request.POST.get("app_descripcion", "").strip(),
             credenciales_demo=request.POST.get("app_credenciales", "").strip(),
             categoria=request.POST.get("app_categoria", "SaaS / Render").strip(),
             visible_en_web=bool(request.POST.get("app_visible_en_web")),
         )
         return redirect("dashboard")

        elif accion == "crear_proyecto" or not accion:
            cliente_id = request.POST.get("cliente_usuario")
            usuario_asignado = User.objects.filter(id=cliente_id).first() if cliente_id else None

            Proyecto.objects.create(
                titulo=request.POST.get("titulo", "").strip(),
                cliente=request.POST.get("cliente", "").strip(),
                cliente_usuario=usuario_asignado,
                descripcion=request.POST.get("descripcion", "").strip(),
                problema_detectado=request.POST.get("problema_detectado", "").strip(),
                resultado_obtenido=request.POST.get("resultado_obtenido", "").strip(),
                estado=request.POST.get("estado", "En progreso"),
                progreso=int(request.POST.get("progreso") or 0),
                tecnologias=request.POST.get("tecnologias", "").strip(),
                visible_en_web=bool(request.POST.get("visible_en_web")),
            )
            return redirect("dashboard")

    proyectos = Proyecto.objects.all()
    clientes = User.objects.filter(is_staff=False)
    pagos_pendientes = ReportePagoTarjeta.objects.filter(estado="pendiente")
    pagos_pub_pendientes = ReportePagoPublicidad.objects.filter(estado="pendiente")

    if not AppDemoRender.objects.exists():
        AppDemoRender.objects.create(
            nombre="AuditTech · Plataforma de Auditoría",
            url="https://audittech.onrender.com/cuentas/login/",
            descripcion="Sistema web desplegado en Render para gestión y control de auditorías.",
            categoria="Auditoría / SaaS",
            orden=1,
        )

    apps_demo = AppDemoRender.objects.all()

    return render(request, "dashboard.html", {
        "proyectos": proyectos,
        "clientes": clientes,
        "pagos_pendientes": pagos_pendientes,
        "pagos_pub_pendientes": pagos_pub_pendientes,
        "apps_demo": apps_demo,
        "mensaje": mensaje,
    })


# 5. CRUD DE PROYECTOS Y APPS DEMO (SOLO ADMIN)
@login_required(login_url="/login/")
def editar_proyecto(request, pk):
    if not request.user.is_staff:
        return redirect("dashboard")
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == "POST":
        cliente_id = request.POST.get("cliente_usuario")
        proyecto.cliente_usuario = User.objects.filter(id=cliente_id).first() if cliente_id else None
        proyecto.titulo = request.POST.get("titulo", "").strip()
        proyecto.cliente = request.POST.get("cliente", "").strip()
        proyecto.descripcion = request.POST.get("descripcion", "").strip()
        proyecto.problema_detectado = request.POST.get("problema_detectado", "").strip()
        proyecto.resultado_obtenido = request.POST.get("resultado_obtenido", "").strip()
        proyecto.estado = request.POST.get("estado", "En progreso")
        proyecto.progreso = int(request.POST.get("progreso") or 0)
        proyecto.tecnologias = request.POST.get("tecnologias", "").strip()
        proyecto.visible_en_web = bool(request.POST.get("visible_en_web"))
        proyecto.save()
    return redirect("dashboard")


@login_required(login_url="/login/")
def eliminar_proyecto(request, pk):
    if not request.user.is_staff:
        return redirect("dashboard")
    proyecto = get_object_or_404(Proyecto, pk=pk)
    proyecto.delete()
    return redirect("dashboard")


@login_required(login_url="/login/")
def eliminar_app_demo(request, pk):
    if not request.user.is_staff:
        return redirect("dashboard")
    app_demo = get_object_or_404(AppDemoRender, pk=pk)
    app_demo.delete()
    return redirect("dashboard")


# 6. TARJETAS DIGITALES: VISTA PÚBLICA
def ver_tarjeta_publica(request, slug):
    tarjeta = get_object_or_404(TarjetaDigital, slug=slug)

    if not tarjeta.esta_activa:
        return render(request, "tarjeta_suspendida.html", {"t": tarjeta})

    if tarjeta.usar_html_personalizado and tarjeta.codigo_html_personalizado.strip():
        return HttpResponse(tarjeta.codigo_html_personalizado)

    return render(request, "tarjeta_publica.html", {"t": tarjeta})


# 7. TARJETAS DIGITALES: ADMIN Y CLIENTE
@login_required(login_url="/login/")
def admin_gestionar_tarjeta(request, user_id):
    if not request.user.is_staff:
        return redirect("dashboard")

    cliente = get_object_or_404(User, id=user_id, is_staff=False)
    tarjeta, _ = TarjetaDigital.objects.get_or_create(
        usuario=cliente,
        defaults={
            "slug": slugify(cliente.username),
            "nombre_completo": cliente.username,
            "cargo": "Consultor / Especialista",
            "telefono": "+58",
            "whatsapp": "58",
            "correo": cliente.email or "contacto@empresa.com",
            "fecha_vencimiento": timezone.localdate() + timedelta(days=30),
        },
    )

    if request.method == "POST":
        tarjeta.habilitada = bool(request.POST.get("habilitada"))
        tarjeta.plan = request.POST.get("plan", "mensual")
        tarjeta.empresa = request.POST.get("empresa", "")
        tarjeta.avatar_dialogo = request.POST.get("avatar_dialogo", "").strip()

        fecha_str = request.POST.get("fecha_vencimiento")
        if fecha_str:
            tarjeta.fecha_vencimiento = datetime.strptime(fecha_str, "%Y-%m-%d").date()

        tarjeta.slug = slugify(request.POST.get("slug") or cliente.username)
        tarjeta.plantilla = request.POST.get("plantilla", "cyber_dark")
        tarjeta.nombre_completo = request.POST.get("nombre_completo", "")
        tarjeta.cargo = request.POST.get("cargo", "")
        tarjeta.empresa = request.POST.get("empresa", "")
        tarjeta.lema_especialidades = request.POST.get("lema_especialidades", "")
        tarjeta.telefono = request.POST.get("telefono", "")
        tarjeta.whatsapp = request.POST.get("whatsapp", "")
        tarjeta.correo = request.POST.get("correo", "")
        tarjeta.sitio_web = request.POST.get("sitio_web", "")
        tarjeta.link_agenda = request.POST.get("link_agenda", "")
        tarjeta.linkedin = request.POST.get("linkedin", "")
        tarjeta.instagram = request.POST.get("instagram", "")
        tarjeta.youtube = request.POST.get("youtube", "")
        tarjeta.facebook = request.POST.get("facebook", "")
        tarjeta.usar_html_personalizado = bool(request.POST.get("usar_html_personalizado"))
        tarjeta.codigo_html_personalizado = request.POST.get("codigo_html_personalizado", "")

        if request.FILES.get("logo_empresa"):
            tarjeta.logo_empresa = request.FILES["logo_empresa"]
        if request.FILES.get("foto"):
            tarjeta.foto = request.FILES["foto"]
        if request.FILES.get("avatar_imagen"):
            tarjeta.avatar_imagen = request.FILES["avatar_imagen"]
        if request.FILES.get("video_avatar"):
            tarjeta.video_avatar = request.FILES["video_avatar"]

        tarjeta.save()
        return redirect("dashboard")

    return render(request, "admin_tarjeta_form.html", {"cliente": cliente, "t": tarjeta})


@login_required(login_url="/login/")
def admin_validar_pago(request, pago_id, accion):
    if not request.user.is_staff:
        return redirect("dashboard")

    pago = get_object_or_404(ReportePagoTarjeta, id=pago_id)
    if accion == "aprobar" and pago.estado == "pendiente":
        pago.estado = "aprobado"
        pago.save()
        pago.tarjeta.renovar_plan(pago.plan_solicitado)
    elif accion == "rechazar" and pago.estado == "pendiente":
        pago.estado = "rechazado"
        pago.save()

    return redirect("dashboard")


@login_required(login_url="/login/")
def cliente_reportar_pago(request):
    tarjeta = get_object_or_404(TarjetaDigital, usuario=request.user)
    if request.method == "POST":
        ReportePagoTarjeta.objects.create(
            tarjeta=tarjeta,
            plan_solicitado=request.POST.get("plan_solicitado", "mensual"),
            metodo_pago=request.POST.get("metodo_pago", ""),
            referencia=request.POST.get("referencia", ""),
            monto=request.POST.get("monto", ""),
            comprobante=request.FILES.get("comprobante"),
        )
    return redirect("dashboard")


@login_required(login_url="/login/")
def cliente_editar_tarjeta(request):
    tarjeta = get_object_or_404(TarjetaDigital, usuario=request.user)
    if not tarjeta.esta_activa or tarjeta.usar_html_personalizado:
        return redirect("dashboard")

    guardado = False
    if request.method == "POST":
        tarjeta.empresa = request.POST.get("empresa", tarjeta.empresa)
        tarjeta.avatar_dialogo = request.POST.get("avatar_dialogo", tarjeta.avatar_dialogo).strip()
        tarjeta.plantilla = request.POST.get("plantilla", tarjeta.plantilla)
        tarjeta.nombre_completo = request.POST.get("nombre_completo", tarjeta.nombre_completo)
        tarjeta.cargo = request.POST.get("cargo", tarjeta.cargo)
        tarjeta.empresa = request.POST.get("empresa", tarjeta.empresa)
        tarjeta.lema_especialidades = request.POST.get("lema_especialidades", tarjeta.lema_especialidades)
        tarjeta.telefono = request.POST.get("telefono", tarjeta.telefono)
        tarjeta.whatsapp = request.POST.get("whatsapp", tarjeta.whatsapp)
        tarjeta.correo = request.POST.get("correo", tarjeta.correo)
        tarjeta.sitio_web = request.POST.get("sitio_web", tarjeta.sitio_web)
        tarjeta.link_agenda = request.POST.get("link_agenda", tarjeta.link_agenda)
        tarjeta.linkedin = request.POST.get("linkedin", tarjeta.linkedin)
        tarjeta.instagram = request.POST.get("instagram", tarjeta.instagram)
        tarjeta.youtube = request.POST.get("youtube", tarjeta.youtube)
        tarjeta.facebook = request.POST.get("facebook", tarjeta.facebook)

        if request.FILES.get("logo_empresa"):
            tarjeta.logo_empresa = request.FILES["logo_empresa"]
        if request.FILES.get("foto"):
            tarjeta.foto = request.FILES["foto"]
        if request.FILES.get("avatar_imagen"):
            tarjeta.avatar_imagen = request.FILES["avatar_imagen"]
        if request.FILES.get("video_avatar"):
            tarjeta.video_avatar = request.FILES["video_avatar"]

        tarjeta.save()
        guardado = True

    return render(request, "cliente_editar_tarjeta.html", {"t": tarjeta, "guardado": guardado})


# 8. PUBLICIDAD B2B: ADMIN Y CLIENTE
@login_required(login_url="/login/")
def admin_gestionar_publicidad(request, user_id):
    if not request.user.is_staff:
        return redirect("dashboard")

    cliente = get_object_or_404(User, id=user_id, is_staff=False)
    banner, _ = PublicidadBanner.objects.get_or_create(
        usuario=cliente,
        defaults={
            "titulo": f"Servicios de {cliente.username}",
            "fecha_vencimiento": timezone.localdate() + timedelta(days=30),
        },
    )

    if request.method == "POST":
        banner.habilitada = bool(request.POST.get("habilitada"))
        banner.ubicacion = request.POST.get("ubicacion", "estandar")
        banner.plan = request.POST.get("plan", "mensual")

        fecha_str = request.POST.get("fecha_vencimiento")
        if fecha_str:
            banner.fecha_vencimiento = datetime.strptime(fecha_str, "%Y-%m-%d").date()

        banner.titulo = request.POST.get("titulo", "")
        banner.texto = request.POST.get("texto", "")
        banner.texto_boton = request.POST.get("texto_boton", "Conocer más →")
        banner.enlace_destino = request.POST.get("enlace_destino", "")
        banner.usar_html_personalizado = bool(request.POST.get("usar_html_personalizado"))
        banner.codigo_html_personalizado = request.POST.get("codigo_html_personalizado", "")

        if request.FILES.get("imagen"):
            banner.imagen = request.FILES["imagen"]

        banner.save()
        return redirect("dashboard")

    return render(request, "admin_publicidad_form.html", {"cliente": cliente, "b": banner})


@login_required(login_url="/login/")
def admin_validar_pago_pub(request, pago_id, accion):
    if not request.user.is_staff:
        return redirect("dashboard")

    pago = get_object_or_404(ReportePagoPublicidad, id=pago_id)
    if accion == "aprobar" and pago.estado == "pendiente":
        pago.estado = "aprobado"
        pago.save()
        pago.publicidad.renovar_plan(pago.plan_solicitado)
    elif accion == "rechazar" and pago.estado == "pendiente":
        pago.estado = "rechazado"
        pago.save()

    return redirect("dashboard")


@login_required(login_url="/login/")
def cliente_editar_publicidad(request):
    banner = get_object_or_404(PublicidadBanner, usuario=request.user)
    if not banner.esta_activa or banner.usar_html_personalizado:
        return redirect("dashboard")

    guardado = False
    if request.method == "POST":
        banner.titulo = request.POST.get("titulo", banner.titulo)
        banner.texto = request.POST.get("texto", banner.texto)
        banner.texto_boton = request.POST.get("texto_boton", banner.texto_boton)
        banner.enlace_destino = request.POST.get("enlace_destino", banner.enlace_destino)
        if request.FILES.get("imagen"):
            banner.imagen = request.FILES["imagen"]
        banner.save()
        guardado = True

    return render(request, "cliente_editar_publicidad.html", {"b": banner, "guardado": guardado})


@login_required(login_url="/login/")
def cliente_reportar_pago_pub(request):
    banner = get_object_or_404(PublicidadBanner, usuario=request.user)
    if request.method == "POST":
        ReportePagoPublicidad.objects.create(
            publicidad=banner,
            plan_solicitado=request.POST.get("plan_solicitado", "mensual"),
            metodo_pago=request.POST.get("metodo_pago", ""),
            referencia=request.POST.get("referencia", ""),
            monto=request.POST.get("monto", ""),
            comprobante=request.FILES.get("comprobante"),
        )
    return redirect("dashboard")

@login_required(login_url="/login/")
def toggle_app_demo_web(request, pk):
    if not request.user.is_staff:
        return redirect("dashboard")
    app_demo = get_object_or_404(AppDemoRender, pk=pk)
    app_demo.visible_en_web = not app_demo.visible_en_web
    app_demo.save()
    return redirect("dashboard")

@login_required(login_url="/login/")
def evaluacion_proyectos_view(request, eval_id=None):
    if not request.user.is_staff:
        return redirect("dashboard")

    clientes = User.objects.filter(is_staff=False)
    evaluaciones = EvaluacionFactibilidad.objects.select_related("cliente").all()
    evaluacion_activa = (
        get_object_or_404(EvaluacionFactibilidad, id=eval_id)
        if eval_id
        else evaluaciones.first()
    )

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "guardar_evaluacion":
            cliente_obj = get_object_or_404(User, id=request.POST.get("cliente_id"))
            ev = EvaluacionFactibilidad.objects.create(
                cliente=cliente_obj,
                nombre_proyecto_propuesto=request.POST.get("nombre_proyecto_propuesto", "").strip(),
                notas_consultor=request.POST.get("notas_consultor", "").strip(),
                # Tecnología
                tec_red_estructurada=bool(request.POST.get("tec_red_estructurada")),
                tec_dominio_correos=bool(request.POST.get("tec_dominio_correos")),
                tec_seguridad_perimetral=bool(request.POST.get("tec_seguridad_perimetral")),
                tec_seguridad_logica=bool(request.POST.get("tec_seguridad_logica")),
                tec_servidores=bool(request.POST.get("tec_servidores")),
                tec_camaras_cctv=bool(request.POST.get("tec_camaras_cctv")),
                # Marketing
                mkt_sitio_web=bool(request.POST.get("mkt_sitio_web")),
                mkt_redes_identidad=bool(request.POST.get("mkt_redes_identidad")),
                mkt_crm_automatizacion=bool(request.POST.get("mkt_crm_automatizacion")),
                mkt_analitica_metricas=bool(request.POST.get("mkt_analitica_metricas")),
                # Organizacional
                org_roles_organigrama=bool(request.POST.get("org_roles_organigrama")),
                org_manuales_procesos=bool(request.POST.get("org_manuales_procesos")),
                org_continuidad_riesgos=bool(request.POST.get("org_continuidad_riesgos")),
                org_kpis_gestion=bool(request.POST.get("org_kpis_gestion")),
            )
            return redirect("evaluacion_proyecto_detalle", eval_id=ev.id)

        elif accion == "convertir_a_proyecto" and evaluacion_activa:
            diag = evaluacion_activa.diagnostico_ia
            todas_brechas = diag["fase1"] + diag["fase2"] + diag["fase3"]
            Proyecto.objects.create(
                titulo=evaluacion_activa.nombre_proyecto_propuesto,
                cliente=evaluacion_activa.cliente.username,
                cliente_usuario=evaluacion_activa.cliente,
                problema_detectado=diag["resumen"],
                resultado_obtenido=f"Proyección de madurez: de {evaluacion_activa.madurez_global}% a {diag['proyeccion_objetivo']}%. Fases: {len(todas_brechas)} mejoras clave.",
                descripcion=" | ".join(todas_brechas[:5]) or "Optimización integral de infraestructura y procesos.",
                estado="En progreso",
                progreso=15,
                tecnologias="Infraestructura, Ciberseguridad, Procesos, Marketing Digital",
                visible_en_web=False,
            )
            return redirect("dashboard")

    return render(request, "evaluacion_factibilidad.html", {
        "clientes": clientes,
        "evaluaciones": evaluaciones,
        "ev": evaluacion_activa,
    })