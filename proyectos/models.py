import uuid
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Proyecto(models.Model):
    ESTADOS = [
        ('En progreso', 'En progreso'),
        ('En auditoría', 'En auditoría'),
        ('Completado', 'Completado'),
    ]
    titulo = models.CharField(max_length=200)
    cliente = models.CharField(max_length=150, help_text="Ej. Sector Salud / Empresa Privada")
    cliente_usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proyectos_asignados",
        help_text="Opcional: Usuario del cliente para que vea su avance en el portal"
    )
    descripcion = models.TextField()
    problema_detectado = models.TextField(blank=True, default="", help_text="Brecha o riesgo inicial encontrado")
    resultado_obtenido = models.TextField(blank=True, default="", help_text="Impacto o mejora lograda")
    estado = models.CharField(max_length=30, choices=ESTADOS, default='En progreso')
    progreso = models.PositiveIntegerField(default=50, help_text="Porcentaje de 0 a 100")
    tecnologias = models.CharField(max_length=200, help_text="Separadas por coma: Django, Firewall, WordPress")
    visible_en_web = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return f"{self.titulo} ({self.progreso}%)"


def generar_codigo_tarjeta():
    return f"TD-{uuid.uuid4().hex[:6].upper()}"


class TarjetaDigital(models.Model):
    PLANTILLAS = [
        ('cyber_dark', '1. Cyber-Executive (Oscuro & Cian)'),
        ('corp_light', '2. Corporativo Ejecutivo (Blanco & Azul Marino)'),
        ('emerald_pro', '3. Consultor Estratégico (Oscuro & Esmeralda)'),
        ('graphite_gold', '4. Directivo Premium (Grafito & Dorado)'),
    ]

    PLANES = [
        ('mensual', 'Plan Mensual (30 días)'),
        ('anual', 'Plan Anual (365 días)'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="tarjeta_digital")
    codigo_suscripcion = models.CharField(max_length=15, unique=True, default=generar_codigo_tarjeta)
    habilitada = models.BooleanField(default=False, help_text="Permiso otorgado por el administrador")
    plan = models.CharField(max_length=20, choices=PLANES, default='mensual')
    fecha_vencimiento = models.DateField(default=timezone.now)

    slug = models.SlugField(max_length=100, unique=True, help_text="URL pública: /card/este-nombre/")
    plantilla = models.CharField(max_length=30, choices=PLANTILLAS, default='cyber_dark')

    # Datos de la tarjeta
    foto = models.FileField(upload_to='tarjetas/', blank=True, null=True)
    nombre_completo = models.CharField(max_length=150)
    cargo = models.CharField(max_length=150)
    empresa = models.CharField(max_length=150, blank=True, default="")
    lema_especialidades = models.CharField(max_length=250, blank=True, default="")
    telefono = models.CharField(max_length=30)
    whatsapp = models.CharField(max_length=30)
    correo = models.EmailField()
    sitio_web = models.URLField(blank=True, default="")
    link_agenda = models.URLField(blank=True, default="")
    linkedin = models.URLField(blank=True, default="")
    instagram = models.URLField(blank=True, default="")
    youtube = models.URLField(blank=True, default="")
    facebook = models.URLField(blank=True, default="")

    # Modo VIP Administrador
    usar_html_personalizado = models.BooleanField(default=False)
    codigo_html_personalizado = models.TextField(blank=True, default="")
    actualizada = models.DateTimeField(auto_now=True)

    @property
    def dias_restantes(self):
        hoy = timezone.localdate()
        return (self.fecha_vencimiento - hoy).days

    @property
    def esta_activa(self):
        return self.habilitada and self.dias_restantes >= 0

    def renovar_plan(self, tipo_plan=None):
        plan_a_aplicar = tipo_plan or self.plan
        dias = 365 if plan_a_aplicar == 'anual' else 30
        hoy = timezone.localdate()
        base = self.fecha_vencimiento if self.fecha_vencimiento > hoy else hoy
        self.fecha_vencimiento = base + timedelta(days=dias)
        self.plan = plan_a_aplicar
        self.habilitada = True
        self.save()

    def __str__(self):
        return f"{self.codigo_suscripcion} - {self.nombre_completo} ({self.dias_restantes} días)"


class ReportePagoTarjeta(models.Model):
    ESTADOS_PAGO = [
        ('pendiente', 'Pendiente por Validar'),
        ('aprobado', 'Aprobado y Renovado'),
        ('rechazado', 'Rechazado'),
    ]

    tarjeta = models.ForeignKey(TarjetaDigital, on_delete=models.CASCADE, related_name="pagos")
    plan_solicitado = models.CharField(max_length=20, choices=TarjetaDigital.PLANES, default='mensual')
    metodo_pago = models.CharField(max_length=100, help_text="Ej. Pago Móvil, Zelle, Transferencia, Binance")
    referencia = models.CharField(max_length=100)
    monto = models.CharField(max_length=50)
    comprobante = models.FileField(upload_to='comprobantes/', blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='pendiente')
    fecha_reporte = models.DateTimeField(auto_now_add=True)

class Meta:
    ordering = ['-fecha_reporte']

def __str__(self):
        return f"Pago {self.tarjeta.codigo_suscripcion} - Ref: {self.referencia} ({self.estado})"

def generar_codigo_banner():
        return f"PUB-{uuid.uuid4().hex[:6].upper()}"


class PublicidadBanner(models.Model):
    UBICACIONES = [
        ('destacado', 'Banner Destacado (Ancho Completo)'),
        ('estandar', 'Tarjeta Aliado (Cuadrícula B2B)'),
    ]

    PLANES = [
        ('mensual', 'Plan Mensual (30 días)'),
        ('trimestral', 'Plan Trimestral (90 días)'),
        ('anual', 'Plan Anual (365 días)'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="publicidad")
    codigo_anuncio = models.CharField(max_length=15, unique=True, default=generar_codigo_banner)
    habilitada = models.BooleanField(default=False, help_text="Permiso otorgado por el administrador")
    ubicacion = models.CharField(max_length=20, choices=UBICACIONES, default='estandar')
    plan = models.CharField(max_length=20, choices=PLANES, default='mensual')
    fecha_vencimiento = models.DateField(default=timezone.now)

    # Campos editables por el cliente (Sin código)
    imagen = models.FileField(upload_to='publicidad/', blank=True, null=True)
    titulo = models.CharField(max_length=120, default="Nombre de la Empresa Aliada")
    texto = models.CharField(max_length=260, default="Descripción breve del servicio o promoción corporativa.")
    texto_boton = models.CharField(max_length=40, default="Conocer más →")
    enlace_destino = models.URLField(blank=True, default="https://")

    # Modo exclusivo Administrador
    usar_html_personalizado = models.BooleanField(default=False)
    codigo_html_personalizado = models.TextField(blank=True, default="")
    actualizada = models.DateTimeField(auto_now=True)

    @property
    def dias_restantes(self):
        return (self.fecha_vencimiento - timezone.localdate()).days

    @property
    def esta_activa(self):
        return self.habilitada and self.dias_restantes >= 0

    def renovar_plan(self, tipo_plan=None):
        plan_a_aplicar = tipo_plan or self.plan
        dias = 365 if plan_a_aplicar == 'anual' else (90 if plan_a_aplicar == 'trimestral' else 30)
        hoy = timezone.localdate()
        base = self.fecha_vencimiento if self.fecha_vencimiento > hoy else hoy
        self.fecha_vencimiento = base + timedelta(days=dias)
        self.plan = plan_a_aplicar
        self.habilitada = True
        self.save()

    def __str__(self):
        return f"{self.codigo_anuncio} - {self.titulo} ({self.dias_restantes} días)"


class ReportePagoPublicidad(models.Model):
    ESTADOS_PAGO = [
        ('pendiente', 'Pendiente por Validar'),
        ('aprobado', 'Aprobado y Renovado'),
        ('rechazado', 'Rechazado'),
    ]

    publicidad = models.ForeignKey(PublicidadBanner, on_delete=models.CASCADE, related_name="pagos")
    plan_solicitado = models.CharField(max_length=20, choices=PublicidadBanner.PLANES, default='mensual')
    metodo_pago = models.CharField(max_length=100)
    referencia = models.CharField(max_length=100)
    monto = models.CharField(max_length=50)
    comprobante = models.FileField(upload_to='comprobantes_pub/', blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='pendiente')
    fecha_reporte = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_reporte']

class AppDemoRender(models.Model):
    nombre = models.CharField(max_length=120, help_text="Ej: AuditTech - Sistema de Auditoría")
    url = models.URLField(help_text="Ej: https://audittech.onrender.com/cuentas/login/")
    descripcion = models.CharField(max_length=250, blank=True, default="")
    credenciales_demo = models.CharField(
        max_length=150,
        blank=True,
        default="",
        help_text="Opcional: Usuario/clave de prueba para tus demos en vivo"
    )
    categoria = models.CharField(max_length=80, default="SaaS / Web App")
    orden = models.PositiveIntegerField(default=1)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', '-creado']

    def __str__(self):
        return f"{self.nombre} ({self.url})"