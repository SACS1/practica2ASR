from consultas import consultaSNMP
from crearBD import crearRRD
from crearBD import vistaXML
from datosBD import fetchBD
from datosBD import lastUpdate
from time import gmtime, strftime
from datetime import datetime
import rrdtool
import threading
import time

def pedirNumeroEntero():

    correcto = False
    num = 0
    while(not correcto):
        try:
            num = int(input("Introduzca un numero entero: "))
            correcto = True
        except ValueError:
            print("Error, introduzca un numero entero")

    return num

#Función que actualiza la base de datos
def updateRRD(comunidad, ipHstName):
    while 1:
        t = int(time.time())
        global tiempo_actual
        if t == tiempo_actual + 300:#Si ya han transcurrido 5 minutos desde el último corte automático, realiza un nuevo corte
            tiempo_actual = t
            reporte(300)
        total_tcpInSegs = int(
            consultaSNMP(comunidad, ipHstName,
                         '1.3.6.1.2.1.6.10.0'))
        total_tcpOutSegs = int(
            consultaSNMP(comunidad, ipHstName,
                         '1.3.6.1.2.1.6.11.0'))

        valor = "N:" + str(total_tcpInSegs) + ':' + str(total_tcpOutSegs)
        try:
            rrdtool.update('monitorSSH.rrd', valor)
        except:
            time.sleep(1)
        time.sleep(1)
        global stop_t
        if(stop_t):#Detiene el hilo
            break

def iniciarMonitoreo(comunidad, ipHstName):
    global stop_t
    stop_t = False
    t = threading.Thread(target = updateRRD, args = [comunidad, ipHstName])#Actualiza la base de datos en segundo plano
    t.start()
    
def obtenerTotalInPack(t):
    resultadoF = fetchBD(t) #corte de 5 minutos
    cont = 0
    for x in range(len(resultadoF[2])):
        if resultadoF[2][x][0] is not None:
            cont += resultadoF[2][x][0]#Acumula las diferencias almacenadas en la base de datos
    lastDS = lastUpdate()["ds"]["tcpInSegs"]#Recupera la última actualización de la base
    stats = [lastDS, cont, lastDS - cont]
    return stats

def obtenerTotalOutPack(t):
    resultadoF = fetchBD(t) #corte de 5 minutos
    cont = 0
    for x in range(len(resultadoF[2])):
        if resultadoF[2][x][1] is not None:
            cont += resultadoF[2][x][1]
    lastDS = lastUpdate()["ds"]["tcpOutSegs"]
    stats = [lastDS, cont, lastDS - cont]
    return stats

def reporte(t):
    
    global version
    global encabezado
    global versionReporte
    versionReporte = "version: " + str(version) + "\n"
    
    
    version += 1
    now = datetime.now()
    rdate = "\nrdate: " + now.strftime("%d %b %Y %H:%M:%S") + "\n"
    cuerpo = "#NAS-IP-Address\n4: 192.168.3.22\n"
    cuerpo += "#NAS-Port\n5: 22\n"
    statsIn = obtenerTotalInPack(t)
    statsOut = obtenerTotalOutPack(t)
    cuerpo += "#Initial-State-Input-Packets\n" + str(statsIn[2]) +"\n"
    cuerpo += "#Acct-Input-Packets\n47: " + str(statsIn[1]) +"\n"
    cuerpo += "#Final-State-Input-Packets\n" + str(statsIn[0]) +"\n"
    cuerpo += "#Initial-State-Output-Packets\n" + str(statsOut[2]) +"\n"
    cuerpo += "#Acct-Output-Packets\n47: " + str(statsOut[1]) +"\n"
    cuerpo += "#Final-State-Output-Packets\n" + str(statsOut[0])
    
    f = open("reporte_SSH.txt", 'w')
    f.write(versionReporte + encabezado + rdate + cuerpo)
    f.close()




salir = False
opcion = 0
stop_t = False
comunidad = "comunidadASR"
ipHstName = "192.168.3.22"
now = datetime.now()
dt_string = now.strftime("%d %b %Y %H:%M:%S")
tiempo_actual = int(time.time())
crearRRD()
version = 1
versionReporte = "version: " + str(version) + "\n"
encabezado = "device: " + str(consultaSNMP(comunidad, ipHstName, "1.3.6.1.2.1.1.5.0")) + "\ndate: " + dt_string + "\ndefaultProtocol: radius\n"

while not salir:

    iniciarMonitoreo(comunidad, ipHstName)
    print(versionReporte + encabezado + "\n")
    print("Ha iniciado el monitoreo del servidor SSH. Corte cada 5 min.\n")

    print ("Elige una opcion\n")

    print("1. Reporte")
    print("2. Vista xml")
    print("3. Salir\n")

    opcion = pedirNumeroEntero()

    if opcion == 1:
        t = int(time.time())
        reporte(t - tiempo_actual)
    elif opcion == 2:
        vistaXML()
    elif opcion == 3:
        stop_t = True
        salir = True
    else:
        print ("Introduce un numero entre 1 y 4")

print ("Fin")
