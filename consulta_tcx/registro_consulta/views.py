from django.shortcuts import render
from django.http import HttpResponse
from .models import Consulta
from django.db.models import Count
from django.views import generic
import datetime
import io
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='whitegrid')
import urllib, base64
from django.db.models.functions import ExtractMonth
import calendar


def index(request):
    lista_pac = Consulta.objects.all()
    return render(request, "registro_consulta/index.html", {"lista_pac": Consulta.objects.order_by('-id')[:20]})

# Agregar datos de paciente y mostrar los ultimos registros de manera descendente

def agrega_pac(request):
    mihora = datetime.datetime.now()
    actual = mihora.strftime('%Y-%m-%d %H:%M:%S')
    nombre1 = request.POST.get("name")
    apellido1 = request.POST.get("last_name1")
    apellido2 = request.POST.get("last_name2")
    edad1 = request.POST.get("age")
    semanas1 = request.POST.get("sdg")
    motivo1 = request.POST.get("mot")
    triage = request.POST.get("triage")
    paciente = Consulta(nombre = nombre1, apellido_paterno = apellido1, apellido_materno = apellido2, edad = edad1, semanas = semanas1, motivo = motivo1, triage = triage, fecha = actual)
    paciente.save()
    return render(request, "registro_consulta/index.html", {"lista_pac": Consulta.objects.order_by('-id')[:20]})

# Buscar paciente por nombre y apellido y mostrar el resultado

def busca_pac(request):
    lista_pac = Consulta.objects.all()
    nombre1 = request.POST.get("name")
    apellido1 = request.POST.get("last_name1")
    paciente_b = Consulta.objects.filter(nombre = nombre1, apellido_paterno = apellido1)
    return render(request, "registro_consulta/buscar.html", {"lista_pac": Consulta.objects.order_by('-id').filter(nombre=nombre1, apellido_paterno=apellido1)})

# Prueba para graficar

def chart(request):
    '''paciente_edad = Consulta.objects.values('edad').annotate(cantidad=Count('edad'))
    edades = [item['edad']for item in paciente_edad]
    cantidades = [item['cantidad']for item in paciente_edad]
    
    plt.figure(figsize=(8, 6))
    sns.barplot(x = edades, y = cantidades)'''

    paciente_fecha = Consulta.objects.annotate(month=ExtractMonth('fecha')).values('month').annotate(total = Count('id'))
    fechas = [(item['month'])for item in paciente_fecha]
    totales = [item['total']for item in paciente_fecha]

    plt.figure(figsize=(8, 6))
    sns.barplot(x = fechas, y = totales)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read()).decode('utf-8')

    return render(request, "registro_consulta/statistics.html", {'string':string})

# Funciones de la pagina estadísticas que incluye un resumen de datos y las gráficas

