from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Proyecto

# 1. PÁGINA PRINCIPAL (LANDING PAGE)
def home_view(request):
    return render(request, "index.html")

# 2. TARJETA DIGITAL
def tarjeta_view(request):
    return render(request, "tarjeta.html")

# 3. API PÚBLICA QUE CONSUME WORDPRESS
def api_proyectos(request):
    proyectos = Proyecto.objects.filter(visible_en_web=True)
    data = [
        {
            "id": p.id,
            "titulo": p.titulo,
            "cliente": p.cliente,
            "descripcion": p.descripcion,
            "estado": p.estado,
            "progreso": p.progreso,
            "tecnologias": p.tecnologias,
        }
        for p in proyectos
    ]
    response = JsonResponse(data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    return response

# 4. VISTA DE LOGIN
def login_view(request):
    error = None
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user:
            login(request, user)
            return redirect("dashboard")
        error = "Usuario o contraseña incorrectos"
    return render(request, "login.html", {"error": error})

# 5. PANEL PRIVADO PARA CREAR PROYECTOS
@login_required(login_url="/login/")
def dashboard_view(request):
    if request.method == "POST":
        Proyecto.objects.create(
            titulo=request.POST.get("titulo"),
            cliente=request.POST.get("cliente"),
            descripcion=request.POST.get("descripcion"),
            estado=request.POST.get("estado"),
            progreso=int(request.POST.get("progreso", 0)),
            tecnologias=request.POST.get("tecnologias"),
            visible_en_web=bool(request.POST.get("visible_en_web"))
        )
        return redirect("dashboard")

    proyectos = Proyecto.objects.all()
    return render(request, "dashboard.html", {"proyectos": proyectos})

# 6. EDITAR PROYECTO
@login_required(login_url="/login/")
def editar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == "POST":
        proyecto.titulo = request.POST.get("titulo")
        proyecto.cliente = request.POST.get("cliente")
        proyecto.descripcion = request.POST.get("descripcion")
        proyecto.estado = request.POST.get("estado")
        proyecto.progreso = int(request.POST.get("progreso", 0))
        proyecto.tecnologias = request.POST.get("tecnologias")
        proyecto.visible_en_web = bool(request.POST.get("visible_en_web"))
        proyecto.save()
    return redirect("dashboard")

# 7. ELIMINAR PROYECTO
@login_required(login_url="/login/")
def eliminar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    proyecto.delete()
    return redirect("dashboard")

# 8. CERRAR SESIÓN
def logout_view(request):
    logout(request)
    return redirect("login")