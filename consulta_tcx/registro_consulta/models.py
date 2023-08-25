from django.db import models
from django.utils import timezone
import datetime

# Create your models here.

class Consulta(models.Model):
    nombre = models.CharField(max_length=50)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50)
    edad = models.IntegerField(default=0)
    semanas = models.IntegerField(default=0)
    motivo = models.CharField(max_length=60)
    triage = models.IntegerField(default=0)
    fecha = models.DateTimeField()
    

    def __str__(self):
        mihora = datetime.datetime.now()
        actual = mihora.strftime('%Y-%m-%d %H:%M:%S')
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno} {self.edad} {self.semanas} {self.motivo} {self.triage} {actual}"