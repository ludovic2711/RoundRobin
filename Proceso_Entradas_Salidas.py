class EntradasSalidas: 
    def __init__(self):
        self.id_entrada_salida = 0
        self.tiempo_llegada_ms = 0
        self.tiempo_procesador = 0
        self.tiempo_dormida = 0

class Proceso:

    def __init__(self, id_proceso, tiempo_llegada_ms, tiempo_procesador, cola_entradas_salidas):
        self.id_proceso = id_proceso
        self.tiempo_llegada_ms = tiempo_llegada_ms
        self.tiempo_procesador = tiempo_procesador
        self.cola_entradas_salidas = cola_entradas_salidas
        
        self.tiempo_llegada_original = tiempo_llegada_ms
        self.tiempo_ingreso_programa = 0
        self.asignado_tiempo_ingreso_programa = False
        self.tiempo_terminado =0
        self.suma_entradas_salida =0