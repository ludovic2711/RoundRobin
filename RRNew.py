from operator import attrgetter
from queue import Queue
from tkinter import *
from tkinter import messagebox as MessageBox

import Proceso_Entradas_Salidas as Proceso

def ordenar_cola(qp):
    list_cola = list(qp.queue)
    lista_ordenada = sorted(list_cola, key=attrgetter('tiempo_llegada_ms'))
    qp_ordenada = Queue(cantidad_procesos)
    for proceso in lista_ordenada:
        qp_ordenada.put(proceso)
    return qp_ordenada

def validar_input(validar):
    try:
        int(validar)
        return True
    except ValueError:
        return False

def inicializar_archivos():
    with open('tiempos.txt', 'w') as archivo:
        archivo.write("||Tiempos de vuelta y espera||")
    with open('solucion.txt', 'w') as archivo:
        archivo.write("||Grantt||\n")
    with open('listos.txt', 'w') as archivo:
        archivo.write("||Registro de listos||")

def escribir_tiempo_vuelta_espera(proceso):
    with open('tiempos.txt', 'a') as archivo:
        archivo.write("\nTIEMPOS DE VUELTA Y DE ESPERA PARA  P:" + str(proceso.id_proceso) + "\n")
        tiempo_espera = proceso.tiempo_ingreso_programa - proceso.tiempo_llegada_original
        tiempo_vuelta = proceso.tiempo_terminado - proceso.suma_entradas_salida - proceso.tiempo_llegada_original
        archivo.write("tiempo de vuelta = " + str(tiempo_vuelta))
        archivo.write(" tiempo de espera = " + str(tiempo_espera))
        return tiempo_vuelta, tiempo_espera

def escribir_grantt(tiempo_anterior, proceso, tiempo_actual, intercambio, qp_ordenada, qp_round_robin, quantum):
    with open('solucion.txt', 'a') as archivo:
        archivo.write("|")
        archivo.write("P" + str(proceso.id_proceso) + "_" + str(1) + "|" )
        archivo.write("_" + str(tiempo_actual - intercambio) + "_ |")
        if not (qp_ordenada.empty() and qp_round_robin.empty()):
            archivo.write(" Intercambio " + str(round((intercambio / quantum), 2)))
        archivo.write('---'+ str(tiempo_actual) + '\n')

