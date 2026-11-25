from django.db import models

class Proyecto(models.Model):
    ESTADOS = [
        ('En progreso', 'En progreso'),
        ('Completado', 'Completado'),
        ('En auditoría', 'En auditoría'),
    ]
    titulo = models.CharField(max_length=200)
    cliente = models.CharField(max_length=150, help_text="Ej. Sector Salud / Empresa Privada")
    descripcion = models.TextField()
    estado = models.CharField(max_length=30, choices=ESTADOS, default='En progreso')
    progreso = models.PositiveIntegerField(default=50, help_text="Porcentaje de 0 a 100")
    tecnologias = models.CharField(max_length=200, help_text="Separadas por coma: Django, Firewall, WordPress")
    visible_en_web = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return f"{self.titulo} ({self.progreso}%)"