def chart2(request):
    
    # Contar el el total de pacientes

    pacientes_total = Consulta.objects.count()
    
    # Contar la cantidad de pacientes por edad y regresar el top 3

    paciente_edad = Consulta.objects.values('edad').annotate(cantidad=Count('edad'))
    paciente_edad_top = Consulta.objects.values('edad').annotate(cantidad=Count('edad')).order_by('-cantidad')[:3]
    edades = [item['edad']for item in paciente_edad]
    cantidades = [item['cantidad']for item in paciente_edad]

    # Gráfica de pacientes por edad
    
    plt.figure(figsize=(7, 4))
    sns.set_palette("magma")
    sns.barplot(x = edades, y = cantidades, palette = ['purple'])
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.title("Consultas por edad")

    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, bbox_inches='tight')
    buf.seek(0)
    string = base64.b64encode(buf.read()).decode('utf-8')

    # Se obtienen los meses y la cantidad de consultas

    paciente_fecha = Consulta.objects.annotate(month=ExtractMonth('fecha')).values('month').annotate(total = Count('id'))

    # Se ordenan la cantidad de consultas por mes de manera descendente

    paciente_fecha_top = Consulta.objects.annotate(month=ExtractMonth('fecha')).values('month').annotate(total = Count('id')).order_by('-total')[:1]
    fechas = [(item['month'])for item in paciente_fecha]
    totales = [item['total']for item in paciente_fecha]

    meses = ["mayo", "junio", "julio"]

    # Gráfica de consultas por mes

    plt.figure(figsize=(5, 4))
    sns.set_palette("magma")
    sns.barplot(x = meses, y = totales)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.title("Consultas por fecha")
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, bbox_inches='tight')
    buf.seek(0)
    string2 = base64.b64encode(buf.read()).decode('utf-8')

    # Cantidad de consultas por color de triage

    paciente_triage = Consulta.objects.values('triage').annotate(total_triage = Count('triage'))

    # Se obtiene el color de triage que tenga más consultas
    paciente_triage_top = Consulta.objects.values('triage').annotate(total_triage = Count('triage')).order_by('-total_triage')[:1]
    colores = ['#60d394', '#ffd97d', '#ee6055']

    consulta_triage = []

    # Se obtiene el valor de la cantidad de conosultas para cada color de triage

    for triages in paciente_triage:
        total_triages = triages['total_triage']
        consulta_triage.append(total_triages)
    
    # Gráfica de triage mostrando su respectivo color y porcentage de consulta resprecto al total

    triage_labels = ['Urgencia menor', 'Urgencia', 'Urgencia vital']
    plt.figure(figsize=(4, 4))
    plt.pie(consulta_triage, colors=colores, labels=triage_labels, autopct="%.1f%%")
    plt.title('Consultas por Triage')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, bbox_inches='tight')
    buf.seek(0)
    string3 = base64.b64encode(buf.read()).decode('utf-8')

    # Se obtienen las consultas por trimestre de embarazo

    pacientes_primer_trimestre = Consulta.objects.filter(semanas__gte=6, semanas__lte=12).count()
    pacientes_segundo_trimestre = Consulta.objects.filter(semanas__gte=13, semanas__lte=24).count()
    pacientes_tercer_trimestre = Consulta.objects.filter(semanas__gte=25, semanas__lte=42).count()

    total_trimestres = [pacientes_primer_trimestre, pacientes_segundo_trimestre, pacientes_tercer_trimestre]
    total_trimestres_top = [pacientes_primer_trimestre, pacientes_segundo_trimestre, pacientes_tercer_trimestre]
    
    # Se obtiene el trimestre que tenga la mayor cantidad de consultas
    
    trim_total = {"1er trimestre": pacientes_primer_trimestre, "2do trimestre": pacientes_segundo_trimestre, "3er trimestre": pacientes_tercer_trimestre}
    trim_2 = dict(sorted(trim_total.items(), key=lambda item: item[1], reverse = True))
    trim_key = trim_2.keys()
    trim_key = list(trim_key)
    
    # Prueba para obtener el trimeste con mayor consulta, pero se obtiene solo el numero

    trim = sorted(total_trimestres_top, reverse=True)

    # Gráfica de la cantidad de consultas por trimestre de embarazo

    labels_trimestre = ["1er trimestre", "2do trimestre", "3er trimestre"]
    plt.figure(figsize=(5, 4))
    sns.barplot(x = labels_trimestre, y = total_trimestres)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.title("Consultas por trimestre")

    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, bbox_inches='tight')
    buf.seek(0)
    string4 = base64.b64encode(buf.read()).decode('utf-8')

    # Prueba de obtener el prmoedio de consultas por mes

    promedios = []

    paciente_meses_nombre = []

    for paciente_meses2 in paciente_fecha_top:
        numero_mes = paciente_meses2['month']
        nombre_mes = calendar.month_name[numero_mes]
        paciente_meses2['month'] = nombre_mes
        paciente_meses_nombre.append(paciente_meses2)

    for paciente_meses_nombre in paciente_fecha_top:
        total_meses = paciente_meses_nombre['total']
        promedio = round(total_meses/30, 2)
        promedios.append({'month': paciente_meses_nombre['month'], 'promedio': promedio})
    
    # Cantidad de consultas por motivo y obtener el motivo por el cual la mayoria de pacientes fue a consulta
    
    paciente_motivo = Consulta.objects.values('motivo').annotate(cantidad=Count('motivo')).order_by('-cantidad')[:1]

    return render(request, "registro_consulta/statistics.html", {'string':string, 'string2':string2,
                                                                   "pacientes_total":pacientes_total, "paciente_fecha":paciente_fecha,
                                                                   "promedios":promedios, "string3":string3,
                                                                   "pacientes_primer_trimestre":pacientes_primer_trimestre,
                                                                   "pacientes_segundo_trimestre":pacientes_segundo_trimestre,
                                                                   "pacientes_tercer_trimestre":pacientes_tercer_trimestre,
                                                                   "string4":string4, "paciente_edad_top": paciente_edad_top,
                                                                   "pacientes_fecha_top": paciente_fecha_top, "paciente_motivo": paciente_motivo, 
                                                                   "paciente_triage_top": paciente_triage_top, "trim": trim, "trim_2": trim_2,
                                                                   "trim_key": trim_key})