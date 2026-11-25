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
    visible_en_web = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=1)
    creado = models.DateTimeField(auto_now_add=True)

class EvaluacionFactibilidad(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name="evaluaciones")
    nombre_proyecto_propuesto = models.CharField(max_length=160)
    notas_consultor = models.TextField(blank=True, default="")

    # 1. TECNOLOGÍA E INFRAESTRUCTURA
    tec_red_estructurada = models.BooleanField(default=False)
    tec_dominio_correos = models.BooleanField(default=False)
    tec_seguridad_perimetral = models.BooleanField(default=False)
    tec_seguridad_logica = models.BooleanField(default=False)
    tec_servidores = models.BooleanField(default=False)
    tec_camaras_cctv = models.BooleanField(default=False)

    # 2. MARKETING Y PRESENCIA DIGITAL
    mkt_sitio_web = models.BooleanField(default=False)
    mkt_redes_identidad = models.BooleanField(default=False)
    mkt_crm_automatizacion = models.BooleanField(default=False)
    mkt_analitica_metricas = models.BooleanField(default=False)

    # 3. EVALUACIÓN ORGANIZACIONAL
    org_roles_organigrama = models.BooleanField(default=False)
    org_manuales_procesos = models.BooleanField(default=False)
    org_continuidad_riesgos = models.BooleanField(default=False)
    org_kpis_gestion = models.BooleanField(default=False)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-actualizado"]

    @property
    def puntaje_tecnologia(self):
        items = [
            self.tec_red_estructurada,
            self.tec_dominio_correos,
            self.tec_seguridad_perimetral,
            self.tec_seguridad_logica,
            self.tec_servidores,
            self.tec_camaras_cctv,
        ]
        return round((sum(items) / len(items)) * 100)

    @property
    def puntaje_marketing(self):
        items = [
            self.mkt_sitio_web,
            self.mkt_redes_identidad,
            self.mkt_crm_automatizacion,
            self.mkt_analitica_metricas,
        ]
        return round((sum(items) / len(items)) * 100)

    @property
    def puntaje_organizacional(self):
        items = [
            self.org_roles_organigrama,
            self.org_manuales_procesos,
            self.org_continuidad_riesgos,
            self.org_kpis_gestion,
        ]
        return round((sum(items) / len(items)) * 100)

    @property
    def madurez_global(self):
        return round(
            (self.puntaje_tecnologia * 0.45)
            + (self.puntaje_marketing * 0.25)
            + (self.puntaje_organizacional * 0.30)
        )

    @property
    def diagnostico_ia(self):
        """Genera análisis de factibilidad, brechas y proyección en 3 fases."""
        brechas_fase1 = []
        brechas_fase2 = []
        brechas_fase3 = []

        # Fase 1: Blindaje e Infraestructura Crítica
        if not self.tec_red_estructurada:
            brechas_fase1.append("Diseño y certificación de red estructurada empresarial.")
        if not self.tec_seguridad_perimetral:
            brechas_fase1.append("Implementación de Firewall perimetral y segmentación de red.")
        if not self.tec_seguridad_logica:
            brechas_fase1.append("Despliegue de seguridad lógica (EDR, 2FA y backups automatizados).")
        if not self.tec_servidores:
            brechas_fase1.append("Centralización en servidor local o arquitectura Cloud híbrida.")
        if not self.tec_camaras_cctv:
            brechas_fase1.append("Instalación de sistema de videovigilancia IP con respaldo remoto.")
        if not self.tec_dominio_correos:
            brechas_fase1.append("Registro de dominio corporativo y migración de correos profesionales.")

        # Fase 2: Orden Organizacional
        if not self.org_roles_organigrama:
            brechas_fase2.append("Definición de organigrama funcional y matriz de responsabilidades.")
        if not self.org_manuales_procesos:
            brechas_fase2.append("Levantamiento y documentación de procesos operativos clave.")
        if not self.org_continuidad_riesgos:
            brechas_fase2.append("Plan de continuidad operativa y recuperación ante desastres (DRP).")
        if not self.org_kpis_gestion:
            brechas_fase2.append("Tablero de indicadores (KPIs) para control ejecutivo.")

        # Fase 3: Aceleración Comercial y Marketing
        if not self.mkt_sitio_web:
            brechas_fase3.append("Desarrollo de plataforma web corporativa orientada a conversión.")
        if not self.mkt_redes_identidad:
            brechas_fase3.append("Estandarización de identidad digital y canales oficiales.")
        if not self.mkt_crm_automatizacion:
            brechas_fase3.append("Implementación de embudo CRM, WhatsApp automatizado y Tarjetas Digitales.")
        if not self.mkt_analitica_metricas:
            brechas_fase3.append("Configuración de analítica web y seguimiento de retorno de inversión.")

        global_score = self.madurez_global
        if global_score < 35:
            factibilidad = "ALTA PRIORIDAD · Transformación Integral"
            resumen = "El cliente opera con alta vulnerabilidad técnica y baja estandarización. Se recomienda iniciar con blindaje de infraestructura antes de escalar ventas."
            proyeccion = min(85, global_score + 50)
        elif global_score < 70:
            factibilidad = "FACTIBILIDAD ÓPTIMA · Modernización y Blindaje"
            resumen = "Cuenta con base operativa funcional, pero presenta brechas de seguridad y procesos que frenan su crecimiento. Excelente candidato para proyecto por fases."
            proyeccion = min(92, global_score + 30)
        else:
            factibilidad = "ALTA MADUREZ · Optimización y Automatización Avanzada"
            resumen = "Infraestructura sólida. El proyecto debe enfocarse en automatización de procesos, analítica avanzada y mejora continua."
            proyeccion = min(98, global_score + 15)

        return {
            "factibilidad": factibilidad,
            "resumen": resumen,
            "proyeccion_objetivo": proyeccion,
            "fase1": brechas_fase1,
            "fase2": brechas_fase2,
            "fase3": brechas_fase3,
        }

    def __str__(self):
        return f"Evaluación {self.cliente.username} - {self.nombre_proyecto_propuesto} ({self.madurez_global}%)"