def round_robin(qp, cantidad_procesos, quantum=50, intercambio=10):
    list_procesos_terminados = []
    tiempo_anterior = 0
    tiempo_actual = 0
    tiempo_vuelta = 0
    promedio_vuelta = 0
    promedio_espera = 0

    qp_ordenada = ordenar_cola(qp)
    print(qp_ordenada.empty())
    qp_round_robin = Queue(cantidad_procesos)

    inicializar_archivos()
    
    while not qp_round_robin.empty() or tiempo_actual == 0:
        if tiempo_actual == 0:
            qp_round_robin.put(qp_ordenada.get())

        proceso = qp_round_robin.get()

        if not proceso.asignado_tiempo_ingreso_programa:
            proceso.tiempo_ingreso_programa = tiempo_actual
            proceso.asignado_tiempo_ingreso_programa = True
        with open('listos.txt', 'a') as archivo:
            archivo.write("\nProceso # " + str(proceso.id_proceso) + " Q Requiere: " + str(proceso.tiempo_procesador))
        
        tiempo_anterior = tiempo_actual
        tiempo_actual = tiempo_actual + (1 * quantum + intercambio)
        proceso.tiempo_procesador = proceso.tiempo_procesador - 1

        len_qp_ordenada = qp_ordenada.qsize()
        i = 0
        while not qp_ordenada.empty() and i <= len_qp_ordenada:
            p_evaluar = qp_ordenada.get()
            if tiempo_actual >= p_evaluar.tiempo_llegada_ms:
                qp_round_robin.put(p_evaluar)
            else:
                qp_ordenada.put(p_evaluar)
                qp_ordenada = ordenar_cola(qp_ordenada)
                i = i + 1      

        if proceso.tiempo_procesador != 0:
            qp_round_robin.put(proceso)

        if proceso.tiempo_procesador == 0:             
            proceso.tiempo_terminado = tiempo_actual - intercambio 
            if proceso.suma_entradas_salida == 0:
                len_cola_es = proceso.cola_entradas_salidas.qsize()
                j = 0
                while j < len_cola_es:
                    proceso_a_revisar_es_quantum = proceso.cola_entradas_salidas.get()
                    proceso.suma_entradas_salida = proceso.suma_entradas_salida + proceso_a_revisar_es_quantum.tiempo_procesador * quantum
                    proceso.cola_entradas_salidas.put(proceso_a_revisar_es_quantum)
                    proceso.cola_entradas_salidas = ordenar_cola(proceso.cola_entradas_salidas)
                    j = j + 1
            list_procesos_terminados.append(proceso)
            if not proceso.cola_entradas_salidas.empty():
                entrada_salida = proceso.cola_entradas_salidas.get()
                tiempo_despertar = tiempo_actual + entrada_salida.tiempo_dormida * quantum
                proceso.tiempo_llegada_ms = tiempo_despertar
                proceso.tiempo_procesador = entrada_salida.tiempo_procesador
                qp_ordenada.put(proceso)
                qp_ordenada = ordenar_cola(qp_ordenada)
            else:
                tiempo_vuelta, tiempo_espera = escribir_tiempo_vuelta_espera(proceso)
                promedio_vuelta = promedio_vuelta + tiempo_vuelta
                promedio_espera = promedio_espera + tiempo_espera

        if qp_ordenada.empty() and qp_round_robin.empty():
            tiempo_actual = tiempo_actual - intercambio
            intercambio = 0
            with open('tiempos.txt', 'a') as archivo:
                archivo.write("Promedios\n")
                archivo.write("El tiempo promedio de vuelta es: " + str(promedio_vuelta / cantidad_procesos))
                archivo.write("El tiempo promedio de espera es: " + str(promedio_espera / cantidad_procesos))

        escribir_grantt(tiempo_anterior, proceso, tiempo_actual, intercambio, qp_ordenada, qp_round_robin, quantum)
    MessageBox.showinfo("Mensaje", "Visualizar los archivos creados") # título, mensaje


cantidad_procesos = 0
while cantidad_procesos <= 0:
    print("¿Cuantos procesos se tiene? : ")
    validar = input()
    if validar_input(validar):
        cantidad_procesos = int(validar)

qp = Queue(cantidad_procesos)
for i in range(cantidad_procesos):
    tiempo_llegada_ms = -1
    while tiempo_llegada_ms <= -1:
        print("En qué tiempo llega el proceso {} en MILISEGUNDOS ".format(i))
        validar = input()
        if validar_input(validar):
            tiempo_llegada_ms = int(validar)
    tiempo_q = -1
    while tiempo_q <= 0:
        print("¿Cuantos Quantums requiere en procesador? ")
        validar = input()
        if validar_input(validar):
            tiempo_q = int(validar)
    entrada_salida_cant = -1
    while entrada_salida_cant <= -1:
        print("¿Cuantas E/S tiene el proceso {} ? ".format(i))
        validar = input()
        if validar_input(validar):
            entrada_salida_cant = int(validar)

    cola_entradas_salidas = Queue()        
    for j in range(entrada_salida_cant):
        entrada_salida = Proceso.EntradasSalidas()
        if entrada_salida_cant > 0:
            dormida_por_proceso = 0
            while dormida_por_proceso <= 0:
                print("Para la E/S  ", j, " ¿Cuanto tiempo se va a dormir el Proceso ", i," en Quantum ?")
                validar = input()
                if validar_input(validar):
                    dormida_por_proceso = int(validar)

            quantum_entrada_salida = 0
            while quantum_entrada_salida <= 0:
                print("¿Cuantos Quantum require la E/S ", j, " ? ")
                validar = input()
                if validar_input(validar):
                    quantum_entrada_salida = int(validar)
                        
            entrada_salida.id_entrada_salida = j                          
            entrada_salida.tiempo_dormida = dormida_por_proceso
            entrada_salida.tiempo_procesador = quantum_entrada_salida

            cola_entradas_salidas.put(entrada_salida)
            
    proceso = Proceso.Proceso(i, tiempo_llegada_ms, tiempo_q, cola_entradas_salidas)
    qp.put(proceso)

round_robin(qp, cantidad_procesos)
