from gpiozero              import AngularServo,DistanceSensor
from gpiozero.pins.pigpio  import PiGPIOFactory
from gpiozero.exc          import DistanceSensorNoEcho
from contextlib            import contextmanager
from time                  import sleep
import asyncio
import statistics
import warnings
import atexit

import logging


class USRotatingSensor:
    def __init__(self):
        # Inicialización de atributos de la clase
        self.DEBUG                  = True
        self.PIN_ECHO_US            = 27
        self.PIN_TRIGGER_US         = 17
        self.PIN_SERVO_GPIO         = 18

        self.MAX_DISTANCE_M         = 3
        self.MAX_ERRORS_POR_LECTURA = 10

        self.ANGULO_INICIO          = 0
        self.ANGULO_FIN             = 180
        self.PASO_ANGULO            = 20

        self.servo_ult_pos          = 0

        # Registrar cleanup en atexit como red de seguridad para liberar recursos
        atexit.register(self.cleanup)

        # Configuramos fichero de log, nivel y formato
        logging.basicConfig(
            filename='LibRoombaExtension.log', 
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Para configurar el acceso al GPIO de la Raspberry, mejora la precisión en los cálculos de temporización
        # Necesita que esté en funcionamiento el demonio pigpiod
        self.factory = PiGPIOFactory()
        self.sensor  = None
        self.servo   = None
        self.logea('Instancia USRotatingSensor creada.')

    def cleanup(self):
        """
        Limpieza EXPLÍCITA y SEGURA de todos los recursos hardware.
        Debe llamarse antes de que el programa termine.
        """
        self.logea("=" * 60)
        self.logea("USRotatingSensor: INICIANDO LIMPIEZA DE RECURSOS...")
        self.logea("=" * 60)
        
        # Orden inverso al de creación + try/except individual por recurso
        # Esto evita que un error en uno impida limpiar los demás
        recursos = [
            ('servo', self.servo),
            ('sensor', self.sensor),
            ('factory', self.factory)
        ]
        
        for nombre, obj in recursos:
            try:
                if obj is not None:
                    obj.close()
                    self.logea(f"USRotatingSensor.cleanup: ✓ {nombre}.close() ejecutado correctamente")
                else:
                    self.logea(f"USRotatingSensor.cleanup: ⚠ {nombre}: ya era None, saltando")
            except Exception as e:
                # Logear pero NO propagar: queremos limpiar todo lo posible
                logea(f"USRotatingSensor.cleanup: ⚠ ERROR cerrando {nombre}: {type(e).__name__}: {e}")
        
        # Resetear estados
        self.sensor = None
        self.servo = None
        self.factory = None
        
        self.logea("=" * 60)
        self.logea("USRotatingSensor.cleanup: LIMPIEZA COMPLETADA EXITOSAMENTE.")
        self.logea("=" * 60)
    
    # =============================================================================
    # PROTOCOLO DE CONTEXT MANAGER (para usar con 'with')
    # =============================================================================
    
    def __enter__(self):
        """Se llama al entrar en el bloque 'with'."""
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Se llama al salir del bloque 'with', incluso si hay excepción."""
        self.cleanup()
        return False  # No suprimir excepciones

    
    def setup(self):
        try:
            # Inicializa el sensor de distancia utilizando la librería GPIO Zero
            self.logea("Configurando sensor: ")
            self.logea(f"Pin ECHO: {self.PIN_ECHO_US}")
            self.logea(f"Pin TRIGGER: {self.PIN_TRIGGER_US}")
            self.logea(f"MAX_DISTANCE (m): {self.MAX_DISTANCE_M}")

            self.sensor = DistanceSensor(echo=self.PIN_ECHO_US, trigger=self.PIN_TRIGGER_US, max_distance=self.MAX_DISTANCE_M, queue_len=1, pin_factory=self.factory)        

            
            # Inicializar el Servo
            # Ajustamos min_pulse y max_pulse para servos estándar de 180 grados
            self.logea("Configurando servo: ")
            self.logea(f"Pin Servo GPIO: {self.PIN_SERVO_GPIO}")
            self.logea(f"Ángulo Inicio: {self.ANGULO_INICIO}")
            self.logea(f"Ángulo Fin: {self.ANGULO_FIN}")
            self.logea(f"Salto ángulo: {self.PASO_ANGULO}")        

            self.servo = AngularServo(self.PIN_SERVO_GPIO, min_angle=0, max_angle=180,
                                    min_pulse_width=0.0005, max_pulse_width=0.0025,
                                    pin_factory=self.factory)
            self.servo.angle   = 0
            self.servo_ult_pos = 0  
        except Exception as e:
            self.logea(f"USRotatingSensor.setup: ✗ ERROR crítico en inicialización: {e}")
            raise RuntimeError(f"USRotatingSensor.setup: Fallo en inicialización de hardware: {e}")            

    # Método para loguear mensajes
    def logea(self, mens):
        if self.DEBUG:
            logging.info(mens) 
            

    async def LecturaUScm(self):
        delay = 0.05
        num_err = 0
        resultado = None

        for intento in range(1, self.MAX_ERRORS_POR_LECTURA + 1):
            with warnings.catch_warnings(record=True) as lista_warnings:
                # Obligamos a que siempre se registre para poder contarlo
                warnings.simplefilter("always")
            
                # Llamada a tu función
                distance = self.sensor.distance
            
                # Revisamos si saltó el warning específico
                hubo_error_eco = any(
                    isinstance(w.message, DistanceSensorNoEcho) 
                    for w in lista_warnings
                    if hasattr(w, 'message')
                )
            
                if not hubo_error_eco:
                    resultado =  round(distance * 100, 1)    

                    self.logea(f"Lectura exitosa en el intento {intento}")
                    break
                else:
                    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                    self.logea(f"Intento {intento} fallido: DistanceSensorNoEcho detectado.")
                    if intento == self.MAX_ERRORS_POR_LECTURA:
                        raise RuntimeError(f"Fallo crítico: El sensor no respondió tras {self.MAX_ERRORS_POR_LECTURA} intentos.")                
                    await asyncio.sleep(delay)
                
        # Continuar con la ejecución normal
        self.logea(f"Resultado final: {resultado}")
        return resultado            

    async def LecturaUScm_Filtrada(self, num_medidas=5, umbral_tolerancia=2.0):
        """
        Guarda una serie de medidas seguidas en una lista, filtra valores espúreos y devuelve el promedio de los restantes.
        
        :param num_medidas: número de tomas de medida del sensor para procesar.
        :param umbral_tolerancia: Cuánto puede alejarse un valor de la mediana para ser aceptado.
        """
    
        #Comprobamos que tenemos un número correcto de medidas 
        if num_medidas<1:
            return -1
    
        #Sacamos lecturas consecutivas del sensor 
        Lecturas = []
        i = 0
        Num_Err = 0
        while i <num_medidas:
            LecturaSensor = self.LecturaUScm()
            Lecturas.append(LecturaSensor)
            await asyncio.sleep(0.03)
            i += 1

        self.logea(f"LecturaUScm_Filtrada: Lecturas directas sensor US:{Lecturas}")

        # Hacemos un filtrado de las lecturas para descartar valores espúreos del sensor 

        # 1. Calculamos la mediana (el valor central, menos afectado por errores extremos)
        mediana = statistics.median(Lecturas)
    
        # 2. Filtramos: solo nos quedamos con valores que no se alejen demasiado de la mediana
        # Usamos una diferencia porcentual o absoluta según necesites.
        valores_validos = [
            x for x in Lecturas 
            if abs(x - mediana) <= umbral_tolerancia
        ]
        self.logea(f"LecturaUScm_Filtrada: Lecturas filtradas:{Lecturas} ")
    
        # 3. Si por algún motivo todos fueran descartados, usamos la mediana como plan B
        if not valores_validos:
            Resultado = round(mediana,1)
            self.logea(f"LecturaUScm_Filtrada: todas las medidas descartadas, devolvemos mediana{Resultado} ")
            return Resultado

        # 4. Devolvemos el promedio de los valores que sobrevivieron al filtro
        Resultado = round(statistics.mean(valores_validos),1)
        self.logea(f"LecturaUScm_Filtrada: resultado lectura sensor US por promedio de medidas:{Resultado} ")
        return Resultado

    async def realizar_barrido(self):
        Lecturas = []
        for angulo in range(self.ANGULO_INICIO, self.ANGULO_FIN + 1, self.PASO_ANGULO):
            # A. MOVER
            self.servo.angle = angulo
        
            # B. ESPERA MECÁNICA (Crucial)
            # Damos tiempo al servo para llegar y detener la vibración.
            # Si el salto es pequeño (5-10 grados), 0.1s o 0.2s es suficiente.
            await asyncio.sleep(0.2) 
        
            # C. MEDIR
            # El sensor devuelve metros, multiplicamos por 100 para cm.
            Lecturas.append(self.LecturaUScm_Filtrada())
        
            # D. ESPERA ACÚSTICA (Crucial)
            # Esperamos a que los ecos ultrasónicos se disipen antes del siguiente disparo.
            await asyncio.sleep(0.1)
        #Volvemos a la posición inicial    
        self.servo.angle = 0
        return Lecturas

    def posicion_angulo_0(self):
        self.servo.angle = 0

    async def gira_sensor(self, angulo):
        try:
            #Validar ángulo solicitado 
            if (angulo < 0) or (angulo > 180):
                raise ValueError(format("Ángulo pasado (%d) incorrecto. Debe estar entre 0 y 180 grados."))
            #Cálculo de pausa para el movimiento pedido, 0,003 sg por grado de movimiento
            pausa = abs(angulo - self.servo_ult_pos) * 0.003
            self.servo.angle   = angulo
            self.servo_ult_pos = angulo
            await asyncio.sleep(pausa)
            # self.servo.detach()
            #  await asyncio.sleep(pausa)      
        except asyncio.CancelledError:
            # Limpieza del servo al cancelar
            self.servo.detach()  # o self.servo.mid(), según prefieras
            raise  # Importante: re-lanzar para que asyncio gestione bien la cancelación        

    def run(self, coro):
        """Punto de entrada que gestiona Ctrl-C limpiamente."""
        try:
            asyncio.run(coro)
        except KeyboardInterrupt:
            pass    